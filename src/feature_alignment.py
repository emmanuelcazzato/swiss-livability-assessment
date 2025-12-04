"""
Feature Alignment Module

Transforms raw features from Swiss Dwellings dataset to match the FIS input universes.
This ensures that all dimensions (noise, daylight, view, location) properly contribute
to the fuzzy inference process.

Key transformations:
- Daylight: klx -> lux (×1000), capped at universe max
- View sky/greenery: sr -> normalized index (data-driven scaling to match MF universe)
- Location POI: log transform + robust min-max scaling to 0-100
- Noise: dBA pass-through with <=0 treated as missing

Reference data statistics (Swiss Dwellings v3.0.0):
- view_sky: median=0.0039 sr, max=3.88 sr (but very skewed toward 0)
- view_greenery: median=0.0089 sr, max=0.059 sr
- daylight: 0-3.91 klx (stored as klx, needs ×1000 for lux)
- location_poi: 3-2662 counts (long-tailed distribution)
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd


# Default path for alignment config JSON
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "feature_alignment.json"


@dataclass(frozen=True)
class FeatureAlignmentConfig:
    """
    Configuration for feature alignment transformations.

    These parameters are fitted on the full dataset and saved to JSON
    to ensure consistency between batch processing and web API.

    Attributes:
        view_sky_ref: Reference value (95th percentile) for view_sky scaling
        view_greenery_ref: Reference value (95th percentile) for view_greenery scaling
        poi_log_p01: 1st percentile of log1p(poi_count) for robust min-max
        poi_log_p99: 99th percentile of log1p(poi_count) for robust min-max
        daylight_lux_cap: Maximum daylight value in lux (matches FIS universe max)
        view_sky_universe_max: Maximum view_sky in FIS universe (steradians)
        view_greenery_universe_max: Maximum view_greenery in FIS universe (steradians)
        location_poi_universe_max: Maximum location_poi in FIS universe
    """
    view_sky_ref: float
    view_greenery_ref: float
    poi_log_p01: float
    poi_log_p99: float
    daylight_lux_cap: float = 1000.0
    view_sky_universe_max: float = 4.0
    view_greenery_universe_max: float = 2.0
    location_poi_universe_max: float = 100.0

    def to_json(self, path: Optional[Path] = None) -> None:
        """Save configuration to JSON file."""
        if path is None:
            path = DEFAULT_CONFIG_PATH
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2))

    @staticmethod
    def from_json(path: Optional[Path] = None) -> "FeatureAlignmentConfig":
        """Load configuration from JSON file."""
        if path is None:
            path = DEFAULT_CONFIG_PATH
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Alignment config not found at {path}. "
                "Run prepare_full_features.py first to generate it."
            )
        obj = json.loads(path.read_text())
        return FeatureAlignmentConfig(**obj)


def fit_alignment_config(
    df_raw: pd.DataFrame,
    view_sky_col: str = "raw_view_sky_sr",
    view_greenery_col: str = "raw_view_greenery_sr",
    poi_count_col: str = "raw_poi_count",
) -> FeatureAlignmentConfig:
    """
    Fit alignment configuration parameters from raw feature data.

    Uses data-driven calibration to determine scaling parameters:
    - View: 95th percentile as reference for "good" view
    - POI: 1st and 99th percentile of log-transformed counts for robust scaling

    Parameters:
        df_raw: DataFrame with raw feature columns
        view_sky_col: Column name for raw view sky values (sr)
        view_greenery_col: Column name for raw view greenery values (sr)
        poi_count_col: Column name for raw POI count

    Returns:
        FeatureAlignmentConfig with fitted parameters
    """
    # View sky reference (95th percentile)
    view_sky_vals = df_raw[view_sky_col].dropna()
    view_sky_ref = float(view_sky_vals.quantile(0.95))
    if view_sky_ref <= 0:
        view_sky_ref = 1e-6  # Avoid division by zero

    # View greenery reference (95th percentile)
    view_greenery_vals = df_raw[view_greenery_col].dropna()
    view_greenery_ref = float(view_greenery_vals.quantile(0.95))
    if view_greenery_ref <= 0:
        view_greenery_ref = 1e-6

    # POI log-transformed percentiles for robust min-max scaling
    poi_vals = df_raw[poi_count_col].clip(lower=0).fillna(0)
    poi_log = np.log1p(poi_vals)
    poi_log_p01 = float(poi_log.quantile(0.01))
    poi_log_p99 = float(poi_log.quantile(0.99))

    # Ensure denominator is positive
    if (poi_log_p99 - poi_log_p01) <= 1e-9:
        poi_log_p99 = poi_log_p01 + 1.0

    return FeatureAlignmentConfig(
        view_sky_ref=view_sky_ref,
        view_greenery_ref=view_greenery_ref,
        poi_log_p01=poi_log_p01,
        poi_log_p99=poi_log_p99,
    )


def align_features(
    df_raw: pd.DataFrame,
    cfg: FeatureAlignmentConfig,
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Transform raw features to aligned features matching FIS input universes.

    Transformations:
    1. Noise: Pass-through, treat <=0 as missing
    2. Daylight: klx -> lux (×1000), capped at universe max
    3. View sky: sr -> normalized index (0 to universe_max)
    4. View greenery: sr -> normalized index (0 to universe_max)
    5. Location POI: log1p + robust min-max scaling -> 0 to universe_max

    Parameters:
        df_raw: DataFrame with raw feature columns (raw_* prefix)
        cfg: FeatureAlignmentConfig with fitted parameters
        inplace: If True, modifies df_raw; otherwise returns a copy

    Returns:
        DataFrame with aligned feature columns added
    """
    out = df_raw if inplace else df_raw.copy()

    # Noise: treat <=0 as missing (these are likely invalid measurements)
    for col in ["raw_noise_day_dba", "raw_noise_night_dba"]:
        if col in out.columns:
            out.loc[out[col] <= 0, col] = np.nan

    # Daylight: klx -> lux, then cap
    if "raw_daylight_klx" in out.columns:
        out["daylight"] = (out["raw_daylight_klx"] * 1000.0).clip(0, cfg.daylight_lux_cap)

    # View sky: sr -> scaled index to match MF universe (0-4)
    # Maps 95th percentile to ~universe_max, allowing some headroom
    if "raw_view_sky_sr" in out.columns:
        out["view_sky"] = (
            out["raw_view_sky_sr"] / cfg.view_sky_ref * cfg.view_sky_universe_max
        ).clip(0, cfg.view_sky_universe_max)

    # View greenery: sr -> scaled index to match MF universe (0-2)
    if "raw_view_greenery_sr" in out.columns:
        out["view_greenery"] = (
            out["raw_view_greenery_sr"] / cfg.view_greenery_ref * cfg.view_greenery_universe_max
        ).clip(0, cfg.view_greenery_universe_max)

    # POI: log1p + robust min-max -> 0-100
    if "raw_poi_count" in out.columns:
        poi_log = np.log1p(out["raw_poi_count"].clip(lower=0))
        denom = cfg.poi_log_p99 - cfg.poi_log_p01
        out["location_poi"] = (
            cfg.location_poi_universe_max * (poi_log - cfg.poi_log_p01) / denom
        ).clip(0, cfg.location_poi_universe_max)

    # Map noise columns to FIS naming convention
    if "raw_noise_day_dba" in out.columns:
        out["noise_lden"] = out["raw_noise_day_dba"]
    if "raw_noise_night_dba" in out.columns:
        out["noise_lnight"] = out["raw_noise_night_dba"]

    return out


