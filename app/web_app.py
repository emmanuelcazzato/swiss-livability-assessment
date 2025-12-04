"""
Swiss Residential Perceived Livability Assessment - Web Interface - V2
A proof-of-concept web application for fuzzy livability assessment

V2 Changes:
- Daylight input now in klx (not lux)
- View variables use raw sr values (no scaling)
- POI uses log10 transformation
- Simplified alignment (no percentile-based scaling)
"""

from flask import Flask, render_template, request, jsonify, session
from flask_babel import Babel, gettext as _
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
from feature_alignment import FeatureAlignmentConfig, align_single_input
from assessment import (
    get_fli_label,
    get_fli_color,
    get_all_assessments,
    get_recommendations as get_assessment_recommendations
)

app = Flask(__name__, template_folder=str(APP_DIR / 'templates'))
app.config['SECRET_KEY'] = 'swiss-livability-2025'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'de', 'fr']

# Supported languages
LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Français'
}

# Initialize Babel
babel = Babel(app)

def get_locale():
    """Select locale based on user preference or browser settings."""
    # Check URL parameter first
    if 'lang' in request.args:
        lang = request.args.get('lang')
        if lang in LANGUAGES:
            session['lang'] = lang
            return lang
    # Check session
    if 'lang' in session:
        return session.get('lang')
    # Fall back to browser preference
    return request.accept_languages.best_match(LANGUAGES.keys(), default='en')

babel.init_app(app, locale_selector=get_locale)

@app.context_processor
def inject_locale():
    """Inject locale and language list into all templates."""
    return {
        'current_locale': get_locale(),
        'languages': LANGUAGES
    }

# Initialize fuzzy system
fuzzy_system = LiveabilityFuzzySystem()

# V2: Use default alignment config (simplified, no external file needed)
alignment_config = FeatureAlignmentConfig.get_default()
print("V2 Alignment config loaded (simplified defaults):")
print(f"  daylight_klx_cap: {alignment_config.daylight_klx_cap} klx")
print(f"  view_sky_max: {alignment_config.view_sky_max} sr")
print(f"  view_greenery_max: {alignment_config.view_greenery_max} sr")
print(f"  location_poi_log_max: {alignment_config.location_poi_log_max}")


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
    daylight_klx: float,
    view_sky_sr: float,
    view_greenery_sr: float,
    poi_count: int
) -> float:
    """
    Compute FLI score from raw user inputs (physical units) - V2.

    V2: Simplified alignment - direct pass-through for most features,
    only POI gets log10 transformation.

    Parameters:
        noise_lden_dba: Day noise level in dBA
        noise_lnight_dba: Night noise level in dBA
        daylight_klx: Daylight illuminance in klx (V2: user provides klx)
        view_sky_sr: Sky view in steradians (V2: raw value)
        view_greenery_sr: Greenery view in steradians (V2: raw value)
        poi_count: Number of POIs within 10-min walk

    Returns:
        FLI score (0-100)
    """
    # V2: Apply simplified alignment
    aligned = align_single_input(
        noise_lden=noise_lden_dba,
        noise_lnight=noise_lnight_dba,
        daylight_klx=daylight_klx,
        view_sky_sr=view_sky_sr,
        view_greenery_sr=view_greenery_sr,
        poi_count=poi_count,
        cfg=alignment_config
    )

    result = fuzzy_system.compute_single_dwelling(aligned)
    return result['fli_score']


