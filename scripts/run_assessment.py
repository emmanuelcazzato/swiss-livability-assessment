"""
Swiss Residential Perceived Livability Assessment

Main script for running the Fuzzy Inference System and generating results.
Computes FLI scores for all dwellings and optionally creates visualizations.

Usage:
    python scripts/run_assessment.py           # Full run with visualizations
    python scripts/run_assessment.py --no-viz  # Skip visualization generation
"""

import argparse
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from common import (
    ROOT, setup_paths,
    load_dwellings_data,
    FEATURE_COLUMNS,
    print_section_header,
    print_label_distribution
)

# Ensure src is in path
setup_paths()

from fuzzy_system import LiveabilityFuzzySystem


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run Swiss Livability Assessment'
    )
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip visualization generation'
    )
    return parser.parse_args()


def create_visualizations(df: pd.DataFrame) -> None:
    """
    Create visualizations for the FLI results.

    Args:
        df: DataFrame with FLI scores and features
    """
    print_section_header("Step 9: Creating Visualizations...")

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)

    # Create output directory
    figures_dir = ROOT / 'results' / 'figures'
    os.makedirs(figures_dir, exist_ok=True)

    # Feature definitions for plots
    features = [
        ('noise_lden', 'Noise Lden (dBA)'),
        ('noise_lnight', 'Noise Lnight (dBA)'),
        ('raw_daylight_klx', 'Daylight (klx)'),
        ('raw_view_sky_sr', 'View Sky p80 (sr)'),
        ('raw_view_greenery_sr', 'View Greenery p80 (sr)'),
        ('raw_poi_count', 'POI Count')
    ]
    colors = {'excellent': '#2ecc71', 'good': '#3498db', 'fair': '#f39c12', 'poor': '#e74c3c'}

    # 1. FLI Score Distribution
    print("  Creating FLI score distribution plot...")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['fli_score'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.axvline(df['fli_score'].mean(), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {df["fli_score"].mean():.2f}')
    ax.set_xlabel('Fuzzy Livability Index (FLI)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Distribution of Fuzzy Livability Index Scores', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(figures_dir / 'fli_distribution.png', dpi=300)
    plt.close()

    # 2. Linguistic Label Distribution
    print("  Creating linguistic label distribution plot...")
    fig, ax = plt.subplots(figsize=(10, 6))
    label_counts = df['linguistic_label'].value_counts()
    label_colors = [colors.get(label, 'gray') for label in label_counts.index]
    bars = ax.bar(range(len(label_counts)), label_counts.values, color=label_colors,
                  edgecolor='black', alpha=0.8)
    ax.set_xticks(range(len(label_counts)))
    ax.set_xticklabels([label.capitalize() for label in label_counts.index], fontsize=11)
    ax.set_ylabel('Number of Dwellings', fontsize=12)
    ax.set_title('Distribution of Linguistic Livability Labels', fontsize=14, fontweight='bold')
    for bar, count in zip(bars, label_counts.values):
        percentage = (count / len(df)) * 100
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{count}\n({percentage:.1f}%)', ha='center', va='bottom', fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(figures_dir / 'linguistic_labels.png', dpi=300)
    plt.close()

    # 3. Feature vs FLI Score Scatter Plots
    print("  Creating feature correlation plots...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for ax, (feature, label) in zip(axes.flat, features):
        ax.scatter(df[feature], df['fli_score'], c=df['fli_score'],
                   cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=0.5)
        ax.set_xlabel(label, fontsize=10)
        ax.set_ylabel('FLI Score', fontsize=10)
        ax.set_title(f'FLI vs {label}', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        corr = df[feature].corr(df['fli_score'])
        ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                verticalalignment='top', fontsize=9)
    plt.tight_layout()
    plt.savefig(figures_dir / 'feature_correlations.png', dpi=300)
    plt.close()

    # 4. Box plot by linguistic label
    print("  Creating box plots by linguistic label...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    label_order = ['poor', 'fair', 'good', 'excellent']
    for ax, (feature, label) in zip(axes.flat, features):
        df_plot = df[[feature, 'linguistic_label']].copy()
        df_plot['linguistic_label'] = pd.Categorical(
            df_plot['linguistic_label'], categories=label_order, ordered=True
        )
        sns.boxplot(data=df_plot, x='linguistic_label', y=feature, ax=ax,
                    hue='linguistic_label', palette=colors, order=label_order, legend=False)
        ax.set_xlabel('Livability Label', fontsize=10)
        ax.set_ylabel(label, fontsize=10)
        ax.set_title(f'{label} by Livability Label', fontsize=11, fontweight='bold')
        ax.set_xticks(range(len(label_order)))
        ax.set_xticklabels([l.capitalize() for l in label_order], rotation=0)
        ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(figures_dir / 'features_by_label.png', dpi=300)
    plt.close()

    # 5. Correlation heatmap
    print("  Creating correlation heatmap...")
    fig, ax = plt.subplots(figsize=(10, 8))
    feature_cols = [f[0] for f in features] + ['fli_score']
    corr_matrix = df[feature_cols].corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(figures_dir / 'correlation_heatmap.png', dpi=300)
    plt.close()

    print(f"\n  All visualizations saved to: {figures_dir}")


def main():
    args = parse_args()

    print_section_header("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT")

    # Step 1: Load prepared full features
    print("\nStep 1: Loading prepared full-feature dataset...")
    try:
        df = load_dwellings_data()
    except FileNotFoundError as e:
        print(f"[Error] {e}")
        return
    print(f"Loaded {len(df)} dwellings")
    print(f"Features: {list(df.columns)}")

    # Step 2: Prepare features for fuzzy system
    print_section_header("Step 2: Preparing features for fuzzy inference...")
    features_df = df[FEATURE_COLUMNS].copy()
    print("\nFeature Statistics:")
    print(features_df.describe())

    # Step 3: Initialize Fuzzy Inference System
    print_section_header("Step 3: Initializing Fuzzy Inference System...")
    fis = LiveabilityFuzzySystem()
    print("\nRule Base Summary:")
    rule_stats = fis.rule_base.get_rule_statistics()
    print(f"Total rules: {rule_stats['total_rules']}")
    print(f"Variables used: {', '.join(rule_stats['variables_used'])}")
    print(f"\nRules by consequent:")
    for consequent, count in rule_stats['rules_by_consequent'].items():
        print(f"  {consequent}: {count} rules")

    # Step 4: Compute Fuzzy Livability Index
    print_section_header("Step 4: Computing Fuzzy Livability Index for all dwellings...")
    results_df = fis.compute_batch(features_df)
    final_df = pd.concat([df, results_df], axis=1)

    # Step 5: Analyze Results
    print_section_header("Step 5: Analyzing Results...")
    print("\nFLI Score Distribution:")
    print(final_df['fli_score'].describe())
    print("\nLinguistic Label Distribution:")
    print_label_distribution(final_df['linguistic_label'])

    # Step 6: Example Explanations
    print_section_header("Step 6: Example Dwelling Assessments...")
    examples = {}
    for label in ['excellent', 'good', 'fair', 'poor']:
        subset = final_df[final_df['linguistic_label'] == label]
        if len(subset) > 0:
            examples[label] = subset.iloc[0]

    for label, row in examples.items():
        print(f"\n{'='*80}")
        print(f"EXAMPLE: {label.upper()} LIVABILITY")
        print(f"{'='*80}")
        print(f"Building ID: {int(row['building_id'])}")
        print(f"FLI Score: {row['fli_score']:.2f}/100")
        print(f"\nInput Features:")
        print(f"  Noise Lden: {row['noise_lden']:.1f} dBA")
        print(f"  Noise Lnight: {row['noise_lnight']:.1f} dBA")
        print(f"  Daylight: {row['raw_daylight_klx']:.3f} klx ({row['raw_daylight_klx']*1000:.0f} lux)")
        print(f"  View Sky (p80): {row['raw_view_sky_sr']:.4f} sr")
        print(f"  View Greenery (p80): {row['raw_view_greenery_sr']:.4f} sr")
        print(f"  POI Count: {int(row['raw_poi_count'])}")

    # Step 7: Detailed explanation for one dwelling
    print_section_header("Step 7: Detailed Explanation for a Sample Dwelling...")
    sample_idx = final_df[final_df['linguistic_label'] == 'good'].index[0] \
        if len(final_df[final_df['linguistic_label'] == 'good']) > 0 else 0
    sample_row = final_df.iloc[sample_idx]
    sample_features = {
        'noise_lden': sample_row['noise_lden'],
        'noise_lnight': sample_row['noise_lnight'],
        'daylight': sample_row['daylight'],
        'view_sky': sample_row['view_sky'],
        'view_greenery': sample_row['view_greenery'],
        'location_poi': sample_row['location_poi']
    }
    explanation = fis.explain_dwelling(sample_features, top_n_rules=3)
    print(explanation)

    # Step 8: Save Results
    print_section_header("Step 8: Saving Results...")
    output_path = ROOT / 'results' / 'outputs' / 'fli_results.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")

    # Save summary report
    report_path = ROOT / 'results' / 'outputs' / 'summary_report.txt'
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT\n")
        f.write("Fuzzy Inference System Results\n")
        f.write("="*80 + "\n\n")
        f.write(f"Dataset: {len(final_df)} dwellings\n\n")
        f.write("FLI Score Statistics:\n")
        f.write(str(final_df['fli_score'].describe()) + "\n\n")
        f.write("Linguistic Label Distribution:\n")
        label_counts = final_df['linguistic_label'].value_counts()
        for label in ['excellent', 'good', 'fair', 'poor']:
            if label in label_counts.index:
                count = label_counts[label]
                percentage = (count / len(final_df)) * 100
                f.write(f"  {label.capitalize()}: {count} ({percentage:.1f}%)\n")
        f.write("\n" + "="*80 + "\n")
        f.write("Standards Applied:\n")
        f.write("="*80 + "\n")
        f.write("WHO 2018 Environmental Noise Guidelines:\n")
        f.write("  - Road traffic: Lden < 53 dB, Lnight < 45 dB\n")
        f.write("  - Railway: Lden < 54 dB, Lnight < 44 dB\n")
        f.write("  - Aircraft: Lden < 45 dB, Lnight < 40 dB\n\n")
        f.write("EN 17037 Daylight Provision:\n")
        f.write("  - Minimum: 300 lux (target), 100 lux (floor)\n")
        f.write("  - Medium: 500 lux (target), 300 lux (floor)\n")
        f.write("  - High: 750 lux (target), 500 lux (floor)\n")
    print(f"Summary report saved to: {report_path}")

    # Step 9: Generate visualizations (optional)
    if not args.no_viz:
        create_visualizations(final_df)
    else:
        print("\nSkipping visualizations (--no-viz flag set)")

    # Done
    print_section_header("ASSESSMENT COMPLETE!")
    print(f"\nOutput files:")
    print(f"  1. {output_path}")
    print(f"  2. {report_path}")
    if not args.no_viz:
        print(f"  3. {ROOT / 'results' / 'figures'}/*.png")


if __name__ == "__main__":
    main()
