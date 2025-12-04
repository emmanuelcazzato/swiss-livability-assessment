"""
Validate Feature Alignment

This script checks that the feature alignment produces reasonable term activation
across all linguistic terms. It ensures that no dimension is "silent" in the FIS.

Expected output:
- Coverage percentages for each variable-term combination
- Warnings if any term has less than 5% coverage
- FLI score distribution comparison before/after alignment
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Add src to path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from membership_functions import FuzzyMembershipFunctions
from fuzzy_system import LiveabilityFuzzySystem
from feature_alignment import (
    FeatureAlignmentConfig,
    compute_term_coverage,
    validate_alignment,
)


def main():
    print("=" * 70)
    print("FEATURE ALIGNMENT VALIDATION")
    print("=" * 70)

    # Load data
    data_path = ROOT_DIR / "data" / "processed" / "dwellings_full.csv"
    config_path = ROOT_DIR / "data" / "processed" / "feature_alignment.json"

    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        print("Run prepare_full_features.py first.")
        return 1

    if not config_path.exists():
        print(f"Error: Alignment config not found: {config_path}")
        print("Run prepare_full_features.py first.")
        return 1

    df = pd.read_csv(data_path)
    config = FeatureAlignmentConfig.from_json(config_path)
    mf = FuzzyMembershipFunctions()
    fuzzy_system = LiveabilityFuzzySystem()

    print(f"\nLoaded {len(df)} dwellings")
    print(f"\nAlignment configuration:")
    print(f"  view_sky_ref: {config.view_sky_ref:.6f} sr")
    print(f"  view_greenery_ref: {config.view_greenery_ref:.6f} sr")
    print(f"  poi_log_p01: {config.poi_log_p01:.3f}")
    print(f"  poi_log_p99: {config.poi_log_p99:.3f}")

    # Check if we have aligned columns
    aligned_cols = ["noise_lden", "noise_lnight", "daylight", "view_sky", "view_greenery", "location_poi"]
    missing_cols = [c for c in aligned_cols if c not in df.columns]
    if missing_cols:
        print(f"\nError: Missing aligned columns: {missing_cols}")
        print("The data file appears to be in the old format.")
        return 1

    # =========================================================================
    # 1. Term Coverage Analysis
    # =========================================================================
    print("\n" + "=" * 70)
    print("1. TERM COVERAGE ANALYSIS")
    print("=" * 70)
    print("\n(Shows % of dwellings where each term has membership > 0.1)")

    coverage = compute_term_coverage(df, mf, threshold=0.1)

    for var in ["noise_lden", "noise_lnight", "daylight", "view_sky", "view_greenery", "location_poi"]:
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
    print("\n" + "=" * 70)
    print("2. FLI SCORE DISTRIBUTION")
    print("=" * 70)

    # Compute FLI scores for all dwellings
    print("\nComputing FLI scores for all dwellings...")
    fli_scores = []
    labels = {"poor": 0, "fair": 0, "good": 0, "excellent": 0}

    for _, row in df.iterrows():
        features = {
            "noise_lden": row["noise_lden"],
            "noise_lnight": row["noise_lnight"],
            "daylight": row["daylight"],
            "view_sky": row["view_sky"],
            "view_greenery": row["view_greenery"],
            "location_poi": row["location_poi"],
        }

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
    valid_df = df.dropna(subset=aligned_cols).copy()
    valid_df = valid_df.head(len(fli_scores))
    valid_df["fli_score"] = fli_scores

    print("\nPearson correlation with FLI score:")
    for col in aligned_cols:
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
