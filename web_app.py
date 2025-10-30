"""
Swiss Residential Perceived Livability Assessment - Web Interface
A proof-of-concept web application for fuzzy livability assessment
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
import sys

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'src'))

from fuzzy_system import LiveabilityFuzzySystem
from membership_functions import FuzzyMembershipFunctions
from rule_base import FuzzyRuleBase

app = Flask(__name__)
app.config['SECRET_KEY'] = 'swiss-livability-2025'

# Initialize fuzzy system
fuzzy_system = LiveabilityFuzzySystem()

def compute_single_dwelling_fli(noise_lden, noise_lnight, daylight, view_sky, view_greenery, poi_count):
    features = {
    'noise_lden': noise_lden,
    'noise_lnight': noise_lnight,
    'daylight': daylight * 1000,
    'view_sky': view_sky,
    'view_greenery': view_greenery,
    'location_poi': poi_count
}
    result = fuzzy_system.compute_single_dwelling(features)
    return result['fli_score']

                 
# Load sample data
try:
    df = pd.read_csv(os.path.join(current_dir, 'data/processed/dwellings_sample.csv'))
    print(f"Loaded {len(df)} dwellings from sample dataset")
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
        # Get summary statistics
        stats = {
            'total_dwellings': len(df),
            'avg_noise': round(df['window_noise_lden'].mean(), 1),
            'avg_daylight': round(df['daylight_avg_klx'].mean(), 1),
            'avg_view_sky': round(df['view_sky'].mean(), 2),
            'avg_view_greenery': round(df['view_greenery'].mean(), 2)
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
    
    # Get first 50 dwellings for display
    dwellings = df.head(50)[['building_id', 'window_noise_lden', 'daylight_avg_klx', 
                              'view_sky', 'view_greenery']].to_dict('records')
    return jsonify(dwellings)

@app.route('/api/assess', methods=['POST'])
def assess_dwelling():
    """API endpoint to assess a dwelling"""
    try:
        data = request.json
        
        # Extract features
        noise_lden = float(data.get('noise_lden', 55))
        noise_lnight = float(data.get('noise_lnight', 45))
        daylight = float(data.get('daylight', 300))
        view_sky = float(data.get('view_sky', 0.5))
        view_greenery = float(data.get('view_greenery', 0.3))
        poi_count = int(data.get('poi_count', 50))
        
        # Compute FLI
        fli_score = compute_single_dwelling_fli(
            noise_lden=noise_lden,
            noise_lnight=noise_lnight,
            daylight=daylight,
            view_sky=view_sky,
            view_greenery=view_greenery,
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
        
        # Get feature assessments
        assessments = {
            'noise': 'Quiet' if noise_lden < 53 else ('Moderate' if noise_lden < 65 else 'Noisy'),
            'daylight': 'High' if daylight > 300 else ('Medium' if daylight > 100 else 'Low'),
            'view_sky': 'Good' if view_sky > 0.8 else ('Moderate' if view_sky > 0.4 else 'Limited'),
            'view_greenery': 'Good' if view_greenery > 0.6 else ('Moderate' if view_greenery > 0.3 else 'Limited'),
            'location': 'Excellent' if poi_count > 80 else ('Good' if poi_count > 50 else 'Moderate')
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

@app.route('/api/dwelling/<building_id>')
def get_dwelling_details(building_id):
    """API endpoint to get specific dwelling details"""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    try:
        dwelling = df[df['building_id'] == building_id].iloc[0]
        
        # Compute FLI
        fli_score = fuzzy_system.compute_fli(
            noise_lden=dwelling['window_noise_lden'],
            noise_lnight=dwelling['window_noise_lnight'],
            daylight=dwelling['daylight_avg_klx'],
            view_sky=dwelling['view_sky'],
            view_greenery=dwelling['view_greenery'],
            poi_count=dwelling['poi_count']
        )
        
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
                'noise_lden': round(dwelling['window_noise_lden'], 1),
                'noise_lnight': round(dwelling['window_noise_lnight'], 1),
                'daylight': round(dwelling['daylight_avg_klx'], 1),
                'view_sky': round(dwelling['view_sky'], 2),
                'view_greenery': round(dwelling['view_greenery'], 2),
                'poi_count': int(dwelling['poi_count'])
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

if __name__ == '__main__':
    print("=" * 80)
    print("SWISS RESIDENTIAL PERCEIVED LIVABILITY ASSESSMENT")
    print("Web Interface - Proof of Concept")
    print("=" * 80)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5001)

