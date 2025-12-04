"""
Prepare full features from swiss-dwellings dataset for the Fuzzy Inference System - V2.

Two-stage processing:
1. Build raw building-level features (with raw_* prefix, original units)
2. Apply V2 feature alignment (simplified: mostly pass-through)

Feature extraction decisions:
- Noise: window-level max per source (traffic/train) with energy summation, by day/night
- View: p80 aggregates (view_sky_p80, view_greenery_p80) in raw sr units
- Daylight: sun klx at 12:00 for equinox, summer solstice, winter solstice, averaged

V2 Changes from V1:
- Daylight: stays in klx (no conversion to lux)
- View: pass-through (raw sr, no percentile scaling)
- POI: log10(count+1) only (no min-max scaling)

Output: data/processed/dwellings_full.csv with columns:
  Raw features (for debugging/analysis):
    building_id, raw_noise_day_dba, raw_noise_night_dba, raw_daylight_klx,
    raw_view_sky_sr, raw_view_greenery_sr, raw_poi_count

  V2 Aligned features (for FIS input):
    noise_lden (dBA), noise_lnight (dBA), daylight (klx),
    view_sky (sr), view_greenery (sr), location_poi (log10)

Also outputs: data/processed/feature_alignment.json with V2 config parameters
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pandas as pd

from common import ROOT, setup_paths, print_section_header

# Add src to path
setup_paths()

from feature_alignment import (
    FeatureAlignmentConfig,
    fit_alignment_config,
    align_features,
)


def energy_sum_db(values: List[float]) -> float:
    vals = [v for v in values if pd.notnull(v) and v > 0]
    if not vals:
        return 0.0
    linear = sum(10 ** (v / 10.0) for v in vals)
    if linear <= 0:
        return 0.0
    return 10.0 * math.log10(linear)


def prepare_features(
    data_root: Path = None,
    output_path: Path = None,
    chunksize: int = 200_000,
):
    # Default paths relative to project root
    scripts_dir = Path(__file__).resolve().parent
    root_dir = scripts_dir.parent

    if data_root is None:
        data_root = root_dir / "data" / "raw" / "swiss-dwellings-v3.0.0"
    if output_path is None:
        output_path = root_dir / "data" / "processed" / "dwellings_full.csv"
    sim_path = data_root / "simulations.csv"
    loc_path = data_root / "locations.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Columns we need from simulations
    sim_cols = [
        "building_id",
        # window noise (max per area)
        "window_noise_traffic_day_max",
        "window_noise_traffic_night_max",
        "window_noise_train_day_max",
        "window_noise_train_night_max",
        # view p80
        "view_sky_p80",
        "view_greenery_p80",
        # sun at 12:00 (klx) for 3 seasons
        "sun_201803211200_mean",
        "sun_201806211200_mean",
        "sun_201812211200_mean",
    ]

    # Aggregators
    # For noise max we keep global max across rows per building_id
    noise_max_cols = [
        "window_noise_traffic_day_max",
        "window_noise_traffic_night_max",
        "window_noise_train_day_max",
        "window_noise_train_night_max",
    ]

    # For view and daylight we accumulate sum and count to compute means later
    view_cols = ["view_sky_p80", "view_greenery_p80"]
    sun_cols = [
        "sun_201803211200_mean",
        "sun_201806211200_mean",
        "sun_201812211200_mean",
    ]

    # Initialize empty frames
    noise_max_df = pd.DataFrame(columns=noise_max_cols)
    noise_max_df.index.name = "building_id"
    view_sum_df = pd.DataFrame(columns=view_cols)
    view_sum_df.index.name = "building_id"
    daylight_sum = pd.Series(dtype=float, name="daylight_sum")
    counts = pd.Series(dtype=int, name="count")

    print("Reading simulations in chunks and aggregating per building_id ...")
    for chunk in pd.read_csv(sim_path, usecols=sim_cols, chunksize=chunksize):
        # Per-row daylight (klx)
        chunk["daylight_avg_klx_row"] = chunk[sun_cols].mean(axis=1)

        # noise: max per building across rows
        nmax = chunk.groupby("building_id")[noise_max_cols].max()
        if not noise_max_df.empty:
            # align and take max
            noise_max_df = (
                pd.concat([noise_max_df, nmax])
                .groupby(level=0)
                .max()
            )
        else:
            noise_max_df = nmax

        # view: sum per building to compute mean later
        vsum = chunk.groupby("building_id")[view_cols].sum()
        if not view_sum_df.empty:
            view_sum_df = view_sum_df.add(vsum, fill_value=0)
        else:
            view_sum_df = vsum

        # daylight sum
        dsum = chunk.groupby("building_id")["daylight_avg_klx_row"].sum()
        daylight_sum = daylight_sum.add(dsum, fill_value=0)

        # counts
        cnt = chunk.groupby("building_id").size()
        counts = counts.add(cnt, fill_value=0)

    # Compute means
    print("Computing building-level means for view and daylight ...")
    view_mean_df = view_sum_df.div(counts, axis=0)
    daylight_mean = daylight_sum.div(counts)
    view_mean_df = view_mean_df.fillna(0)
    daylight_mean = daylight_mean.fillna(0)

    # Compute combined noise via energy sum
    print("Combining window-level noise sources (traffic + train) via energy sum ...")
    agg = noise_max_df.copy()
    agg["noise_lden"] = [
        energy_sum_db([row.get("window_noise_traffic_day_max", float("nan")), row.get("window_noise_train_day_max", float("nan"))])
        for _, row in agg.iterrows()
    ]
    agg["noise_lnight"] = [
        energy_sum_db([row.get("window_noise_traffic_night_max", float("nan")), row.get("window_noise_train_night_max", float("nan"))])
        for _, row in agg.iterrows()
    ]

    # =========================================================================
    # STAGE 1: Assemble RAW feature frame (original units, raw_* prefix)
    # =========================================================================
    print("\n" + "=" * 60)
    print("STAGE 1: Building raw features (original units)")
    print("=" * 60)

    raw_features_df = pd.DataFrame({
        "building_id": agg.index,
        "raw_noise_day_dba": agg["noise_lden"].values,
        "raw_noise_night_dba": agg["noise_lnight"].values,
        "raw_daylight_klx": daylight_mean.reindex(agg.index).values,
        "raw_view_sky_sr": view_mean_df.reindex(agg.index)["view_sky_p80"].values,
        "raw_view_greenery_sr": view_mean_df.reindex(agg.index)["view_greenery_p80"].values,
    })

    # Load locations for POI aggregation
    print("Aggregating POI from locations.csv ...")
    loc_df = pd.read_csv(loc_path)
    poi_cols = [c for c in loc_df.columns if c.startswith("walkshed_")]
    if poi_cols:
        loc_df["raw_poi_count"] = loc_df[poi_cols].fillna(0).sum(axis=1)
        loc_df_small = loc_df[["building_id", "raw_poi_count"]]
    else:
        loc_df_small = loc_df[["building_id"]].copy()
        loc_df_small["raw_poi_count"] = 0

    # Merge raw features with POI counts
    raw_df = raw_features_df.merge(loc_df_small, on="building_id", how="left")

    # Basic stats for raw features
    def qstats(s: pd.Series):
        return {
            "min": float(s.min()),
            "q25": float(s.quantile(0.25)),
            "q50": float(s.quantile(0.50)),
            "q75": float(s.quantile(0.75)),
            "q90": float(s.quantile(0.90)),
            "q95": float(s.quantile(0.95)),
            "max": float(s.max()),
        }

    print("\nRaw feature distributions:")
    print(f"  raw_noise_day_dba: {qstats(raw_df['raw_noise_day_dba'])}")
    print(f"  raw_noise_night_dba: {qstats(raw_df['raw_noise_night_dba'])}")
    print(f"  raw_daylight_klx: {qstats(raw_df['raw_daylight_klx'])}")
    print(f"  raw_view_sky_sr: {qstats(raw_df['raw_view_sky_sr'])}")
    print(f"  raw_view_greenery_sr: {qstats(raw_df['raw_view_greenery_sr'])}")
    print(f"  raw_poi_count: {qstats(raw_df['raw_poi_count'])}")

    # =========================================================================
    # STAGE 2: Fit alignment config and apply transformation
    # =========================================================================
    print("\n" + "=" * 60)
    print("STAGE 2: Fitting and applying feature alignment")
    print("=" * 60)

    # Fit alignment configuration from raw data
    print("\nFitting alignment configuration...")
    alignment_config = fit_alignment_config(raw_df)

    print(f"  daylight_klx_cap: {alignment_config.daylight_klx_cap} klx")
    print(f"  view_sky_max: {alignment_config.view_sky_max} sr")
    print(f"  view_greenery_max: {alignment_config.view_greenery_max} sr")
    print(f"  location_poi_log_max: {alignment_config.location_poi_log_max}")

    # Save alignment config
    config_path = output_path.parent / "feature_alignment.json"
    alignment_config.to_json(config_path)
    print(f"\nSaved alignment config to: {config_path}")

    # Apply alignment transformation
    print("\nApplying alignment transformation...")
    aligned_df = align_features(raw_df, alignment_config)

    # Print aligned feature distributions (V2 units)
    print("\nAligned feature distributions (V2):")
    print(f"  noise_lden (dBA): {qstats(aligned_df['noise_lden'].dropna())}")
    print(f"  noise_lnight (dBA): {qstats(aligned_df['noise_lnight'].dropna())}")
    print(f"  daylight (klx, 0-6): {qstats(aligned_df['daylight'])}")
    print(f"  view_sky (sr, 0-0.13): {qstats(aligned_df['view_sky'])}")
    print(f"  view_greenery (sr, 0-0.06): {qstats(aligned_df['view_greenery'])}")
    print(f"  location_poi (log10, 0-3.5): {qstats(aligned_df['location_poi'])}")

    # =========================================================================
    # Save final output with both raw and aligned columns
    # =========================================================================
    # Select columns to output (raw for debugging + aligned for FIS)
    output_cols = [
        "building_id",
        # Raw features (original units)
        "raw_noise_day_dba",
        "raw_noise_night_dba",
        "raw_daylight_klx",
        "raw_view_sky_sr",
        "raw_view_greenery_sr",
        "raw_poi_count",
        # Aligned features (FIS input)
        "noise_lden",
        "noise_lnight",
        "daylight",
        "view_sky",
        "view_greenery",
        "location_poi",
    ]

    aligned_df[output_cols].to_csv(output_path, index=False)
    print(f"\nSaved features to: {output_path}")
    print(f"Rows: {len(aligned_df)} | Columns: {output_cols}")


if __name__ == "__main__":
    prepare_features()