# Load sample data
try:
    data_path = DATA_DIR / 'processed' / 'dwellings_full.csv'
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} dwellings from {data_path}")

    # Pre-compute FLI scores for all dwellings
    if df is not None and not df.empty:
        print("Computing FLI scores...")
        # Handle column naming compatibility for V2
        if 'daylight' not in df.columns and 'raw_daylight_klx' in df.columns:
            df['daylight'] = df['raw_daylight_klx']
        if 'view_sky' not in df.columns and 'raw_view_sky_sr' in df.columns:
            df['view_sky'] = df['raw_view_sky_sr']
        if 'view_greenery' not in df.columns and 'raw_view_greenery_sr' in df.columns:
            df['view_greenery'] = df['raw_view_greenery_sr']
        
        # Ensure we have location_poi (log10)
        if 'location_poi' not in df.columns and 'raw_poi_count' in df.columns:
            df['location_poi'] = np.log10(df['raw_poi_count'] + 1)

        # Compute FLI
        df['fli_score'] = df.apply(lambda row: compute_single_dwelling_fli(
            row['noise_lden'],
            row['noise_lnight'],
            row['daylight'],
            row['view_sky'],
            row['view_greenery'],
            row['location_poi']
        ), axis=1)
        print("FLI computation complete.")

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

@app.route('/filter')
def filter_page():
    """Filter dwellings page"""
    return render_template('filter.html')