def align_single_input(
    noise_lden: float,
    noise_lnight: float,
    daylight_lux: float,
    view_sky_sr: float,
    view_greenery_sr: float,
    poi_count: int,
    cfg: FeatureAlignmentConfig,
) -> dict:
    """
    Align a single dwelling's input features for the FIS.

    This is used by the web API to align user-provided inputs
    before passing them to the fuzzy inference system.

    Parameters:
        noise_lden: Day noise level in dBA
        noise_lnight: Night noise level in dBA
        daylight_lux: Daylight illuminance in lux (user provides lux directly)
        view_sky_sr: Sky view in steradians
        view_greenery_sr: Greenery view in steradians
        poi_count: Number of POIs within 10-min walk
        cfg: FeatureAlignmentConfig with fitted parameters

    Returns:
        Dictionary with aligned feature values ready for FIS
    """
    # Noise: pass-through (but validate)
    aligned_noise_lden = noise_lden if noise_lden > 0 else np.nan
    aligned_noise_lnight = noise_lnight if noise_lnight > 0 else np.nan

    # Daylight: cap at universe max (user already provides lux)
    aligned_daylight = min(max(daylight_lux, 0), cfg.daylight_lux_cap)

    # View sky: scale to universe
    aligned_view_sky = min(
        max(view_sky_sr / cfg.view_sky_ref * cfg.view_sky_universe_max, 0),
        cfg.view_sky_universe_max
    )

    # View greenery: scale to universe
    aligned_view_greenery = min(
        max(view_greenery_sr / cfg.view_greenery_ref * cfg.view_greenery_universe_max, 0),
        cfg.view_greenery_universe_max
    )

    # POI: log + robust min-max
    poi_log = math.log1p(max(poi_count, 0))
    denom = cfg.poi_log_p99 - cfg.poi_log_p01
    aligned_poi = min(
        max(cfg.location_poi_universe_max * (poi_log - cfg.poi_log_p01) / denom, 0),
        cfg.location_poi_universe_max
    )

    return {
        "noise_lden": aligned_noise_lden,
        "noise_lnight": aligned_noise_lnight,
        "daylight": aligned_daylight,
        "view_sky": aligned_view_sky,
        "view_greenery": aligned_view_greenery,
        "location_poi": aligned_poi,
    }


