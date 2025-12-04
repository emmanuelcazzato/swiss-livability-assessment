"""
Feature Alignment Module - V2

Transforms raw features from Swiss Dwellings dataset to match the FIS input universes.

V2 Simplifications:
- Daylight: stays in klx (no conversion to lux)
- View sky/greenery: direct pass-through (raw sr values, no scaling)
- Location POI: log10(count+1) transformation only (no min-max scaling)
- Noise: dBA pass-through with <=0 treated as missing

V2 Design Rationale:
- MF universes now calibrated to match actual data distributions
- Removes complex percentile-based scaling that caused saturation issues
- POI uses log10 (base-10) for intuitive interpretation

Reference data statistics (Swiss Dwellings v3.0.0):
- view_sky: 0-0.13 sr (median ~0.029, 95th pctl ~0.05)
- view_greenery: 0-0.06 sr (median ~0.01, 95th pctl ~0.026)
- daylight: 0-3.91 klx (noon illuminance)
- location_poi: 3-2662 counts -> log10: ~0.6-3.43
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
    Configuration for feature alignment transformations - V2.

    V2 Simplification: Most parameters are now fixed based on dataset analysis.
    Only POI-related parameters are retained for reference.

    Attributes:
        daylight_klx_cap: Maximum daylight value in klx (matches FIS universe max)
        view_sky_max: Maximum view_sky in sr (matches FIS universe max)
        view_greenery_max: Maximum view_greenery in sr (matches FIS universe max)
        location_poi_log_max: Maximum location_poi in log10 scale (matches FIS universe max)
    """
    # V2: Fixed values based on dataset analysis and MF universe design
    daylight_klx_cap: float = 6.0       # klx, matching universe max
    view_sky_max: float = 0.13          # sr, matching universe max
    view_greenery_max: float = 0.06     # sr, matching universe max
    location_poi_log_max: float = 3.5   # log10 scale, matching universe max

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
            # V2: Config is optional since values are fixed
            return FeatureAlignmentConfig()
        obj = json.loads(path.read_text())
        return FeatureAlignmentConfig(**obj)

    @staticmethod
    def get_default() -> "FeatureAlignmentConfig":
        """Get default V2 configuration."""
        return FeatureAlignmentConfig()


def fit_alignment_config(
    df_raw: pd.DataFrame,
    view_sky_col: str = "raw_view_sky_sr",
    view_greenery_col: str = "raw_view_greenery_sr",
    poi_count_col: str = "raw_poi_count",
) -> FeatureAlignmentConfig:
    """
    Fit alignment configuration parameters from raw feature data - V2.

    V2 Simplification: Returns default config since parameters are now fixed.
    This function is retained for API compatibility but simply validates
    that the data falls within expected ranges.

    Parameters:
        df_raw: DataFrame with raw feature columns
        view_sky_col: Column name for raw view sky values (sr)
        view_greenery_col: Column name for raw view greenery values (sr)
        poi_count_col: Column name for raw POI count

    Returns:
        FeatureAlignmentConfig with default V2 parameters
    """
    # V2: Validate data ranges (informational only)
    if view_sky_col in df_raw.columns:
        view_sky_max = df_raw[view_sky_col].max()
        if view_sky_max > 0.13:
            print(f"Warning: view_sky max ({view_sky_max:.4f}) exceeds expected range (0-0.13 sr)")

    if view_greenery_col in df_raw.columns:
        view_greenery_max = df_raw[view_greenery_col].max()
        if view_greenery_max > 0.06:
            print(f"Warning: view_greenery max ({view_greenery_max:.4f}) exceeds expected range (0-0.06 sr)")

    if poi_count_col in df_raw.columns:
        poi_max = df_raw[poi_count_col].max()
        poi_log_max = np.log10(poi_max + 1) if poi_max > 0 else 0
        if poi_log_max > 3.5:
            print(f"Warning: poi_log max ({poi_log_max:.2f}) exceeds expected range (0-3.5)")

    return FeatureAlignmentConfig.get_default()


