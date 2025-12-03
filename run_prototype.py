"""
Main Prototype Script for Swiss Residential Perceived Livability Assessment
Using Fuzzy Inference System and Computing with Words Framework
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Ensure src is importable via relative path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from data_processing import preprocess_features, get_feature_statistics
from fuzzy_system import LiveabilityFuzzySystem
from membership_functions import FuzzyMembershipFunctions
from rule_base import FuzzyRuleBase

def main():
    print("\n" + "="*80)
    print("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT")
    print("Fuzzy Inference System Prototype")
    print("="*80 + "\n")
    
    # Step 1: Load prepared full features
    print("Step 1: Loading prepared full-feature dataset...")
    data_path = ROOT / 'data' / 'processed' / 'dwellings_full.csv'
    if not data_path.exists():
        print(f"[Error] Missing dataset: {data_path}")
        print("Please run: python3 prepare_full_features.py")
        return
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} dwellings")
    print(f"Features: {list(df.columns)}")
    
    # Step 2: Prepare features for fuzzy system
    print("\n" + "="*80)
    print("Step 2: Preparing features for fuzzy inference...")
    print("="*80)
    
    # Create feature dataframe with proper naming
    # Note: daylight_avg is in klx here; FIS converts to lux internally when value < 10
    features_df = pd.DataFrame({
        'noise_lden': df['noise_lden'],
        'noise_lnight': df['noise_lnight'],
        'daylight_avg': df['daylight_avg_klx'],  # in klx
        'view_sky': df['view_sky'],
        'view_greenery': df['view_greenery'],
        'location_poi_count': df['location_poi_count']
    })
    
    # Display statistics
    print("\nFeature Statistics:")
    print(features_df.describe())
    
    # Step 3: Initialize Fuzzy Inference System
    print("\n" + "="*80)
    print("Step 3: Initializing Fuzzy Inference System...")
    print("="*80)
    
    fis = LiveabilityFuzzySystem()
    
    # Display rule base
    print("\nRule Base Summary:")
    rule_stats = fis.rule_base.get_rule_statistics()
    print(f"Total rules: {rule_stats['total_rules']}")
    print(f"Variables used: {', '.join(rule_stats['variables_used'])}")
    print(f"\nRules by consequent:")
    for consequent, count in rule_stats['rules_by_consequent'].items():
        print(f"  {consequent}: {count} rules")
    
    # Step 4: Compute Fuzzy Livability Index
    print("\n" + "="*80)
    print("Step 4: Computing Fuzzy Livability Index for all dwellings...")
    print("="*80)
    
    results_df = fis.compute_batch(features_df)
    
    # Merge results with original data
    final_df = pd.concat([df, results_df], axis=1)
    
    # Step 5: Analyze Results
    print("\n" + "="*80)
    print("Step 5: Analyzing Results...")
    print("="*80)
    
    print("\nFLI Score Distribution:")
    print(final_df['fli_score'].describe())
    
    print("\nLinguistic Label Distribution:")
    label_dist = final_df['linguistic_label'].value_counts()
    for label, count in label_dist.items():
        percentage = (count / len(final_df)) * 100
        print(f"  {label.capitalize()}: {count} ({percentage:.1f}%)")
    
    # Step 6: Example Explanations
    print("\n" + "="*80)
    print("Step 6: Example Dwelling Assessments...")
    print("="*80)
    
    # Find examples of each category
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
        print(f"  Daylight: {row['daylight_avg_klx']:.3f} klx ({row['daylight_avg_klx']*1000:.0f} lux)")
        print(f"  View Sky (p80): {row['view_sky']:.4f} sr")
        print(f"  View Greenery (p80): {row['view_greenery']:.4f} sr")
        print(f"  POI Count: {int(row['location_poi_count'])}")
    
    # Step 7: Detailed explanation for one dwelling
    print("\n" + "="*80)
    print("Step 7: Detailed Explanation for a Sample Dwelling...")
    print("="*80)
    
    # Pick a dwelling with good livability
    sample_idx = final_df[final_df['linguistic_label'] == 'good'].index[0] if len(final_df[final_df['linguistic_label'] == 'good']) > 0 else 0
    sample_row = final_df.iloc[sample_idx]
    
    sample_features = {
        'noise_lden': sample_row['noise_lden'],
        'noise_lnight': sample_row['noise_lnight'],
        'daylight': sample_row['daylight_avg_klx'] * 1000,  # Convert to lux
        'view_sky': sample_row['view_sky'],
        'view_greenery': sample_row['view_greenery'],
        'location_poi': sample_row['location_poi_count']
    }
    
    explanation = fis.explain_dwelling(sample_features, top_n_rules=3)
    print(explanation)
    
    # Step 8: Save Results
    print("\n" + "="*80)
    print("Step 8: Saving Results...")
    print("="*80)
    
    output_path = ROOT / 'results' / 'outputs' / 'fli_results.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")
    
    # Save summary report
    report_path = ROOT / 'results' / 'outputs' / 'summary_report.txt'
    with open(report_path, 'w') as f:
        f.write("="*80 + "\n")
        f.write("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT\n")
        f.write("Fuzzy Inference System - Prototype Results\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Dataset: {len(final_df)} dwellings\n\n")
        
        f.write("FLI Score Statistics:\n")
        f.write(str(final_df['fli_score'].describe()) + "\n\n")
        
        f.write("Linguistic Label Distribution:\n")
        for label, count in label_dist.items():
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
    
    print("\n" + "="*80)
    print("PROTOTYPE EXECUTION COMPLETE!")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  1. {output_path}")
    print(f"  2. {report_path}")
    print("\nNext steps:")
    print("  - Review the FLI scores and linguistic labels")
    print("  - Validate against external ratings (if available)")
    print("  - Adjust membership functions and rules as needed")
    print("  - Generate visualizations")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
