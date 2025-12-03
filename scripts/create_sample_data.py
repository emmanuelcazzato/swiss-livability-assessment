"""
Create sample simulation data for prototype development.
Since simulations.csv is too large, we'll create synthetic data based on realistic ranges.
"""

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Load locations to get building_ids
print("Loading locations.csv...")
locations_df = pd.read_csv('/home/ubuntu/swiss_livability/data/raw/locations.csv')

# Sample 500 dwellings for the prototype
n_sample = 500
sample_buildings = locations_df.sample(n=n_sample, random_state=42)

print(f"Creating synthetic simulation data for {n_sample} dwellings...")

# Create synthetic simulation data based on realistic ranges
simulations_data = {
    'building_id': sample_buildings['building_id'].values,
    
    # Noise data (dBA) - based on WHO 2018 guidelines
    # Lden: 30-80 dB, Lnight: 25-70 dB
    'window_noise_lden': np.random.normal(55, 8, n_sample).clip(30, 80),
    'window_noise_lnight': np.random.normal(47, 7, n_sample).clip(25, 70),
    
    # Daylight data (klx) - seasonal variations
    # Winter: lower, Summer: higher
    'window_daylight_winter': np.random.lognormal(np.log(0.15), 0.5, n_sample).clip(0.01, 1.0),
    'window_daylight_spring': np.random.lognormal(np.log(0.25), 0.5, n_sample).clip(0.05, 1.5),
    'window_daylight_summer': np.random.lognormal(np.log(0.35), 0.5, n_sample).clip(0.1, 2.0),
    'window_daylight_autumn': np.random.lognormal(np.log(0.20), 0.5, n_sample).clip(0.03, 1.2),
    
    # View data (solid angle in steradians)
    # Sky view: 0-4 sr, Greenery view: 0-2 sr
    'view_sky': np.random.gamma(2, 0.8, n_sample).clip(0, 4),
    'view_greenery': np.random.gamma(1.5, 0.4, n_sample).clip(0, 2),
}

simulations_df = pd.DataFrame(simulations_data)

# Calculate average daylight
simulations_df['daylight_avg_klx'] = simulations_df[[
    'window_daylight_winter', 'window_daylight_spring', 
    'window_daylight_summer', 'window_daylight_autumn'
]].mean(axis=1)

# Save to CSV
output_path = '/home/ubuntu/swiss_livability/data/processed/simulations_sample.csv'
simulations_df.to_csv(output_path, index=False)
print(f"Saved simulation data to: {output_path}")

# Display summary statistics
print("\n" + "="*80)
print("SIMULATION DATA SUMMARY")
print("="*80)
print(simulations_df.describe())

# Merge with locations to get POI data
print("\n" + "="*80)
print("MERGING WITH LOCATION DATA")
print("="*80)

# Get POI columns
poi_cols = [col for col in locations_df.columns if 'walkshed' in col]
print(f"Found {len(poi_cols)} POI columns")

# Select relevant location features
location_features = sample_buildings[['building_id'] + poi_cols[:50]]  # Use first 50 POI columns

# Calculate total POI count
poi_count = location_features[poi_cols[:50]].fillna(0).sum(axis=1)
location_features['location_poi_count'] = poi_count

# Merge
merged_df = simulations_df.merge(
    location_features[['building_id', 'location_poi_count']], 
    on='building_id'
)

# Save merged dataset
merged_path = '/home/ubuntu/swiss_livability/data/processed/dwellings_sample.csv'
merged_df.to_csv(merged_path, index=False)
print(f"Saved merged dataset to: {merged_path}")

print("\n" + "="*80)
print("MERGED DATASET SUMMARY")
print("="*80)
print(f"Shape: {merged_df.shape}")
print(f"\nColumns: {list(merged_df.columns)}")
print(f"\nFirst 5 rows:")
print(merged_df.head())

print("\n" + "="*80)
print("SAMPLE DATA CREATION COMPLETE!")
print("="*80)
print(f"Files created:")
print(f"  1. {output_path}")
print(f"  2. {merged_path}")