def compute_term_coverage(
    df_aligned: pd.DataFrame,
    membership_functions: "FuzzyMembershipFunctions",
    threshold: float = 0.1,
) -> dict:
    """
    Compute coverage statistics for each linguistic term.

    This validation check ensures that each term in each variable
    is activated (membership > threshold) for at least some dwellings.
    If a term has 0% coverage, it means that dimension is "silent"
    and not contributing to the FIS output.

    Parameters:
        df_aligned: DataFrame with aligned features
        membership_functions: FuzzyMembershipFunctions instance
        threshold: Minimum membership degree to count as "activated"

    Returns:
        Dictionary with coverage percentages per variable and term
    """
    coverage = {}

    variable_mapping = {
        "noise_lden": "noise_lden",
        "noise_lnight": "noise_lnight",
        "daylight": "daylight",
        "view_sky": "view_sky",
        "view_greenery": "view_greenery",
        "location_poi": "location_poi",
    }

    for col, var in variable_mapping.items():
        if col not in df_aligned.columns:
            continue

        mfs = membership_functions.get_all_membership_functions(var)
        if not mfs:
            continue

        coverage[var] = {}
        values = df_aligned[col].dropna()
        n = len(values)

        if n == 0:
            for term in mfs:
                coverage[var][term] = 0.0
            continue

        for term in mfs:
            # Count how many dwellings have membership > threshold for this term
            activated = sum(
                membership_functions.fuzzify_value(var, v).get(term, 0) > threshold
                for v in values
            )
            coverage[var][term] = round(100.0 * activated / n, 1)

    return coverage


def validate_alignment(
    df_aligned: pd.DataFrame,
    membership_functions: "FuzzyMembershipFunctions",
    min_coverage: float = 5.0,
    threshold: float = 0.1,
) -> tuple[bool, str]:
    """
    Validate that the feature alignment produces reasonable term activation.

    Parameters:
        df_aligned: DataFrame with aligned features
        membership_functions: FuzzyMembershipFunctions instance
        min_coverage: Minimum percentage of dwellings that should activate each term
        threshold: Minimum membership degree for activation

    Returns:
        Tuple of (is_valid, message)
    """
    coverage = compute_term_coverage(df_aligned, membership_functions, threshold)

    issues = []
    for var, terms in coverage.items():
        for term, pct in terms.items():
            if pct < min_coverage:
                issues.append(f"{var}.{term}: {pct}% coverage (below {min_coverage}%)")

    if issues:
        msg = "Alignment validation warnings:\n" + "\n".join(f"  - {i}" for i in issues)
        return False, msg

    return True, "All terms have adequate coverage."


if __name__ == "__main__":
    # Example usage and testing
    print("Feature Alignment Module")
    print("=" * 60)

    # Create sample raw data
    sample_data = pd.DataFrame({
        "raw_noise_day_dba": [55.0, 65.0, 45.0, 70.0],
        "raw_noise_night_dba": [45.0, 55.0, 35.0, 60.0],
        "raw_daylight_klx": [0.5, 0.3, 0.8, 0.2],
        "raw_view_sky_sr": [0.01, 0.05, 0.1, 0.002],
        "raw_view_greenery_sr": [0.02, 0.01, 0.04, 0.005],
        "raw_poi_count": [100, 500, 50, 1000],
    })

    print("\nSample raw data:")
    print(sample_data)

    # Fit alignment config
    cfg = fit_alignment_config(sample_data)
    print(f"\nFitted alignment config:")
    print(f"  view_sky_ref: {cfg.view_sky_ref:.6f} sr")
    print(f"  view_greenery_ref: {cfg.view_greenery_ref:.6f} sr")
    print(f"  poi_log_p01: {cfg.poi_log_p01:.3f}")
    print(f"  poi_log_p99: {cfg.poi_log_p99:.3f}")

    # Align features
    aligned = align_features(sample_data, cfg)
    print("\nAligned features:")
    aligned_cols = ["noise_lden", "noise_lnight", "daylight", "view_sky", "view_greenery", "location_poi"]
    print(aligned[aligned_cols])

    # Test single input alignment
    print("\nSingle input alignment test:")
    single = align_single_input(
        noise_lden=55.0,
        noise_lnight=45.0,
        daylight_lux=300.0,
        view_sky_sr=0.05,
        view_greenery_sr=0.02,
        poi_count=200,
        cfg=cfg,
    )
    for k, v in single.items():
        print(f"  {k}: {v:.2f}")
