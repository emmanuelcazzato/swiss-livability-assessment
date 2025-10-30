"""
Data Processing Module for Swiss Dwellings Livability Assessment

This module handles loading, cleaning, and preprocessing of the Swiss Dwellings dataset.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


def load_swiss_dwellings(filepath: str) -> pd.DataFrame:
    """
    Load the Swiss Dwellings dataset from CSV file.
    
    Parameters:
    -----------
    filepath : str
        Path to the Swiss Dwellings CSV file
        
    Returns:
    --------
    pd.DataFrame
        Loaded dataset
    """
    print(f"Loading Swiss Dwellings dataset from: {filepath}")
    df = pd.read_csv(filepath)
    print(f"Dataset loaded: {len(df)} dwellings, {len(df.columns)} features")
    return df


def identify_relevant_features(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Identify relevant feature columns for each livability dimension.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Swiss Dwellings dataset
        
    Returns:
    --------
    Dict[str, List[str]]
        Dictionary mapping dimensions to column names
    """
    features = {
        'noise': [],
        'daylight': [],
        'view': [],
        'location': []
    }
    
    # Identify noise-related columns
    noise_keywords = ['noise', 'lden', 'lnight', 'acoustic']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in noise_keywords):
            features['noise'].append(col)
    
    # Identify daylight-related columns
    daylight_keywords = ['daylight', 'sun', 'illuminance', 'lux']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in daylight_keywords):
            features['daylight'].append(col)
    
    # Identify view-related columns
    view_keywords = ['view', 'sky', 'greenery', 'landscape']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in view_keywords):
            features['view'].append(col)
    
    # Identify location-related columns
    location_keywords = ['poi', 'distance', 'accessibility', 'amenity']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in location_keywords):
            features['location'].append(col)
    
    return features


def extract_core_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract and prepare core features for fuzzy inference.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Swiss Dwellings dataset
        
    Returns:
    --------
    pd.DataFrame
        Dataset with extracted core features
    """
    print("Extracting core features...")
    
    # Create a new dataframe with core features
    core_df = pd.DataFrame()
    
    # Noise features (dBA)
    if 'window_noise_lden' in df.columns:
        core_df['noise_lden'] = df['window_noise_lden']
    if 'window_noise_lnight' in df.columns:
        core_df['noise_lnight'] = df['window_noise_lnight']
    
    # Daylight features (convert klx to lux if needed)
    daylight_cols = [col for col in df.columns if 'daylight' in col.lower()]
    if daylight_cols:
        # Use average daylight across seasons as a representative measure
        daylight_values = df[daylight_cols].mean(axis=1)
        core_df['daylight_avg'] = daylight_values
    
    # View features (solid angle in sr)
    if 'view_sky' in df.columns:
        core_df['view_sky'] = df['view_sky']
    if 'view_greenery' in df.columns:
        core_df['view_greenery'] = df['view_greenery']
    
    # Location features (POI accessibility)
    poi_cols = [col for col in df.columns if 'poi' in col.lower()]
    if poi_cols:
        # Aggregate POI counts as a location convenience measure
        core_df['location_poi_count'] = df[poi_cols].sum(axis=1)
    
    print(f"Core features extracted: {list(core_df.columns)}")
    return core_df


def handle_missing_values(df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset with potential missing values
    strategy : str
        Strategy for handling missing values ('median', 'mean', 'drop')
        
    Returns:
    --------
    pd.DataFrame
        Dataset with missing values handled
    """
    print(f"Handling missing values using strategy: {strategy}")
    
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        print(f"Missing values found:")
        for col, count in missing_counts[missing_counts > 0].items():
            print(f"  {col}: {count} ({count/len(df)*100:.2f}%)")
    
    if strategy == 'median':
        df = df.fillna(df.median())
    elif strategy == 'mean':
        df = df.fillna(df.mean())
    elif strategy == 'drop':
        df = df.dropna()
    
    print(f"Dataset size after handling missing values: {len(df)} dwellings")
    return df


def normalize_features(df: pd.DataFrame, method: str = 'minmax') -> pd.DataFrame:
    """
    Normalize features for consistent scaling (optional, for visualization).
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset to normalize
    method : str
        Normalization method ('minmax' or 'zscore')
        
    Returns:
    --------
    pd.DataFrame
        Normalized dataset
    """
    df_normalized = df.copy()
    
    if method == 'minmax':
        for col in df.columns:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_normalized[col] = (df[col] - min_val) / (max_val - min_val)
    elif method == 'zscore':
        for col in df.columns:
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                df_normalized[col] = (df[col] - mean_val) / std_val
    
    return df_normalized


def preprocess_features(df: pd.DataFrame, handle_missing: bool = True) -> pd.DataFrame:
    """
    Complete preprocessing pipeline for Swiss Dwellings dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw Swiss Dwellings dataset
    handle_missing : bool
        Whether to handle missing values
        
    Returns:
    --------
    pd.DataFrame
        Preprocessed dataset ready for fuzzy inference
    """
    print("\n" + "="*60)
    print("PREPROCESSING SWISS DWELLINGS DATASET")
    print("="*60 + "\n")
    
    # Extract core features
    core_df = extract_core_features(df)
    
    # Handle missing values
    if handle_missing:
        core_df = handle_missing_values(core_df, strategy='median')
    
    # Display summary statistics
    print("\nSummary Statistics:")
    print(core_df.describe())
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE")
    print("="*60 + "\n")
    
    return core_df


def get_feature_statistics(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate statistics for each feature to inform fuzzy membership function design.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Preprocessed dataset
        
    Returns:
    --------
    Dict[str, Dict[str, float]]
        Statistics for each feature (min, max, mean, median, std, quartiles)
    """
    stats = {}
    
    for col in df.columns:
        stats[col] = {
            'min': df[col].min(),
            'max': df[col].max(),
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'q25': df[col].quantile(0.25),
            'q50': df[col].quantile(0.50),
            'q75': df[col].quantile(0.75)
        }
    
    return stats


if __name__ == "__main__":
    # Example usage
    print("Data Processing Module for Swiss Dwellings Livability Assessment")
    print("This module should be imported and used with actual dataset.")

