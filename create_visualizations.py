"""
Create visualizations for the Fuzzy Livability Assessment results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load results
print("Loading results...")
df = pd.read_csv('/home/ubuntu/swiss_livability/results/outputs/fli_results.csv')

# Create output directory
import os
os.makedirs('/home/ubuntu/swiss_livability/results/figures', exist_ok=True)

# 1. FLI Score Distribution
print("Creating FLI score distribution plot...")
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df['fli_score'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
ax.axvline(df['fli_score'].mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {df["fli_score"].mean():.2f}')
ax.set_xlabel('Fuzzy Livability Index (FLI)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Distribution of Fuzzy Livability Index Scores', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/home/ubuntu/swiss_livability/results/figures/fli_distribution.png', dpi=300)
plt.close()

# 2. Linguistic Label Distribution
print("Creating linguistic label distribution plot...")
fig, ax = plt.subplots(figsize=(10, 6))
label_counts = df['linguistic_label'].value_counts()
colors = {'excellent': '#2ecc71', 'good': '#3498db', 'fair': '#f39c12', 'poor': '#e74c3c'}
label_colors = [colors.get(label, 'gray') for label in label_counts.index]
bars = ax.bar(range(len(label_counts)), label_counts.values, color=label_colors, edgecolor='black', alpha=0.8)
ax.set_xticks(range(len(label_counts)))
ax.set_xticklabels([label.capitalize() for label in label_counts.index], fontsize=11)
ax.set_ylabel('Number of Dwellings', fontsize=12)
ax.set_title('Distribution of Linguistic Livability Labels', fontsize=14, fontweight='bold')
# Add value labels on bars
for i, (bar, count) in enumerate(zip(bars, label_counts.values)):
    percentage = (count / len(df)) * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, 
            f'{count}\n({percentage:.1f}%)', ha='center', va='bottom', fontsize=10)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('/home/ubuntu/swiss_livability/results/figures/linguistic_labels.png', dpi=300)
plt.close()

# 3. Feature vs FLI Score Scatter Plots
print("Creating feature correlation plots...")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
features = [
    ('window_noise_lden', 'Noise Lden (dBA)'),
    ('window_noise_lnight', 'Noise Lnight (dBA)'),
    ('daylight_avg_klx', 'Daylight (klx)'),
    ('view_sky', 'View Sky (sr)'),
    ('view_greenery', 'View Greenery (sr)'),
    ('location_poi_count', 'POI Count')
]

for ax, (feature, label) in zip(axes.flat, features):
    scatter = ax.scatter(df[feature], df['fli_score'], c=df['fli_score'], 
                        cmap='RdYlGn', alpha=0.6, edgecolors='black', linewidth=0.5)
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel('FLI Score', fontsize=10)
    ax.set_title(f'FLI vs {label}', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add correlation coefficient
    corr = df[feature].corr(df['fli_score'])
    ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            verticalalignment='top', fontsize=9)

plt.tight_layout()
plt.savefig('/home/ubuntu/swiss_livability/results/figures/feature_correlations.png', dpi=300)
plt.close()

# 4. Box plot by linguistic label
print("Creating box plots by linguistic label...")
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for ax, (feature, label) in zip(axes.flat, features):
    df_plot = df[[feature, 'linguistic_label']].copy()
    # Order labels
    label_order = ['poor', 'fair', 'good', 'excellent']
    df_plot['linguistic_label'] = pd.Categorical(df_plot['linguistic_label'], categories=label_order, ordered=True)
    
    sns.boxplot(data=df_plot, x='linguistic_label', y=feature, ax=ax, 
                palette=colors, order=label_order)
    ax.set_xlabel('Livability Label', fontsize=10)
    ax.set_ylabel(label, fontsize=10)
    ax.set_title(f'{label} by Livability Label', fontsize=11, fontweight='bold')
    ax.set_xticklabels([l.capitalize() for l in label_order], rotation=0)
    ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/ubuntu/swiss_livability/results/figures/features_by_label.png', dpi=300)
plt.close()

# 5. Correlation heatmap
print("Creating correlation heatmap...")
fig, ax = plt.subplots(figsize=(10, 8))
feature_cols = [f[0] for f in features] + ['fli_score']
corr_matrix = df[feature_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
ax.set_title('Feature Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('/home/ubuntu/swiss_livability/results/figures/correlation_heatmap.png', dpi=300)
plt.close()

print("\nAll visualizations created successfully!")
print("Saved to: /home/ubuntu/swiss_livability/results/figures/")

