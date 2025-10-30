"""
Fuzzy Inference System Module

Implements the Mamdani fuzzy inference system for livability assessment
using the Computing with Words framework.
"""

import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, List, Tuple
from membership_functions import FuzzyMembershipFunctions
from rule_base import FuzzyRuleBase


class LiveabilityFuzzySystem:
    """
    Mamdani Fuzzy Inference System for assessing residential livability.
    """
    
    def __init__(self):
        """Initialize the fuzzy inference system."""
        self.mf = FuzzyMembershipFunctions()
        self.rule_base = FuzzyRuleBase()
        print("Livability Fuzzy Inference System initialized")
    
    def compute_single_dwelling(self, features: Dict[str, float]) -> Dict:
        """
        Compute fuzzy livability index for a single dwelling.
        
        Parameters:
        -----------
        features : Dict[str, float]
            Dictionary of feature values for the dwelling
            
        Returns:
        --------
        Dict
            Results including FLI score and intermediate values
        """
        # Fuzzify inputs
        fuzzified = {}
        for var, value in features.items():
            if var in self.mf.membership_functions:
                fuzzified[var] = self.mf.fuzzify_value(var, value)
        
        # Apply fuzzy rules and aggregate
        activated_rules = []
        output_aggregation = {
            'poor': 0.0,
            'fair': 0.0,
            'good': 0.0,
            'excellent': 0.0
        }
        
        for rule in self.rule_base.get_rules():
            # Calculate rule activation strength (minimum of antecedents)
            activation_degrees = []
            
            for var, term in rule['antecedents'].items():
                if var in fuzzified and term in fuzzified[var]:
                    activation_degrees.append(fuzzified[var][term])
            
            if activation_degrees:
                # Use minimum (AND operation in fuzzy logic)
                activation = min(activation_degrees) * rule['weight']
                
                # Apply to consequent
                consequent_term = rule['consequent']['livability']
                output_aggregation[consequent_term] = max(
                    output_aggregation[consequent_term],
                    activation
                )
                
                if activation > 0.01:  # Only track significantly activated rules
                    activated_rules.append({
                        'rule_id': rule['id'],
                        'description': rule['description'],
                        'activation': activation
                    })
        
        # Defuzzification using centroid method
        fli_score = self._defuzzify_centroid(output_aggregation)
        
        # Determine linguistic label
        linguistic_label = self._get_linguistic_label(fli_score)
        
        return {
            'fli_score': fli_score,
            'linguistic_label': linguistic_label,
            'output_memberships': output_aggregation,
            'activated_rules': activated_rules,
            'input_fuzzification': fuzzified
        }
    
    def _defuzzify_centroid(self, output_memberships: Dict[str, float]) -> float:
        """
        Defuzzify using centroid method.
        
        Parameters:
        -----------
        output_memberships : Dict[str, float]
            Membership degrees for output linguistic terms
            
        Returns:
        --------
        float
            Defuzzified FLI score (0-100)
        """
        universe = self.mf.get_universe('livability')
        
        # Aggregate membership functions
        aggregated = np.zeros_like(universe, dtype=float)
        
        for term, activation in output_memberships.items():
            if activation > 0:
                mf = self.mf.get_membership_function('livability', term)
                # Clip membership function at activation level
                clipped = np.fmin(activation, mf)
                aggregated = np.fmax(aggregated, clipped)
        
        # Compute centroid
        if aggregated.sum() > 0:
            fli_score = fuzz.defuzz(universe, aggregated, 'centroid')
        else:
            # Default to middle value if no rules activated
            fli_score = 50.0
        
        return float(fli_score)
    
    def _get_linguistic_label(self, fli_score: float) -> str:
        """
        Convert FLI score to linguistic label.
        
        Parameters:
        -----------
        fli_score : float
            Fuzzy Livability Index score
            
        Returns:
        --------
        str
            Linguistic label
        """
        if fli_score >= 65:
            return 'excellent'
        elif fli_score >= 45:
            return 'good'
        elif fli_score >= 25:
            return 'fair'
        else:
            return 'poor'
    
    def compute_batch(self, df: pd.DataFrame, 
                     feature_mapping: Dict[str, str] = None) -> pd.DataFrame:
        """
        Compute FLI for multiple dwellings.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame with dwelling features
        feature_mapping : Dict[str, str]
            Mapping from dataset columns to fuzzy variable names
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with FLI scores and labels
        """
        print(f"\nComputing Fuzzy Livability Index for {len(df)} dwellings...")
        
        # Default feature mapping
        if feature_mapping is None:
            feature_mapping = {
                'noise_lden': 'noise_lden',
                'noise_lnight': 'noise_lnight',
                'daylight_avg': 'daylight',
                'view_sky': 'view_sky',
                'view_greenery': 'view_greenery',
                'location_poi_count': 'location_poi'
            }
        
        results = []
        
        for idx, row in df.iterrows():
            # Extract features
            features = {}
            for dataset_col, fuzzy_var in feature_mapping.items():
                if dataset_col in row:
                    value = row[dataset_col]
                    # Convert daylight from klx to lux if needed
                    if fuzzy_var == 'daylight' and value < 10:
                        value = value * 1000  # Convert klx to lux
                    features[fuzzy_var] = value
            
            # Compute FLI
            result = self.compute_single_dwelling(features)
            
            results.append({
                'dwelling_id': idx,
                'fli_score': result['fli_score'],
                'linguistic_label': result['linguistic_label'],
                'num_activated_rules': len(result['activated_rules'])
            })
        
        results_df = pd.DataFrame(results)
        
        print(f"Computation complete!")
        print(f"\nFLI Score Distribution:")
        print(results_df['fli_score'].describe())
        print(f"\nLinguistic Label Distribution:")
        print(results_df['linguistic_label'].value_counts())
        
        return results_df
    
    def explain_dwelling(self, features: Dict[str, float], 
                        top_n_rules: int = 5) -> str:
        """
        Generate human-readable explanation for a dwelling's FLI score.
        
        Parameters:
        -----------
        features : Dict[str, float]
            Dwelling features
        top_n_rules : int
            Number of top activated rules to include
            
        Returns:
        --------
        str
            Explanation text
        """
        result = self.compute_single_dwelling(features)
        
        explanation = []
        explanation.append("="*80)
        explanation.append("FUZZY LIVABILITY ASSESSMENT EXPLANATION")
        explanation.append("="*80)
        explanation.append(f"\nFuzzy Livability Index (FLI): {result['fli_score']:.2f}/100")
        explanation.append(f"Linguistic Label: {result['linguistic_label'].upper()}")
        explanation.append("\n" + "-"*80)
        explanation.append("INPUT FEATURES:")
        explanation.append("-"*80)
        
        for var, value in features.items():
            explanation.append(f"\n{var}: {value:.2f}")
            if var in result['input_fuzzification']:
                fuzz_values = result['input_fuzzification'][var]
                for term, degree in fuzz_values.items():
                    if degree > 0.01:
                        explanation.append(f"  - {term}: {degree:.3f}")
        
        explanation.append("\n" + "-"*80)
        explanation.append(f"TOP {top_n_rules} ACTIVATED RULES:")
        explanation.append("-"*80)
        
        # Sort rules by activation
        sorted_rules = sorted(
            result['activated_rules'],
            key=lambda x: x['activation'],
            reverse=True
        )[:top_n_rules]
        
        for i, rule in enumerate(sorted_rules, 1):
            explanation.append(f"\n{i}. Rule {rule['rule_id']}: {rule['description']}")
            explanation.append(f"   Activation: {rule['activation']:.3f}")
        
        explanation.append("\n" + "-"*80)
        explanation.append("OUTPUT MEMBERSHIPS:")
        explanation.append("-"*80)
        
        for term, degree in result['output_memberships'].items():
            if degree > 0.01:
                explanation.append(f"{term}: {degree:.3f}")
        
        explanation.append("\n" + "="*80)
        
        return "\n".join(explanation)


def compute_fuzzy_livability_index(df: pd.DataFrame, 
                                   feature_mapping: Dict[str, str] = None) -> pd.DataFrame:
    """
    Main function to compute Fuzzy Livability Index for a dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Preprocessed dwelling dataset
    feature_mapping : Dict[str, str]
        Mapping from dataset columns to fuzzy variable names
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with FLI scores
    """
    fis = LiveabilityFuzzySystem()
    return fis.compute_batch(df, feature_mapping)


if __name__ == "__main__":
    # Example usage with synthetic data
    print("Fuzzy Inference System for Livability Assessment")
    print("="*80)
    
    # Create fuzzy system
    fis = LiveabilityFuzzySystem()
    
    # Example dwelling features
    example_dwelling = {
        'noise_lden': 52,      # dBA - just below WHO threshold
        'noise_lnight': 43,    # dBA - quiet at night
        'daylight': 350,       # lux - high daylight
        'view_sky': 2.5,       # sr - good sky view
        'view_greenery': 0.8,  # sr - moderate greenery
        'location_poi': 35     # POI count - high accessibility
    }
    
    # Compute and explain
    explanation = fis.explain_dwelling(example_dwelling)
    print(explanation)

