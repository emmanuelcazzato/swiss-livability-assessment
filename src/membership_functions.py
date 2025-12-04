"""
Fuzzy Membership Functions Module - V2

Defines membership functions for linguistic variables based on:
- WHO 2018 Environmental Noise Guidelines (road traffic: Lden <53 dB, Lnight <45 dB)
- EN 17037 Daylight Provision Standards (as proxy, using klx units)
- Data-driven calibration for views (raw sr units matching Swiss Dwellings dataset)
- POI accessibility using log10 transformation to handle long-tail distribution

V2 Design Principles:
1. Health-first approach: noise remains strong factor but not absolute veto
2. Avoid redundant calculations: daylight and sky-view not hard-ANDed in rules
3. POI as conditional bonus: high accessibility only helps when health baseline is decent
4. Direct use of raw units for view variables (no scaling)
"""

import numpy as np
import skfuzzy as fuzz
from typing import Dict, Tuple


class FuzzyMembershipFunctions:
    """
    Class to define and manage fuzzy membership functions for livability assessment.
    """
    
    def __init__(self):
        """Initialize fuzzy membership functions for all dimensions."""
        self.universes = {}
        self.membership_functions = {}
        self._define_universes()
        self._define_membership_functions()
    
    def _define_universes(self):
        """
        Define the universe of discourse for each input/output variable.

        V2 Changes:
        - noise_lden: expanded to 20-80 dBA (WHO anchors at 53 dB)
        - noise_lnight: expanded to 10-72 dBA (WHO anchors at 45 dB)
        - daylight: now in klx (0-6) instead of lux
        - view_sky: raw sr units (0-0.13) matching dataset range
        - view_greenery: raw sr units (0-0.06) matching dataset range
        - location_poi: log10(count+1) scale (0-3.5)
        """
        # Noise (dBA) - WHO 2018 guidelines as anchor points
        self.universes['noise_lden'] = np.arange(20, 80.5, 0.5)
        self.universes['noise_lnight'] = np.arange(10, 72.5, 0.5)

        # Daylight (klx) - direct kilolux units, typical noon illuminance
        self.universes['daylight'] = np.arange(0, 6.05, 0.05)

        # View sky (solid angle in steradians) - raw units from dataset
        # Dataset range: 0-0.13 sr
        self.universes['view_sky'] = np.arange(0, 0.131, 0.001)

        # View greenery (solid angle in steradians) - raw units from dataset
        # Dataset range: 0-0.06 sr
        self.universes['view_greenery'] = np.arange(0, 0.0605, 0.0005)

        # Location POI - log10(count+1) to handle long-tail distribution
        # Dataset raw range: 3-2662, log10 range: ~0.6-3.43
        self.universes['location_poi'] = np.arange(0, 3.55, 0.05)

        # Output: Fuzzy Livability Index (0-100)
        self.universes['livability'] = np.arange(0, 101, 1)
    
    def _define_membership_functions(self):
        """
        Define membership functions for all linguistic variables.

        V2 Design: Parameters calibrated based on:
        - WHO 2018 noise guidelines (Lden 53 dB, Lnight 45 dB as anchors)
        - Dataset distribution percentiles for views
        - Log-scale POI to handle 3-2662 count range
        """
        # NOISE LDEN (WHO 2018: road traffic Lden < 53 dB recommended)
        # quiet: right boundary at WHO threshold (53 dB)
        # moderate: covers main density of dataset
        # noisy: upper quantile and extreme values
        self.membership_functions['noise_lden'] = {
            'quiet': fuzz.trapmf(self.universes['noise_lden'], [20, 20, 42, 53]),
            'moderate': fuzz.trimf(self.universes['noise_lden'], [48, 56, 65]),
            'noisy': fuzz.trapmf(self.universes['noise_lden'], [60, 68, 80, 80])
        }

        # NOISE LNIGHT (WHO 2018: road traffic Lnight < 45 dB recommended)
        # quiet: right boundary at WHO threshold (45 dB)
        # Night noise weighted higher for sleep quality
        self.membership_functions['noise_lnight'] = {
            'quiet': fuzz.trapmf(self.universes['noise_lnight'], [10, 10, 32, 45]),
            'moderate': fuzz.trimf(self.universes['noise_lnight'], [40, 48, 56]),
            'noisy': fuzz.trapmf(self.universes['noise_lnight'], [52, 60, 72, 72])
        }

        # DAYLIGHT (klx) - noon illuminance proxy
        # Note: EN 17037 compliance uses annual/coverage thresholds,
        # this is a relative daylight sufficiency proxy
        # Dataset range: 0-3.91 klx (typically 0.24-3.91)
        self.membership_functions['daylight'] = {
            'low': fuzz.trapmf(self.universes['daylight'], [0.0, 0.0, 0.3, 1.2]),
            'medium': fuzz.trimf(self.universes['daylight'], [0.8, 1.6, 2.3]),
            'high': fuzz.trapmf(self.universes['daylight'], [2.0, 2.7, 6.0, 6.0])
        }

        # VIEW SKY (sr) - raw steradians from dataset
        # Dataset range: 0-0.13 sr (median ~0.029, 95th pctl ~0.05)
        # Calibrated based on data distribution
        self.membership_functions['view_sky'] = {
            'poor': fuzz.trapmf(self.universes['view_sky'], [0.000, 0.000, 0.010, 0.020]),
            'moderate': fuzz.trimf(self.universes['view_sky'], [0.015, 0.030, 0.040]),
            'good': fuzz.trapmf(self.universes['view_sky'], [0.035, 0.050, 0.130, 0.130])
        }

        # VIEW GREENERY (sr) - raw steradians from dataset
        # Dataset range: 0-0.06 sr (median ~0.01, 95th pctl ~0.026)
        # Green view associated with stress recovery and wellbeing
        self.membership_functions['view_greenery'] = {
            'poor': fuzz.trapmf(self.universes['view_greenery'], [0.000, 0.000, 0.003, 0.006]),
            'moderate': fuzz.trimf(self.universes['view_greenery'], [0.004, 0.010, 0.016]),
            'good': fuzz.trapmf(self.universes['view_greenery'], [0.012, 0.025, 0.060, 0.060])
        }

        # LOCATION POI - log10(count+1) scale
        # Dataset raw range: 3-2662, log10 range: ~0.6-3.43
        # log10(40+1)=1.61, log10(110+1)=2.05, log10(500+1)=2.70
        # Reflects 15-minute city accessibility concept
        self.membership_functions['location_poi'] = {
            'low': fuzz.trapmf(self.universes['location_poi'], [0.0, 0.0, 1.60, 2.05]),      # ~0-110 POIs
            'medium': fuzz.trimf(self.universes['location_poi'], [1.90, 2.35, 2.90]),        # ~80-800 POIs
            'high': fuzz.trapmf(self.universes['location_poi'], [2.70, 3.05, 3.50, 3.50])    # ~500+ POIs
        }

        # OUTPUT: LIVABILITY INDEX (unchanged from V1)
        # Poor: 0-35, Fair: 25-55, Good: 45-75, Excellent: 65-100
        self.membership_functions['livability'] = {
            'poor': fuzz.trapmf(self.universes['livability'], [0, 0, 15, 35]),
            'fair': fuzz.trimf(self.universes['livability'], [25, 40, 55]),
            'good': fuzz.trimf(self.universes['livability'], [45, 60, 75]),
            'excellent': fuzz.trapmf(self.universes['livability'], [65, 80, 100, 100])
        }
    
    def get_universe(self, variable: str) -> np.ndarray:
        """
        Get the universe of discourse for a variable.
        
        Parameters:
        -----------
        variable : str
            Variable name
            
        Returns:
        --------
        np.ndarray
            Universe of discourse
        """
        return self.universes.get(variable, None)
    
    def get_membership_function(self, variable: str, term: str) -> np.ndarray:
        """
        Get a specific membership function.
        
        Parameters:
        -----------
        variable : str
            Variable name (e.g., 'noise_lden')
        term : str
            Linguistic term (e.g., 'quiet')
            
        Returns:
        --------
        np.ndarray
            Membership function values
        """
        if variable in self.membership_functions:
            return self.membership_functions[variable].get(term, None)
        return None
    
    def get_all_membership_functions(self, variable: str) -> Dict[str, np.ndarray]:
        """
        Get all membership functions for a variable.
        
        Parameters:
        -----------
        variable : str
            Variable name
            
        Returns:
        --------
        Dict[str, np.ndarray]
            Dictionary of membership functions
        """
        return self.membership_functions.get(variable, {})
    
    def fuzzify_value(self, variable: str, value: float) -> Dict[str, float]:
        """
        Fuzzify a crisp input value.
        
        Parameters:
        -----------
        variable : str
            Variable name
        value : float
            Crisp input value
            
        Returns:
        --------
        Dict[str, float]
            Membership degrees for each linguistic term
        """
        if variable not in self.membership_functions:
            return {}
        
        memberships = {}
        for term, mf in self.membership_functions[variable].items():
            # Interpolate membership degree for the given value
            memberships[term] = fuzz.interp_membership(
                self.universes[variable], mf, value
            )
        
        return memberships
    
    def get_standard_thresholds(self) -> Dict[str, Dict[str, float]]:
        """
        Get the standard thresholds used for membership function design.

        Returns:
        --------
        Dict[str, Dict[str, float]]
            Standard thresholds from WHO 2018, EN 17037, and data-driven calibration
        """
        return {
            'WHO_2018_noise': {
                'road_traffic_lden': 53,    # dBA - used as quiet/moderate boundary
                'road_traffic_lnight': 45,  # dBA - used as quiet/moderate boundary
                'railway_lden': 54,
                'railway_lnight': 44,
                'aircraft_lden': 45,
                'aircraft_lnight': 40
            },
            'EN_17037_daylight_reference': {
                # Note: EN 17037 uses annual/coverage thresholds, not single-point illuminance
                # These are reference values; our MFs use klx proxy from noon simulation
                'minimum_target': 300,  # lux
                'minimum_floor': 100,   # lux
                'medium_target': 500,   # lux
                'high_target': 750,     # lux
            },
            'V2_data_driven_view': {
                # Calibrated from Swiss Dwellings v3.0.0 dataset
                'view_sky_median': 0.029,      # sr
                'view_sky_95th_pctl': 0.050,   # sr
                'view_greenery_median': 0.010, # sr
                'view_greenery_95th_pctl': 0.026,  # sr
            },
            'V2_poi_log_anchors': {
                # log10(count+1) reference points
                'low_upper': 2.05,   # ~110 POIs
                'medium_center': 2.35,  # ~220 POIs
                'high_lower': 2.70,  # ~500 POIs
            }
        }


