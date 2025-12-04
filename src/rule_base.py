"""
Fuzzy Rule Base Module - V2

Defines the fuzzy inference rules for livability assessment using Mamdani inference.

V2 Design Principles:
1. Health-first: noise is a strong negative factor but NOT an absolute veto
2. Avoid redundancy: daylight and sky-view not hard-ANDed (they're correlated)
3. POI as conditional bonus: high accessibility only helps if health baseline is decent
4. City trade-off: high POI + high noise = "convenient but uncomfortable" = fair
5. Green view matters: associated with stress recovery, explicit in excellent/good rules

Rule Distribution:
- POOR (7 rules): serious health/comfort issues
- FAIR (8 rules): acceptable but suboptimal conditions
- GOOD (6 rules): comfortable living conditions
- EXCELLENT (3 rules): ideal conditions across all dimensions
"""

import numpy as np
from typing import List, Dict, Tuple


class FuzzyRuleBase:
    """
    Class to define and manage fuzzy inference rules for livability assessment.
    """
    
    def __init__(self):
        """Initialize the fuzzy rule base."""
        self.rules = self._define_rules()
    
    def _define_rules(self) -> List[Dict]:
        """
        Define fuzzy IF-THEN rules for livability assessment.

        V2 Rule Base: 24 rules organized by consequent (poor/fair/good/excellent)
        Key changes from V1:
        - No single-variable veto rules for noise (requires combination)
        - City trade-off rules: high POI + high noise = fair (not poor)
        - Greenery explicitly required for excellent ratings
        - Daylight and sky-view not hard-ANDed (avoid redundancy)

        Returns:
        --------
        List[Dict]
            List of 24 fuzzy rules
        """
        rules = [
            # ============================================================
            # POOR LIVABILITY RULES (7 rules)
            # Serious health/comfort issues requiring multiple factors
            # ============================================================
            {
                'id': 1,
                'description': 'Both day and night noise are high - severe noise exposure',
                'antecedents': {
                    'noise_lden': 'noisy',
                    'noise_lnight': 'noisy'
                },
                'consequent': {'livability': 'poor'},
                'weight': 1.0
            },
            {
                'id': 2,
                'description': 'Night noise is high with poor greenery - sleep quality compromised',
                'antecedents': {
                    'noise_lnight': 'noisy',
                    'view_greenery': 'poor'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.95
            },
            {
                'id': 3,
                'description': 'Day noise is high with low daylight - multiple health stressors',
                'antecedents': {
                    'noise_lden': 'noisy',
                    'daylight': 'low'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.90
            },
            {
                'id': 4,
                'description': 'Day noise is high with poor sky view - confined and loud',
                'antecedents': {
                    'noise_lden': 'noisy',
                    'view_sky': 'poor'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.90
            },
            {
                'id': 5,
                'description': 'Triple poor: low daylight, poor sky view, poor greenery',
                'antecedents': {
                    'daylight': 'low',
                    'view_sky': 'poor',
                    'view_greenery': 'poor'
                },
                'consequent': {'livability': 'poor'},
                'weight': 1.0
            },
            {
                'id': 6,
                'description': 'Moderate day noise with noisy nights - sleep disruption',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'noise_lnight': 'noisy'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.90
            },
            {
                'id': 7,
                'description': 'Moderate day noise with low daylight - substandard environment',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'daylight': 'low'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.80
            },

            # ============================================================
            # FAIR LIVABILITY RULES (8 rules)
            # Acceptable but suboptimal, includes city trade-off scenarios
            # ============================================================
            {
                'id': 8,
                'description': 'Moderate noise levels day and night - typical urban condition',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'noise_lnight': 'moderate'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.95
            },
            {
                'id': 9,
                'description': 'Quiet day noise but low daylight - lighting deficiency',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'daylight': 'low'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.75
            },
            {
                'id': 10,
                'description': 'Quiet day noise but poor sky view - limited openness',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'view_sky': 'poor'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.75
            },
            {
                'id': 11,
                'description': 'Poor greenery with medium daylight - limited nature contact',
                'antecedents': {
                    'view_greenery': 'poor',
                    'daylight': 'medium'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.80
            },
            {
                'id': 12,
                'description': 'Poor greenery with moderate sky view - limited restorative environment',
                'antecedents': {
                    'view_greenery': 'poor',
                    'view_sky': 'moderate'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.80
            },
            {
                'id': 13,
                'description': 'City trade-off: high POI but day noise is high - convenient but loud',
                'antecedents': {
                    'location_poi': 'high',
                    'noise_lden': 'noisy'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.60
            },
            {
                'id': 14,
                'description': 'City trade-off: high POI but night noise is high - convenient but sleep-disrupting',
                'antecedents': {
                    'location_poi': 'high',
                    'noise_lnight': 'noisy'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.55
            },
            {
                'id': 15,
                'description': 'Low POI but quiet with good greenery - peaceful but remote',
                'antecedents': {
                    'location_poi': 'low',
                    'noise_lden': 'quiet',
                    'view_greenery': 'good'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.70
            },

            # ============================================================
            # GOOD LIVABILITY RULES (6 rules)
            # Comfortable living conditions
            # ============================================================
            {
                'id': 16,
                'description': 'Quiet day and night with high daylight - healthy environment',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'noise_lnight': 'quiet',
                    'daylight': 'high'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.90
            },
            {
                'id': 17,
                'description': 'Quiet day and night with good sky view - open and peaceful',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'noise_lnight': 'quiet',
                    'view_sky': 'good'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.90
            },
            {
                'id': 18,
                'description': 'Quiet day with good greenery and medium daylight - restorative',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'view_greenery': 'good',
                    'daylight': 'medium'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.85
            },
            {
                'id': 19,
                'description': 'Quiet day with good greenery and moderate sky view - nature contact',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'view_greenery': 'good',
                    'view_sky': 'moderate'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.85
            },
            {
                'id': 20,
                'description': 'Moderate day but quiet night with high daylight - daytime active area',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'noise_lnight': 'quiet',
                    'daylight': 'high'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.80
            },
            {
                'id': 21,
                'description': 'Quiet day with high POI and moderate greenery - convenient and quiet',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'location_poi': 'high',
                    'view_greenery': 'moderate'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.75
            },

            # ============================================================
            # EXCELLENT LIVABILITY RULES (3 rules)
            # Ideal conditions - note: greenery required for excellent
            # ============================================================
            {
                'id': 22,
                'description': 'Quiet day/night with good greenery and high daylight - ideal healthy home',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'noise_lnight': 'quiet',
                    'view_greenery': 'good',
                    'daylight': 'high'
                },
                'consequent': {'livability': 'excellent'},
                'weight': 1.0
            },
            {
                'id': 23,
                'description': 'Quiet day/night with good greenery and good sky view - ideal open home',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'noise_lnight': 'quiet',
                    'view_greenery': 'good',
                    'view_sky': 'good'
                },
                'consequent': {'livability': 'excellent'},
                'weight': 1.0
            },
            {
                'id': 24,
                'description': 'Quiet day/night with good greenery and high POI - ideal accessible home',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'noise_lnight': 'quiet',
                    'view_greenery': 'good',
                    'location_poi': 'high'
                },
                'consequent': {'livability': 'excellent'},
                'weight': 0.90
            }
        ]

        return rules
    
    def get_rules(self) -> List[Dict]:
        """
        Get all fuzzy rules.
        
        Returns:
        --------
        List[Dict]
            List of fuzzy rules
        """
        return self.rules
    
    def get_rule_by_id(self, rule_id: int) -> Dict:
        """
        Get a specific rule by ID.
        
        Parameters:
        -----------
        rule_id : int
            Rule ID
            
        Returns:
        --------
        Dict
            Rule dictionary
        """
        for rule in self.rules:
            if rule['id'] == rule_id:
                return rule
        return None
    
    def get_rules_by_consequent(self, consequent_term: str) -> List[Dict]:
        """
        Get all rules with a specific consequent.
        
        Parameters:
        -----------
        consequent_term : str
            Consequent linguistic term (e.g., 'excellent')
            
        Returns:
        --------
        List[Dict]
            List of matching rules
        """
        matching_rules = []
        for rule in self.rules:
            if rule['consequent']['livability'] == consequent_term:
                matching_rules.append(rule)
        return matching_rules
    
    def print_rules(self, verbose: bool = True):
        """
        Print all fuzzy rules in a readable format.
        
        Parameters:
        -----------
        verbose : bool
            Whether to print full details
        """
        print("\n" + "="*80)
        print("FUZZY RULE BASE FOR LIVABILITY ASSESSMENT")
        print("="*80 + "\n")
        
        # Group rules by consequent
        consequents = ['excellent', 'good', 'fair', 'poor']
        
        for consequent in consequents:
            rules = self.get_rules_by_consequent(consequent)
            if rules:
                print(f"\n{consequent.upper()} LIVABILITY RULES ({len(rules)} rules):")
                print("-" * 80)
                
                for rule in rules:
                    print(f"\nRule {rule['id']}: {rule['description']}")
                    print(f"  Weight: {rule['weight']}")
                    
                    if verbose:
                        # Print antecedents
                        antecedent_str = " AND ".join([
                            f"{var} is {term}" 
                            for var, term in rule['antecedents'].items()
                        ])
                        print(f"  IF {antecedent_str}")
                        print(f"  THEN livability is {rule['consequent']['livability']}")
        
        print("\n" + "="*80)
        print(f"TOTAL RULES: {len(self.rules)}")
        print("="*80 + "\n")
    
    def get_rule_statistics(self) -> Dict:
        """
        Get statistics about the rule base.
        
        Returns:
        --------
        Dict
            Statistics about rules
        """
        stats = {
            'total_rules': len(self.rules),
            'rules_by_consequent': {},
            'variables_used': set(),
            'average_weight': 0.0
        }
        
        # Count rules by consequent
        for rule in self.rules:
            consequent = rule['consequent']['livability']
            stats['rules_by_consequent'][consequent] = \
                stats['rules_by_consequent'].get(consequent, 0) + 1
            
            # Collect variables used
            for var in rule['antecedents'].keys():
                stats['variables_used'].add(var)
        
        # Calculate average weight
        stats['average_weight'] = np.mean([rule['weight'] for rule in self.rules])
        
        return stats


if __name__ == "__main__":
    # Example usage
    print("Fuzzy Rule Base Module for Livability Assessment")
    
    # Create rule base
    rule_base = FuzzyRuleBase()
    
    # Print all rules
    rule_base.print_rules(verbose=True)
    
    # Print statistics
    print("\nRule Base Statistics:")
    stats = rule_base.get_rule_statistics()
    print(f"Total rules: {stats['total_rules']}")
    print(f"Average weight: {stats['average_weight']:.2f}")
    print(f"Variables used: {', '.join(stats['variables_used'])}")
    print(f"\nRules by consequent:")
    for consequent, count in stats['rules_by_consequent'].items():
        print(f"  {consequent}: {count} rules")