def align_features(
    df_raw: pd.DataFrame,
    cfg: FeatureAlignmentConfig = None,
    inplace: bool = False,
) -> pd.DataFrame:
    """
    Transform raw features to aligned features matching FIS input universes - V2.

    V2 Transformations (simplified):
    1. Noise: Pass-through, treat <=0 as missing
    2. Daylight: stays in klx (pass-through), capped at universe max
    3. View sky: pass-through (raw sr), capped at universe max
    4. View greenery: pass-through (raw sr), capped at universe max
    5. Location POI: log10(count+1) only, capped at universe max

    Parameters:
        df_raw: DataFrame with raw feature columns (raw_* prefix)
        cfg: FeatureAlignmentConfig (optional, uses default if None)
        inplace: If True, modifies df_raw; otherwise returns a copy

    Returns:
        DataFrame with aligned feature columns added
    """
    if cfg is None:
        cfg = FeatureAlignmentConfig.get_default()

    out = df_raw if inplace else df_raw.copy()

    # Noise: treat <=0 as missing (these are likely invalid measurements)
    for col in ["raw_noise_day_dba", "raw_noise_night_dba"]:
        if col in out.columns:
            out.loc[out[col] <= 0, col] = np.nan

    # Daylight: stays in klx (V2), just clip to universe max
    if "raw_daylight_klx" in out.columns:
        out["daylight"] = out["raw_daylight_klx"].clip(0, cfg.daylight_klx_cap)

    # View sky: pass-through (V2), clip to universe max
    if "raw_view_sky_sr" in out.columns:
        out["view_sky"] = out["raw_view_sky_sr"].clip(0, cfg.view_sky_max)

    # View greenery: pass-through (V2), clip to universe max
    if "raw_view_greenery_sr" in out.columns:
        out["view_greenery"] = out["raw_view_greenery_sr"].clip(0, cfg.view_greenery_max)

    # POI: log10(count+1) transformation (V2)
    if "raw_poi_count" in out.columns:
        out["location_poi"] = np.log10(
            out["raw_poi_count"].clip(lower=0) + 1
        ).clip(0, cfg.location_poi_log_max)

    # Map noise columns to FIS naming convention
    if "raw_noise_day_dba" in out.columns:
        out["noise_lden"] = out["raw_noise_day_dba"]
    if "raw_noise_night_dba" in out.columns:
        out["noise_lnight"] = out["raw_noise_night_dba"]

    return out


def align_single_input(
    noise_lden: float,
    noise_lnight: float,
    daylight_klx: float,
    view_sky_sr: float,
    view_greenery_sr: float,
    poi_count: int,
    cfg: FeatureAlignmentConfig = None,
) -> dict:
    """
    Align a single dwelling's input features for the FIS - V2.

    This is used by the web API to align user-provided inputs
    before passing them to the fuzzy inference system.

    V2 Simplification: Direct pass-through for most features,
    only POI gets log10 transformation.

    Parameters:
        noise_lden: Day noise level in dBA
        noise_lnight: Night noise level in dBA
        daylight_klx: Daylight illuminance in klx (V2: user provides klx directly)
        view_sky_sr: Sky view in steradians (V2: raw value, no scaling)
        view_greenery_sr: Greenery view in steradians (V2: raw value, no scaling)
        poi_count: Number of POIs within 10-min walk
        cfg: FeatureAlignmentConfig (optional, uses default if None)

    Returns:
        Dictionary with aligned feature values ready for FIS
    """
    if cfg is None:
        cfg = FeatureAlignmentConfig.get_default()

    # Noise: pass-through (but validate)
    aligned_noise_lden = noise_lden if noise_lden > 0 else np.nan
    aligned_noise_lnight = noise_lnight if noise_lnight > 0 else np.nan

    # Daylight: stays in klx (V2), just clip to universe max
    aligned_daylight = min(max(daylight_klx, 0), cfg.daylight_klx_cap)

    # View sky: pass-through (V2), clip to universe max
    aligned_view_sky = min(max(view_sky_sr, 0), cfg.view_sky_max)

    # View greenery: pass-through (V2), clip to universe max
    aligned_view_greenery = min(max(view_greenery_sr, 0), cfg.view_greenery_max)

    # POI: log10(count+1) transformation (V2)
    aligned_poi = min(
        max(math.log10(max(poi_count, 0) + 1), 0),
        cfg.location_poi_log_max
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
    # Example usage and testing - V2
    print("Feature Alignment Module - V2")
    print("=" * 60)

    # Create sample raw data
    sample_data = pd.DataFrame({
        "raw_noise_day_dba": [55.0, 65.0, 45.0, 70.0],
        "raw_noise_night_dba": [45.0, 55.0, 35.0, 60.0],
        "raw_daylight_klx": [0.5, 1.3, 2.8, 0.2],
        "raw_view_sky_sr": [0.01, 0.05, 0.10, 0.002],
        "raw_view_greenery_sr": [0.02, 0.01, 0.04, 0.005],
        "raw_poi_count": [100, 500, 50, 1000],
    })

    print("\nSample raw data:")
    print(sample_data)

    # Get default V2 config
    cfg = FeatureAlignmentConfig.get_default()
    print(f"\nV2 alignment config (fixed values):")
    print(f"  daylight_klx_cap: {cfg.daylight_klx_cap} klx")
    print(f"  view_sky_max: {cfg.view_sky_max} sr")
    print(f"  view_greenery_max: {cfg.view_greenery_max} sr")
    print(f"  location_poi_log_max: {cfg.location_poi_log_max}")

    # Align features (V2: mostly pass-through)
    aligned = align_features(sample_data, cfg)
    print("\nAligned features (V2):")
    aligned_cols = ["noise_lden", "noise_lnight", "daylight", "view_sky", "view_greenery", "location_poi"]
    print(aligned[aligned_cols])

    # Test single input alignment (V2)
    print("\nSingle input alignment test (V2):")
    single = align_single_input(
        noise_lden=55.0,
        noise_lnight=45.0,
        daylight_klx=1.5,        # V2: klx input
        view_sky_sr=0.03,        # V2: raw sr
        view_greenery_sr=0.01,   # V2: raw sr
        poi_count=200,
        cfg=cfg,
    )
    for k, v in single.items():
        if isinstance(v, float) and not np.isnan(v):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
