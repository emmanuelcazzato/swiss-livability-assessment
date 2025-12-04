"""
Swiss Residential Perceived Livability Assessment - Web Interface
A proof-of-concept web application for fuzzy livability assessment
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path

# Setup paths
APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
SRC_DIR = ROOT_DIR / 'src'
DATA_DIR = ROOT_DIR / 'data'

# Add src directory to path
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fuzzy_system import LiveabilityFuzzySystem
from membership_functions import FuzzyMembershipFunctions
from rule_base import FuzzyRuleBase
from feature_alignment import FeatureAlignmentConfig, align_single_input

app = Flask(__name__, template_folder=str(APP_DIR / 'templates'))
app.config['SECRET_KEY'] = 'swiss-livability-2025'

# Initialize fuzzy system
fuzzy_system = LiveabilityFuzzySystem()

# Load feature alignment configuration
alignment_config = None
try:
    config_path = DATA_DIR / 'processed' / 'feature_alignment.json'
    alignment_config = FeatureAlignmentConfig.from_json(config_path)
    print(f"Loaded alignment config from {config_path}")
    print(f"  view_sky_ref: {alignment_config.view_sky_ref:.6f} sr")
    print(f"  view_greenery_ref: {alignment_config.view_greenery_ref:.6f} sr")
    print(f"  poi_log_p01: {alignment_config.poi_log_p01:.3f}")
    print(f"  poi_log_p99: {alignment_config.poi_log_p99:.3f}")
except Exception as e:
    print(f"Warning: Could not load alignment config: {e}")
    print("  Web API will use raw input values without alignment.")
    print("  Run prepare_full_features.py to generate the config file.")


def compute_single_dwelling_fli(noise_lden, noise_lnight, daylight, view_sky, view_greenery, poi_count):
    """
    Compute FLI score for a single dwelling.

    Note: This function expects ALREADY ALIGNED feature values.
    For raw user inputs, use compute_fli_from_raw_inputs() instead.
    """
    features = {
        'noise_lden': noise_lden,
        'noise_lnight': noise_lnight,
        'daylight': daylight,
        'view_sky': view_sky,
        'view_greenery': view_greenery,
        'location_poi': poi_count
    }
    result = fuzzy_system.compute_single_dwelling(features)
    return result['fli_score']


def compute_fli_from_raw_inputs(
    noise_lden_dba: float,
    noise_lnight_dba: float,
    daylight_lux: float,
    view_sky_sr: float,
    view_greenery_sr: float,
    poi_count: int
) -> float:
    """
    Compute FLI score from raw user inputs (physical units).

    Applies feature alignment before passing to FIS.

    Parameters:
        noise_lden_dba: Day noise level in dBA
        noise_lnight_dba: Night noise level in dBA
        daylight_lux: Daylight illuminance in lux
        view_sky_sr: Sky view in steradians
        view_greenery_sr: Greenery view in steradians
        poi_count: Number of POIs within 10-min walk

    Returns:
        FLI score (0-100)
    """
    if alignment_config is not None:
        # Apply alignment transformation
        aligned = align_single_input(
            noise_lden=noise_lden_dba,
            noise_lnight=noise_lnight_dba,
            daylight_lux=daylight_lux,
            view_sky_sr=view_sky_sr,
            view_greenery_sr=view_greenery_sr,
            poi_count=poi_count,
            cfg=alignment_config
        )
    else:
        # Fallback: use values as-is with basic capping
        aligned = {
            'noise_lden': noise_lden_dba,
            'noise_lnight': noise_lnight_dba,
            'daylight': min(daylight_lux, 1000),
            'view_sky': min(view_sky_sr, 4.0),
            'view_greenery': min(view_greenery_sr, 2.0),
            'location_poi': min(poi_count, 100)
        }

    result = fuzzy_system.compute_single_dwelling(aligned)
    return result['fli_score']


# Load sample data
try:
    data_path = DATA_DIR / 'processed' / 'dwellings_full.csv'
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} dwellings from {data_path}")
except Exception as e:
    print(f"Error loading data: {e}")
    df = None

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/explore')
def explore():
    """Explore dwellings page"""
    if df is not None:
        # Get summary statistics - handle both old and new column formats
        daylight_col = 'raw_daylight_klx' if 'raw_daylight_klx' in df.columns else 'daylight_avg_klx'
        view_sky_col = 'raw_view_sky_sr' if 'raw_view_sky_sr' in df.columns else 'view_sky'
        view_greenery_col = 'raw_view_greenery_sr' if 'raw_view_greenery_sr' in df.columns else 'view_greenery'

        stats = {
            'total_dwellings': len(df),
            'avg_noise': round(df['noise_lden'].mean(), 1),
            'avg_daylight': round(df[daylight_col].mean(), 3),
            'avg_view_sky': round(df[view_sky_col].mean(), 4),
            'avg_view_greenery': round(df[view_greenery_col].mean(), 4)
        }
        return render_template('explore.html', stats=stats)
    return render_template('explore.html', stats=None)

@app.route('/assess')
def assess():
    """Assessment page"""
    return render_template('assess.html')

@app.route('/api/dwellings')
def get_dwellings():
    """API endpoint to get dwelling list"""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500

    # Handle both old and new column formats
    if 'raw_daylight_klx' in df.columns:
        # New format
        cols = ['building_id', 'noise_lden', 'raw_daylight_klx',
                'raw_view_sky_sr', 'raw_view_greenery_sr']
        dwellings = df.head(50)[cols].rename(columns={
            'raw_daylight_klx': 'daylight_klx',
            'raw_view_sky_sr': 'view_sky_sr',
            'raw_view_greenery_sr': 'view_greenery_sr'
        }).to_dict('records')
    else:
        # Old format (backwards compatibility)
        dwellings = df.head(50)[['building_id', 'noise_lden', 'daylight_avg_klx',
                                  'view_sky', 'view_greenery']].to_dict('records')
    return jsonify(dwellings)

@app.route('/api/assess', methods=['POST'])
def assess_dwelling():
    """
    API endpoint to assess a dwelling from user-provided raw inputs.

    Expected input (physical units):
        noise_lden: Day noise level in dBA
        noise_lnight: Night noise level in dBA
        daylight: Daylight illuminance in lux
        view_sky: Sky view in steradians (raw)
        view_greenery: Greenery view in steradians (raw)
        poi_count: Number of POIs within 10-min walk

    The alignment layer transforms these to FIS-compatible values.
    """
    try:
        data = request.json

        # Extract raw features (physical units from user input)
        noise_lden = float(data.get('noise_lden', 55))
        noise_lnight = float(data.get('noise_lnight', 45))
        daylight_lux = float(data.get('daylight', 300))
        view_sky_sr = float(data.get('view_sky', 0.01))  # Default ~median of real data
        view_greenery_sr = float(data.get('view_greenery', 0.01))  # Default ~median
        poi_count = int(data.get('poi_count', 200))  # Default ~median of real data

        # Compute FLI using alignment-aware function
        fli_score = compute_fli_from_raw_inputs(
            noise_lden_dba=noise_lden,
            noise_lnight_dba=noise_lnight,
            daylight_lux=daylight_lux,
            view_sky_sr=view_sky_sr,
            view_greenery_sr=view_greenery_sr,
            poi_count=poi_count
        )

        # Determine linguistic label
        if fli_score >= 65:
            label = "Excellent"
            color = "#10b981"  # green
        elif fli_score >= 45:
            label = "Good"
            color = "#3b82f6"  # blue
        elif fli_score >= 25:
            label = "Fair"
            color = "#f59e0b"  # orange
        else:
            label = "Poor"
            color = "#ef4444"  # red

        # Get feature assessments (using raw values for display)
        # Thresholds based on WHO/EN standards and data distribution
        assessments = {
            'noise': 'Quiet' if noise_lden < 53 else ('Moderate' if noise_lden < 65 else 'Noisy'),
            'daylight': 'High' if daylight_lux > 300 else ('Medium' if daylight_lux > 100 else 'Low'),
            'view_sky': get_view_assessment(view_sky_sr, 'sky'),
            'view_greenery': get_view_assessment(view_greenery_sr, 'greenery'),
            'location': get_poi_assessment(poi_count)
        }

        return jsonify({
            'fli_score': round(fli_score, 2),
            'label': label,
            'color': color,
            'assessments': assessments,
            'recommendations': get_recommendations(fli_score, assessments)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


def get_view_assessment(view_sr: float, view_type: str) -> str:
    """Get linguistic assessment for view based on data-driven thresholds."""
    if alignment_config is None:
        # Fallback to original thresholds
        if view_type == 'sky':
            return 'Good' if view_sr > 0.8 else ('Moderate' if view_sr > 0.4 else 'Limited')
        else:
            return 'Good' if view_sr > 0.6 else ('Moderate' if view_sr > 0.3 else 'Limited')

    # Use data-driven thresholds based on alignment config
    # Good: top 20% (> 75th percentile of typical values)
    # Moderate: 20-60% (between 40th and 75th percentile)
    # Limited: bottom 40%
    if view_type == 'sky':
        ref = alignment_config.view_sky_ref
        good_threshold = ref * 0.6  # ~75th percentile
        moderate_threshold = ref * 0.2  # ~40th percentile
    else:
        ref = alignment_config.view_greenery_ref
        good_threshold = ref * 0.6
        moderate_threshold = ref * 0.2

    if view_sr > good_threshold:
        return 'Good'
    elif view_sr > moderate_threshold:
        return 'Moderate'
    else:
        return 'Limited'


def get_poi_assessment(poi_count: int) -> str:
    """Get linguistic assessment for POI accessibility based on data distribution."""
    if alignment_config is None:
        return 'Excellent' if poi_count > 80 else ('Good' if poi_count > 50 else 'Moderate')

    # Use log-scale thresholds from alignment config
    import math
    poi_log = math.log1p(max(poi_count, 0))
    p01 = alignment_config.poi_log_p01
    p99 = alignment_config.poi_log_p99

    # Normalize to 0-100 scale
    normalized = 100 * (poi_log - p01) / (p99 - p01)

    if normalized >= 70:
        return 'Excellent'
    elif normalized >= 40:
        return 'Good'
    else:
        return 'Moderate'

@app.route('/api/dwelling/<building_id>')
def get_dwelling_details(building_id):
    """
    API endpoint to get specific dwelling details.

    Uses pre-aligned features from the processed dataframe.
    The dataframe contains both raw (raw_*) and aligned columns.
    """
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500

    try:
        dwelling = df[df['building_id'] == int(building_id)].iloc[0]

        # Check if we have the new aligned columns or old format
        if 'daylight' in dwelling.index and 'location_poi' in dwelling.index:
            # New format: use pre-aligned features
            features = {
                'noise_lden': dwelling['noise_lden'],
                'noise_lnight': dwelling['noise_lnight'],
                'daylight': dwelling['daylight'],
                'view_sky': dwelling['view_sky'],
                'view_greenery': dwelling['view_greenery'],
                'location_poi': dwelling['location_poi']
            }
            # Raw values for display
            raw_daylight_klx = dwelling.get('raw_daylight_klx', dwelling['daylight'] / 1000)
            raw_view_sky = dwelling.get('raw_view_sky_sr', dwelling['view_sky'])
            raw_view_greenery = dwelling.get('raw_view_greenery_sr', dwelling['view_greenery'])
            raw_poi = dwelling.get('raw_poi_count', dwelling['location_poi'])
        else:
            # Old format: convert on the fly (backwards compatibility)
            features = {
                'noise_lden': dwelling['noise_lden'],
                'noise_lnight': dwelling['noise_lnight'],
                'daylight': dwelling['daylight_avg_klx'] * 1000,  # Convert klx to lux
                'view_sky': dwelling['view_sky'],
                'view_greenery': dwelling['view_greenery'],
                'location_poi': dwelling['location_poi_count']
            }
            raw_daylight_klx = dwelling['daylight_avg_klx']
            raw_view_sky = dwelling['view_sky']
            raw_view_greenery = dwelling['view_greenery']
            raw_poi = dwelling['location_poi_count']

        result = fuzzy_system.compute_single_dwelling(features)
        fli_score = result['fli_score']

        # Determine label
        if fli_score >= 65:
            label = "Excellent"
        elif fli_score >= 45:
            label = "Good"
        elif fli_score >= 25:
            label = "Fair"
        else:
            label = "Poor"

        return jsonify({
            'building_id': building_id,
            'fli_score': round(fli_score, 2),
            'label': label,
            'features': {
                'noise_lden': round(dwelling['noise_lden'], 1),
                'noise_lnight': round(dwelling['noise_lnight'], 1),
                'daylight_klx': round(raw_daylight_klx, 3),
                'view_sky_sr': round(raw_view_sky, 4),
                'view_greenery_sr': round(raw_view_greenery, 4),
                'poi_count': int(raw_poi)
            },
            'aligned_features': {
                'daylight': round(features['daylight'], 1),
                'view_sky': round(features['view_sky'], 3),
                'view_greenery': round(features['view_greenery'], 3),
                'location_poi': round(features['location_poi'], 1)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def get_recommendations(fli_score, assessments):
    """Generate recommendations based on assessment"""
    recommendations = []
    
    if assessments['noise'] == 'Noisy':
        recommendations.append("Consider noise reduction measures (better windows, insulation)")
    
    if assessments['daylight'] == 'Low':
        recommendations.append("Improve natural lighting (larger windows, lighter colors)")
    
    if assessments['view_sky'] == 'Limited':
        recommendations.append("Limited sky view - consider higher floors or less obstructed locations")
    
    if assessments['view_greenery'] == 'Limited':
        recommendations.append("Add indoor plants or consider locations with more greenery")
    
    if fli_score >= 65:
        recommendations.append("Excellent livability! This dwelling meets high standards.")
    elif fli_score < 35:
        recommendations.append("Significant improvements needed for better livability")
    
    return recommendations

def main():
    """Entry point for the web application"""
    print("=" * 80)
    print("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT")
    print("Web Interface - Proof of Concept")
    print("=" * 80)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5001)


if __name__ == '__main__':
    main()