if __name__ == "__main__":
    # Example usage - V2
    print("Fuzzy Membership Functions Module - V2")
    print("=" * 60)

    # Create membership functions
    mf = FuzzyMembershipFunctions()

    # Display standard thresholds
    print("\nStandard Thresholds:")
    thresholds = mf.get_standard_thresholds()
    for standard, values in thresholds.items():
        print(f"\n{standard}:")
        for key, value in values.items():
            print(f"  {key}: {value}")

    # Example fuzzification with V2 units
    print("\n" + "=" * 60)
    print("Example Fuzzification (V2 Units):")
    print("=" * 60)

    # Test noise fuzzification
    noise_value = 55  # dBA
    noise_memberships = mf.fuzzify_value('noise_lden', noise_value)
    print(f"\nNoise Lden = {noise_value} dBA:")
    for term, degree in noise_memberships.items():
        print(f"  {term}: {degree:.3f}")

    # Test daylight fuzzification (now in klx)
    daylight_value = 1.5  # klx (= 1500 lux)
    daylight_memberships = mf.fuzzify_value('daylight', daylight_value)
    print(f"\nDaylight = {daylight_value} klx:")
    for term, degree in daylight_memberships.items():
        print(f"  {term}: {degree:.3f}")

    # Test view_sky fuzzification (raw sr)
    view_sky_value = 0.03  # sr (typical median)
    view_sky_memberships = mf.fuzzify_value('view_sky', view_sky_value)
    print(f"\nView Sky = {view_sky_value} sr:")
    for term, degree in view_sky_memberships.items():
        print(f"  {term}: {degree:.3f}")

    # Test POI fuzzification (log10 scale)
    import math
    poi_count = 200  # raw count
    poi_log = math.log10(poi_count + 1)  # ~2.30
    poi_memberships = mf.fuzzify_value('location_poi', poi_log)
    print(f"\nLocation POI = {poi_count} count (log10={poi_log:.2f}):")
    for term, degree in poi_memberships.items():
        print(f"  {term}: {degree:.3f}")

