"""
Validation Module

Validates the Fuzzy Livability Index against external benchmarks
and performs statistical analysis.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import seaborn as sns


def validate_against_ratings(fli_scores: pd.DataFrame,
                            ratings_filepath: str,
                            merge_key: str = 'dwelling_id') -> Dict:
    """
    Validate FLI scores against external expert ratings.
    
    Parameters:
    -----------
    fli_scores : pd.DataFrame
        DataFrame with FLI scores
    ratings_filepath : str
        Path to external ratings CSV file
    merge_key : str
        Column name to merge on
        
    Returns:
    --------
    Dict
        Validation results including correlation and statistics
    """
    print("\n" + "="*80)
    print("VALIDATION AGAINST EXTERNAL RATINGS")
    print("="*80 + "\n")
    
    # Load external ratings
    try:
        ratings_df = pd.read_csv(ratings_filepath)
        print(f"External ratings loaded: {len(ratings_df)} records")
    except FileNotFoundError:
        print(f"Warning: Ratings file not found at {ratings_filepath}")
        return {}
    
    # Merge FLI scores with ratings
    merged_df = fli_scores.merge(ratings_df, on=merge_key, how='inner')
    print(f"Merged dataset: {len(merged_df)} dwellings with both FLI and ratings")
    
    if len(merged_df) == 0:
        print("No matching records found for validation")
        return {}
    
    # Assume ratings column is named 'rating' or similar
    rating_col = None
    for col in merged_df.columns:
        if 'rating' in col.lower() or 'score' in col.lower():
            rating_col = col
            break
    
    if rating_col is None:
        print("Warning: Could not find rating column in external data")
        return {}
    
    # Calculate correlations
    pearson_corr, pearson_p = stats.pearsonr(
        merged_df['fli_score'], 
        merged_df[rating_col]
    )
    
    spearman_corr, spearman_p = stats.spearmanr(
        merged_df['fli_score'],
        merged_df[rating_col]
    )
    
    # Calculate RMSE
    rmse = np.sqrt(np.mean((merged_df['fli_score'] - merged_df[rating_col])**2))
    
    # Calculate MAE
    mae = np.mean(np.abs(merged_df['fli_score'] - merged_df[rating_col]))
    
    results = {
        'n_samples': len(merged_df),
        'pearson_correlation': pearson_corr,
        'pearson_p_value': pearson_p,
        'spearman_correlation': spearman_corr,
        'spearman_p_value': spearman_p,
        'rmse': rmse,
        'mae': mae,
        'fli_mean': merged_df['fli_score'].mean(),
        'fli_std': merged_df['fli_score'].std(),
        'rating_mean': merged_df[rating_col].mean(),
        'rating_std': merged_df[rating_col].std()
    }
    
    # Print results
    print("\nValidation Results:")
    print("-"*80)
    print(f"Sample size: {results['n_samples']}")
    print(f"\nPearson correlation: {results['pearson_correlation']:.4f} (p={results['pearson_p_value']:.4e})")
    print(f"Spearman correlation: {results['spearman_correlation']:.4f} (p={results['spearman_p_value']:.4e})")
    print(f"\nRMSE: {results['rmse']:.2f}")
    print(f"MAE: {results['mae']:.2f}")
    print(f"\nFLI Score - Mean: {results['fli_mean']:.2f}, Std: {results['fli_std']:.2f}")
    print(f"External Rating - Mean: {results['rating_mean']:.2f}, Std: {results['rating_std']:.2f}")
    
    # Interpretation
    print("\n" + "-"*80)
    print("Interpretation:")
    if results['pearson_p_value'] < 0.001:
        significance = "highly significant (p < 0.001)"
    elif results['pearson_p_value'] < 0.01:
        significance = "very significant (p < 0.01)"
    elif results['pearson_p_value'] < 0.05:
        significance = "significant (p < 0.05)"
    else:
        significance = "not significant (p >= 0.05)"
    
    print(f"The correlation is {significance}")
    
    if abs(results['pearson_correlation']) > 0.7:
        strength = "strong"
    elif abs(results['pearson_correlation']) > 0.5:
        strength = "moderate"
    elif abs(results['pearson_correlation']) > 0.3:
        strength = "weak"
    else:
        strength = "very weak"
    
    print(f"The correlation strength is {strength}")
    
    print("="*80 + "\n")
    
    return results


def perform_sensitivity_analysis(fis, base_features: Dict[str, float],
                                 variable: str, value_range: Tuple[float, float],
                                 n_steps: int = 20) -> pd.DataFrame:
    """
    Perform sensitivity analysis by varying one input variable.
    
    Parameters:
    -----------
    fis : LiveabilityFuzzySystem
        Fuzzy inference system instance
    base_features : Dict[str, float]
        Base feature values
    variable : str
        Variable to vary
    value_range : Tuple[float, float]
        (min, max) range for the variable
    n_steps : int
        Number of steps in the range
        
    Returns:
    --------
    pd.DataFrame
        Sensitivity analysis results
    """
    from fuzzy_system import LiveabilityFuzzySystem
    
    print(f"\nPerforming sensitivity analysis for: {variable}")
    print(f"Range: {value_range[0]} to {value_range[1]}")
    
    values = np.linspace(value_range[0], value_range[1], n_steps)
    results = []
    
    for value in values:
        features = base_features.copy()
        features[variable] = value
        
        result = fis.compute_single_dwelling(features)
        
        results.append({
            variable: value,
            'fli_score': result['fli_score'],
            'linguistic_label': result['linguistic_label']
        })
    
    results_df = pd.DataFrame(results)
    
    print(f"FLI range: {results_df['fli_score'].min():.2f} to {results_df['fli_score'].max():.2f}")
    print(f"FLI change: {results_df['fli_score'].max() - results_df['fli_score'].min():.2f}")
    
    return results_df


def analyze_spatial_distribution(fli_scores: pd.DataFrame,
                                 coordinates_df: pd.DataFrame = None) -> Dict:
    """
    Analyze spatial distribution of FLI scores.
    
    Parameters:
    -----------
    fli_scores : pd.DataFrame
        DataFrame with FLI scores
    coordinates_df : pd.DataFrame
        DataFrame with spatial coordinates (optional)
        
    Returns:
    --------
    Dict
        Spatial analysis results
    """
    print("\n" + "="*80)
    print("SPATIAL DISTRIBUTION ANALYSIS")
    print("="*80 + "\n")
    
    # Basic statistics by linguistic label
    label_stats = fli_scores.groupby('linguistic_label')['fli_score'].agg([
        'count', 'mean', 'std', 'min', 'max'
    ])
    
    print("FLI Statistics by Linguistic Label:")
    print(label_stats)
    
    # Calculate percentiles
    percentiles = [10, 25, 50, 75, 90]
    percentile_values = fli_scores['fli_score'].quantile([p/100 for p in percentiles])
    
    print(f"\nFLI Score Percentiles:")
    for p, value in zip(percentiles, percentile_values):
        print(f"  {p}th percentile: {value:.2f}")
    
    results = {
        'label_statistics': label_stats.to_dict(),
        'percentiles': {p: v for p, v in zip(percentiles, percentile_values)}
    }
    
    print("="*80 + "\n")
    
    return results


def generate_validation_report(fli_scores: pd.DataFrame,
                              validation_results: Dict,
                              output_path: str):
    """
    Generate a comprehensive validation report.
    
    Parameters:
    -----------
    fli_scores : pd.DataFrame
        DataFrame with FLI scores
    validation_results : Dict
        Validation results from validate_against_ratings
    output_path : str
        Path to save the report
    """
    report = []
    report.append("="*80)
    report.append("FUZZY LIVABILITY INDEX - VALIDATION REPORT")
    report.append("="*80)
    report.append("")
    
    # Dataset summary
    report.append("1. DATASET SUMMARY")
    report.append("-"*80)
    report.append(f"Total dwellings assessed: {len(fli_scores)}")
    report.append(f"FLI Score Range: {fli_scores['fli_score'].min():.2f} - {fli_scores['fli_score'].max():.2f}")
    report.append(f"Mean FLI Score: {fli_scores['fli_score'].mean():.2f}")
    report.append(f"Std FLI Score: {fli_scores['fli_score'].std():.2f}")
    report.append("")
    
    # Distribution by label
    report.append("Distribution by Linguistic Label:")
    label_counts = fli_scores['linguistic_label'].value_counts()
    for label, count in label_counts.items():
        percentage = (count / len(fli_scores)) * 100
        report.append(f"  {label}: {count} ({percentage:.1f}%)")
    report.append("")
    
    # Validation results
    if validation_results:
        report.append("2. VALIDATION AGAINST EXTERNAL RATINGS")
        report.append("-"*80)
        report.append(f"Sample size: {validation_results['n_samples']}")
        report.append(f"Pearson correlation: {validation_results['pearson_correlation']:.4f}")
        report.append(f"  p-value: {validation_results['pearson_p_value']:.4e}")
        report.append(f"Spearman correlation: {validation_results['spearman_correlation']:.4f}")
        report.append(f"  p-value: {validation_results['spearman_p_value']:.4e}")
        report.append(f"RMSE: {validation_results['rmse']:.2f}")
        report.append(f"MAE: {validation_results['mae']:.2f}")
        report.append("")
    
    # Save report
    report_text = "\n".join(report)
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"Validation report saved to: {output_path}")
    return report_text


if __name__ == "__main__":
    print("Validation Module for Fuzzy Livability Assessment")
    print("This module should be used with actual FLI scores and external ratings.")

