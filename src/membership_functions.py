"""
Fuzzy Membership Functions Module

Defines membership functions for linguistic variables based on:
- WHO 2018 Environmental Noise Guidelines
- EN 17037 Daylight Provision Standards
- Domain expert knowledge for views and location
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
        """Define the universe of discourse for each input/output variable."""
        # Noise (dBA) - typical range for urban environments
        self.universes['noise_lden'] = np.arange(30, 85, 0.5)
        self.universes['noise_lnight'] = np.arange(25, 75, 0.5)
        
        # Daylight (klx) - converted to lux for easier interpretation
        # Note: 1 klx = 1000 lux
        self.universes['daylight'] = np.arange(0, 1000, 5)  # in lux
        
        # View sky (solid angle in steradians)
        self.universes['view_sky'] = np.arange(0, 4, 0.05)
        
        # View greenery (solid angle in steradians)
        self.universes['view_greenery'] = np.arange(0, 2, 0.02)
        
        # Location POI count
        self.universes['location_poi'] = np.arange(0, 100, 1)
        
        # Output: Fuzzy Livability Index (0-100)
        self.universes['livability'] = np.arange(0, 101, 1)
    
    def _define_membership_functions(self):
        """Define membership functions for all linguistic variables."""
        # NOISE LDEN (based on WHO 2018 guidelines)
        # Quiet: < 53 dB, Moderate: 53-65 dB, Noisy: > 65 dB
        self.membership_functions['noise_lden'] = {
            'quiet': fuzz.trapmf(self.universes['noise_lden'], [30, 30, 48, 55]),
            'moderate': fuzz.trimf(self.universes['noise_lden'], [50, 58, 68]),
            'noisy': fuzz.trapmf(self.universes['noise_lden'], [63, 70, 85, 85])
        }
        
        # NOISE LNIGHT (based on WHO 2018 guidelines)
        # Quiet: < 45 dB, Moderate: 45-55 dB, Noisy: > 55 dB
        self.membership_functions['noise_lnight'] = {
            'quiet': fuzz.trapmf(self.universes['noise_lnight'], [25, 25, 40, 47]),
            'moderate': fuzz.trimf(self.universes['noise_lnight'], [42, 50, 58]),
            'noisy': fuzz.trapmf(self.universes['noise_lnight'], [53, 60, 75, 75])
        }
        
        # DAYLIGHT (based on EN 17037 standards)
        # Low: < 100 lux, Medium: 100-300 lux, High: > 300 lux
        self.membership_functions['daylight'] = {
            'low': fuzz.trapmf(self.universes['daylight'], [0, 0, 50, 120]),
            'medium': fuzz.trimf(self.universes['daylight'], [80, 200, 350]),
            'high': fuzz.trapmf(self.universes['daylight'], [280, 400, 1000, 1000])
        }
        
        # VIEW SKY (based on visual comfort research)
        # Poor: < 1.0 sr, Moderate: 1.0-2.0 sr, Good: > 2.0 sr
        self.membership_functions['view_sky'] = {
            'poor': fuzz.trapmf(self.universes['view_sky'], [0, 0, 0.5, 1.2]),
            'moderate': fuzz.trimf(self.universes['view_sky'], [0.8, 1.5, 2.3]),
            'good': fuzz.trapmf(self.universes['view_sky'], [2.0, 2.8, 4, 4])
        }
        
        # VIEW GREENERY
        # Poor: < 0.3 sr, Moderate: 0.3-0.8 sr, Good: > 0.8 sr
        self.membership_functions['view_greenery'] = {
            'poor': fuzz.trapmf(self.universes['view_greenery'], [0, 0, 0.1, 0.4]),
            'moderate': fuzz.trimf(self.universes['view_greenery'], [0.2, 0.6, 1.0]),
            'good': fuzz.trapmf(self.universes['view_greenery'], [0.7, 1.2, 2, 2])
        }
        
        # LOCATION POI COUNT
        # Low: < 10, Medium: 10-30, High: > 30
        self.membership_functions['location_poi'] = {
            'low': fuzz.trapmf(self.universes['location_poi'], [0, 0, 5, 15]),
            'medium': fuzz.trimf(self.universes['location_poi'], [10, 25, 40]),
            'high': fuzz.trapmf(self.universes['location_poi'], [35, 50, 100, 100])
        }
        
        # OUTPUT: LIVABILITY INDEX
        # Poor: 0-30, Fair: 20-50, Good: 40-70, Excellent: 60-100
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
            Standard thresholds from WHO 2018 and EN 17037
        """
        return {
            'WHO_2018_noise': {
                'road_traffic_lden': 53,
                'road_traffic_lnight': 45,
                'railway_lden': 54,
                'railway_lnight': 44,
                'aircraft_lden': 45,
                'aircraft_lnight': 40
            },
            'EN_17037_daylight': {
                'minimum_target': 300,  # lux
                'minimum_floor': 100,   # lux
                'medium_target': 500,   # lux
                'medium_floor': 300,    # lux
                'high_target': 750,     # lux
                'high_floor': 500       # lux
            }
        }


if __name__ == "__main__":
    # Example usage
    print("Fuzzy Membership Functions Module")
    print("="*60)
    
    # Create membership functions
    mf = FuzzyMembershipFunctions()
    
    # Display standard thresholds
    print("\nStandard Thresholds:")
    thresholds = mf.get_standard_thresholds()
    for standard, values in thresholds.items():
        print(f"\n{standard}:")
        for key, value in values.items():
            print(f"  {key}: {value}")
    
    # Example fuzzification
    print("\n" + "="*60)
    print("Example Fuzzification:")
    print("="*60)
    
    # Test noise fuzzification
    noise_value = 55  # dBA
    noise_memberships = mf.fuzzify_value('noise_lden', noise_value)
    print(f"\nNoise Lden = {noise_value} dBA:")
    for term, degree in noise_memberships.items():
        print(f"  {term}: {degree:.3f}")
    
    # Test daylight fuzzification
    daylight_value = 250  # lux
    daylight_memberships = mf.fuzzify_value('daylight', daylight_value)
    print(f"\nDaylight = {daylight_value} lux:")
    for term, degree in daylight_memberships.items():
        print(f"  {term}: {degree:.3f}")