@app.route('/api/dwellings/all')
def get_all_dwellings():
    """API endpoint to get all dwellings with FLI scores for filtering"""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500

    # Select relevant columns to minimize payload
    # Note: We rely on the pre-computed columns from load time
    cols = ['building_id', 'noise_lden', 'daylight', 'view_sky', 'view_greenery', 'location_poi', 'fli_score']
    
    # Add raw POI count if available for display
    if 'raw_poi_count' in df.columns:
        cols.append('raw_poi_count')
    
    # Ensure all columns exist
    available_cols = [c for c in cols if c in df.columns]
    
    # Replace NaN with None (null in JSON) or 0 to avoid JSON errors
    export_df = df[available_cols].fillna(0)
    
    data = export_df.to_dict('records')
    
    # Rename raw_poi_count to poi_count for frontend consistency
    for d in data:
        if 'raw_poi_count' in d:
            d['poi_count'] = int(d.pop('raw_poi_count'))
        elif 'location_poi' in d:
            # Fallback if raw count missing
            d['poi_count'] = int(10 ** d['location_poi'] - 1)
            
    return jsonify(data)

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
    API endpoint to assess a dwelling from user-provided raw inputs - V2.

    Expected input (physical units - V2):
        noise_lden: Day noise level in dBA
        noise_lnight: Night noise level in dBA
        daylight: Daylight illuminance in klx (V2: not lux!)
        view_sky: Sky view in steradians (raw, 0-0.13)
        view_greenery: Greenery view in steradians (raw, 0-0.06)
        poi_count: Number of POIs within 10-min walk

    The V2 alignment layer transforms POI to log10 scale.
    """
    try:
        data = request.json

        # Extract raw features (V2 physical units from user input)
        noise_lden = float(data.get('noise_lden', 55))
        noise_lnight = float(data.get('noise_lnight', 45))
        daylight_klx = float(data.get('daylight', 1.5))     # V2: klx, default ~median
        view_sky_sr = float(data.get('view_sky', 0.03))     # V2: sr, default ~median
        view_greenery_sr = float(data.get('view_greenery', 0.01))  # V2: sr, default ~median
        poi_count = int(data.get('poi_count', 200))         # Default ~median of real data

        # Compute FLI using V2 alignment
        fli_score = compute_fli_from_raw_inputs(
            noise_lden_dba=noise_lden,
            noise_lnight_dba=noise_lnight,
            daylight_klx=daylight_klx,
            view_sky_sr=view_sky_sr,
            view_greenery_sr=view_greenery_sr,
            poi_count=poi_count
        )

        # Use centralized assessment functions
        fli_label = get_fli_label(fli_score)
        color = get_fli_color(fli_label)

        # Get feature assessments using centralized thresholds
        raw_assessments = get_all_assessments(
            noise_lden=noise_lden,
            daylight_klx=daylight_klx,
            view_sky_sr=view_sky_sr,
            view_greenery_sr=view_greenery_sr,
            poi_count=poi_count
        )

        # Translate assessment labels for i18n
        assessments = {k: _(v) for k, v in raw_assessments.items()}

        # Get recommendations (in English) and translate
        raw_recommendations = get_assessment_recommendations(fli_score, raw_assessments)
        recommendations = [_(r) for r in raw_recommendations]

        return jsonify({
            'fli_score': round(fli_score, 2),
            'label': _(fli_label.capitalize()),
            'color': color,
            'assessments': assessments,
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/dwelling/<building_id>')
def get_dwelling_details(building_id):
    """
    API endpoint to get specific dwelling details - V2.

    Uses pre-aligned features from the processed dataframe.
    V2: Features use simplified alignment (klx, raw sr, log10 POI).
    """
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500

    try:
        import math
        dwelling = df[df['building_id'] == int(building_id)].iloc[0]

        # V2: Check column format and extract raw values
        if 'daylight' in dwelling.index and 'location_poi' in dwelling.index:
            # New V2 format: aligned features already in V2 units
            features = {
                'noise_lden': dwelling['noise_lden'],
                'noise_lnight': dwelling['noise_lnight'],
                'daylight': dwelling['daylight'],           # V2: klx
                'view_sky': dwelling['view_sky'],           # V2: raw sr
                'view_greenery': dwelling['view_greenery'], # V2: raw sr
                'location_poi': dwelling['location_poi']    # V2: log10
            }
            # Raw values for display
            raw_daylight_klx = dwelling.get('raw_daylight_klx', dwelling['daylight'])
            raw_view_sky = dwelling.get('raw_view_sky_sr', dwelling['view_sky'])
            raw_view_greenery = dwelling.get('raw_view_greenery_sr', dwelling['view_greenery'])
            raw_poi = dwelling.get('raw_poi_count', int(10 ** dwelling['location_poi'] - 1))
        else:
            # Old format: convert on the fly for V2 (backwards compatibility)
            raw_daylight_klx = dwelling.get('daylight_avg_klx', dwelling.get('raw_daylight_klx', 1.0))
            raw_view_sky = dwelling.get('raw_view_sky_sr', dwelling.get('view_sky', 0.03))
            raw_view_greenery = dwelling.get('raw_view_greenery_sr', dwelling.get('view_greenery', 0.01))
            raw_poi = int(dwelling.get('raw_poi_count', dwelling.get('location_poi_count', 100)))

            # V2 aligned features
            features = {
                'noise_lden': dwelling['noise_lden'],
                'noise_lnight': dwelling['noise_lnight'],
                'daylight': raw_daylight_klx,               # V2: klx
                'view_sky': raw_view_sky,                   # V2: raw sr
                'view_greenery': raw_view_greenery,         # V2: raw sr
                'location_poi': math.log10(raw_poi + 1)     # V2: log10
            }

        result = fuzzy_system.compute_single_dwelling(features)
        fli_score = result['fli_score']

        # Use centralized label function
        label = _(get_fli_label(fli_score).capitalize())

        return jsonify({
            'building_id': building_id,
            'fli_score': round(fli_score, 2),
            'label': label,
            'features': {
                # V2: Field names match form input IDs
                'noise_lden': round(dwelling['noise_lden'], 1),
                'noise_lnight': round(dwelling['noise_lnight'], 1),
                'daylight': round(raw_daylight_klx, 3),      # V2: klx
                'view_sky': round(raw_view_sky, 4),          # V2: raw sr
                'view_greenery': round(raw_view_greenery, 4), # V2: raw sr
                'poi_count': int(raw_poi)
            },
            'aligned_features': {
                'daylight': round(features['daylight'], 3),   # V2: klx
                'view_sky': round(features['view_sky'], 4),   # V2: raw sr
                'view_greenery': round(features['view_greenery'], 4), # V2: raw sr
                'location_poi': round(features['location_poi'], 2)   # V2: log10
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

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
