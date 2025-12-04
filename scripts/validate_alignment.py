"""
Validate Feature Alignment - V2

This script checks that the feature alignment produces reasonable term activation
across all linguistic terms. It ensures that no dimension is "silent" in the FIS.

V2 Changes:
- Updated config parameter names to V2 (daylight_klx_cap, view_*_max, location_poi_log_max)
- Uses simplified alignment (klx, raw sr, log10 POI)

Expected output:
- Coverage percentages for each variable-term combination
- Warnings if any term has less than 5% coverage
- FLI score distribution comparison before/after alignment
"""

from __future__ import annotations

import sys

import pandas as pd
import numpy as np

from common import (
    ROOT, setup_paths,
    load_dwellings_data,
    FEATURE_COLUMNS,
    print_section_header
)

setup_paths()

from membership_functions import FuzzyMembershipFunctions
from fuzzy_system import LiveabilityFuzzySystem
from feature_alignment import (
    FeatureAlignmentConfig,
    compute_term_coverage,
    validate_alignment,
)


def main():
    print_section_header("FEATURE ALIGNMENT VALIDATION", width=70)

    # Load data
    config_path = ROOT / "data" / "processed" / "feature_alignment.json"

    try:
        df = load_dwellings_data()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    # V2: Config file is optional since parameters are fixed defaults
    if config_path.exists():
        config = FeatureAlignmentConfig.from_json(config_path)
    else:
        print("Note: Using default V2 alignment config (config file not found)")
        config = FeatureAlignmentConfig.get_default()
    mf = FuzzyMembershipFunctions()
    fuzzy_system = LiveabilityFuzzySystem()

    print(f"\nLoaded {len(df)} dwellings")
    print(f"\nV2 Alignment configuration:")
    print(f"  daylight_klx_cap: {config.daylight_klx_cap} klx")
    print(f"  view_sky_max: {config.view_sky_max} sr")
    print(f"  view_greenery_max: {config.view_greenery_max} sr")
    print(f"  location_poi_log_max: {config.location_poi_log_max}")

    # Check if we have aligned columns
    missing_cols = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"\nError: Missing aligned columns: {missing_cols}")
        print("The data file appears to be in the old format.")
        return 1

    # =========================================================================
    # 1. Term Coverage Analysis
    # =========================================================================
    print_section_header("1. TERM COVERAGE ANALYSIS", width=70)
    print("\n(Shows % of dwellings where each term has membership > 0.1)")

    coverage = compute_term_coverage(df, mf, threshold=0.1)

    for var in FEATURE_COLUMNS:
        if var not in coverage:
            print(f"\n{var}: [not computed]")
            continue

        print(f"\n{var}:")
        terms = coverage[var]
        for term, pct in terms.items():
            status = "" if pct >= 5.0 else " [LOW COVERAGE!]"
            print(f"  {term:12s}: {pct:5.1f}%{status}")

    # Validate alignment
    is_valid, msg = validate_alignment(df, mf, min_coverage=5.0, threshold=0.1)
    print(f"\nValidation result: {'PASS' if is_valid else 'WARNINGS'}")
    if not is_valid:
        print(msg)

    # =========================================================================
    # 2. FLI Score Distribution
    # =========================================================================
    print_section_header("2. FLI SCORE DISTRIBUTION", width=70)

    # Compute FLI scores for all dwellings
    print("\nComputing FLI scores for all dwellings...")
    fli_scores = []
    labels = {"poor": 0, "fair": 0, "good": 0, "excellent": 0}

    for _, row in df.iterrows():
        features = {col: row[col] for col in FEATURE_COLUMNS}

        # Skip rows with NaN
        if any(pd.isna(v) for v in features.values()):
            continue

        result = fuzzy_system.compute_single_dwelling(features)
        fli_scores.append(result["fli_score"])
        labels[result["linguistic_label"].lower()] += 1

    fli_scores = np.array(fli_scores)

    print(f"\nFLI Score Statistics (n={len(fli_scores)}):")
    print(f"  Mean:   {fli_scores.mean():.2f}")
    print(f"  Std:    {fli_scores.std():.2f}")
    print(f"  Min:    {fli_scores.min():.2f}")
    print(f"  25%:    {np.percentile(fli_scores, 25):.2f}")
    print(f"  Median: {np.percentile(fli_scores, 50):.2f}")
    print(f"  75%:    {np.percentile(fli_scores, 75):.2f}")
    print(f"  Max:    {fli_scores.max():.2f}")

    total = sum(labels.values())
    print(f"\nLinguistic Label Distribution:")
    for label in ["excellent", "good", "fair", "poor"]:
        count = labels[label]
        pct = 100.0 * count / total if total > 0 else 0
        print(f"  {label.capitalize():10s}: {count:5d} ({pct:5.1f}%)")

    # =========================================================================
    # 3. Check for problematic patterns
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. DIAGNOSTIC CHECKS")
    print("=" * 70)

    # Check for FLI=50 concentration (sign of dimension failure)
    fli_at_50 = np.sum(np.abs(fli_scores - 50.0) < 0.5)
    pct_at_50 = 100.0 * fli_at_50 / len(fli_scores)
    if pct_at_50 > 20:
        print(f"\n[WARNING] {pct_at_50:.1f}% of FLI scores are at exactly 50.0")
        print("  This may indicate dimension failure (some variables not contributing).")
    else:
        print(f"\n[OK] Only {pct_at_50:.1f}% of FLI scores at 50.0 (expected for balanced inputs)")

    # Check for missing Excellent
    if labels["excellent"] == 0:
        print("\n[WARNING] No dwellings rated 'Excellent'")
        print("  Check if view/daylight/location alignment is too conservative.")
    else:
        print(f"\n[OK] {labels['excellent']} dwellings rated 'Excellent'")

    # Check for missing Fair
    if labels["fair"] < 10:
        print(f"\n[WARNING] Only {labels['fair']} dwellings rated 'Fair'")
        print("  The distribution may be too polarized between Good and Poor.")
    else:
        print(f"\n[OK] {labels['fair']} dwellings rated 'Fair'")

    # =========================================================================
    # 4. Correlation Analysis
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. FLI CORRELATION WITH INPUT FEATURES")
    print("=" * 70)

    # Create a dataframe with valid scores
    valid_df = df.dropna(subset=FEATURE_COLUMNS).copy()
    valid_df = valid_df.head(len(fli_scores))
    valid_df["fli_score"] = fli_scores

    print("\nPearson correlation with FLI score:")
    for col in FEATURE_COLUMNS:
        if col in valid_df.columns:
            corr = valid_df["fli_score"].corr(valid_df[col])
            direction = "+" if corr > 0 else "-"
            strength = "strong" if abs(corr) > 0.3 else ("moderate" if abs(corr) > 0.1 else "weak")
            # Expected direction
            if col.startswith("noise"):
                expected = "-"  # More noise = lower FLI
            else:
                expected = "+"  # More daylight/view/poi = higher FLI
            match = "[OK]" if (corr > 0) == (expected == "+") else "[CHECK]"
            print(f"  {col:15s}: {corr:+.3f} ({strength}, {match})")

    print("\n" + "=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
