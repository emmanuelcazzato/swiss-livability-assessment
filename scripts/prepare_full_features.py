"""
Prepare full features from swiss-dwellings dataset for the Fuzzy Inference System.

Decisions (confirmed by user):
- Noise: use window-level max per source (traffic/train) with energy summation, by day/night.
- View: use p80 aggregates (view_sky_p80, view_greenery_p80).
- Daylight: use sun klx at 12:00 for equinox, summer solstice, winter solstice and average them.

Output: data/processed/dwellings_full.csv with columns:
  building_id, noise_lden, noise_lnight, daylight_avg_klx, view_sky, view_greenery, location_poi_count
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import List

import pandas as pd


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

    # Assemble feature frame
    features_df = pd.DataFrame({
        "building_id": agg.index,
        "noise_lden": agg["noise_lden"].values,
        "noise_lnight": agg["noise_lnight"].values,
        "daylight_avg_klx": daylight_mean.reindex(agg.index).values,
        "view_sky": view_mean_df.reindex(agg.index)["view_sky_p80"].values,
        "view_greenery": view_mean_df.reindex(agg.index)["view_greenery_p80"].values,
    })

    # Load locations for POI aggregation
    print("Aggregating POI from locations.csv ...")
    loc_df = pd.read_csv(loc_path)
    poi_cols = [c for c in loc_df.columns if c.startswith("walkshed_")]
    if poi_cols:
        loc_df["location_poi_count"] = loc_df[poi_cols].fillna(0).sum(axis=1)
        loc_df_small = loc_df[["building_id", "location_poi_count"]]
    else:
        loc_df_small = loc_df[["building_id"]].copy()
        loc_df_small["location_poi_count"] = 0

    # Merge
    merged = features_df.merge(loc_df_small, on="building_id", how="left")

    # Basic stats and threshold suggestions for views
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

    print("\nView (sr) distribution snapshots (for membership tuning):")
    print("view_sky:", qstats(merged["view_sky"]))
    print("view_greenery:", qstats(merged["view_greenery"]))

    # Save
    merged.to_csv(output_path, index=False)
    print(f"\nSaved features to: {output_path}")
    print(f"Rows: {len(merged)} | Columns: {list(merged.columns)}")


if __name__ == "__main__":
    prepare_features()

