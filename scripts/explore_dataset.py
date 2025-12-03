import pandas as pd
import sys

# Load the dataset
print("Loading locations.csv...")
df = pd.read_csv('/home/ubuntu/swiss_livability/data/raw/locations.csv')

print(f"\nDataset shape: {df.shape}")
print(f"Number of dwellings: {len(df)}")
print(f"Number of features: {len(df.columns)}")

# Get column names
columns = df.columns.tolist()

# Look for relevant features
print("\n" + "="*80)
print("SEARCHING FOR RELEVANT FEATURES")
print("="*80)

# Noise-related columns
noise_cols = [col for col in columns if 'noise' in col.lower()]
print(f"\nNoise-related columns ({len(noise_cols)}):")
for col in noise_cols[:20]:  # Show first 20
    print(f"  - {col}")

# Daylight-related columns
daylight_cols = [col for col in columns if 'daylight' in col.lower() or 'sun' in col.lower() or 'illuminance' in col.lower()]
print(f"\nDaylight-related columns ({len(daylight_cols)}):")
for col in daylight_cols[:20]:
    print(f"  - {col}")

# View-related columns
view_cols = [col for col in columns if 'view' in col.lower() or 'sky' in col.lower()]
print(f"\nView-related columns ({len(view_cols)}):")
for col in view_cols[:20]:
    print(f"  - {col}")

# POI-related columns
poi_cols = [col for col in columns if 'walkshed' in col.lower() or 'poi' in col.lower()]
print(f"\nPOI/Accessibility columns ({len(poi_cols)}):")
print(f"  (Total: {len(poi_cols)} columns)")

# Sample the first few rows
print("\n" + "="*80)
print("SAMPLE DATA (first 3 rows, selected columns)")
print("="*80)

# Select a subset of columns to display
display_cols = ['building_id'] + noise_cols[:3] + daylight_cols[:3] + view_cols[:3]
display_cols = [col for col in display_cols if col in df.columns]

print(df[display_cols].head(3))

# Check for missing values
print("\n" + "="*80)
print("MISSING VALUES CHECK")
print("="*80)

missing_summary = df[display_cols].isnull().sum()
print(missing_summary[missing_summary > 0])

print("\nDataset exploration complete!")
