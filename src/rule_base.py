"""
Fuzzy Rule Base Module

Defines the fuzzy inference rules for livability assessment using Mamdani inference.
Rules are based on expert knowledge and the Computing with Words framework.
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
        
        Returns:
        --------
        List[Dict]
            List of fuzzy rules
        """
        rules = [
            # EXCELLENT LIVABILITY RULES
            {
                'id': 1,
                'description': 'Quiet environment with high daylight and good views',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'daylight': 'high',
                    'view_sky': 'good'
                },
                'consequent': {'livability': 'excellent'},
                'weight': 1.0
            },
            {
                'id': 2,
                'description': 'Quiet with good greenery view and high accessibility',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'view_greenery': 'good',
                    'location_poi': 'high'
                },
                'consequent': {'livability': 'excellent'},
                'weight': 1.0
            },
            
            # GOOD LIVABILITY RULES
            {
                'id': 3,
                'description': 'Moderate noise with high daylight and good views',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'daylight': 'high',
                    'view_sky': 'good'
                },
                'consequent': {'livability': 'good'},
                'weight': 1.0
            },
            {
                'id': 4,
                'description': 'Quiet environment with medium daylight',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'daylight': 'medium',
                    'view_sky': 'moderate'
                },
                'consequent': {'livability': 'good'},
                'weight': 1.0
            },
            {
                'id': 5,
                'description': 'Moderate noise but good views and accessibility',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'view_sky': 'good',
                    'location_poi': 'high'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.9
            },
            
            # FAIR LIVABILITY RULES
            {
                'id': 6,
                'description': 'Moderate noise with medium daylight',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'daylight': 'medium',
                    'view_sky': 'moderate'
                },
                'consequent': {'livability': 'fair'},
                'weight': 1.0
            },
            {
                'id': 7,
                'description': 'Quiet but low daylight and poor views',
                'antecedents': {
                    'noise_lden': 'quiet',
                    'daylight': 'low',
                    'view_sky': 'poor'
                },
                'consequent': {'livability': 'fair'},
                'weight': 1.0
            },
            {
                'id': 8,
                'description': 'Moderate noise with good accessibility',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'location_poi': 'high',
                    'view_sky': 'moderate'
                },
                'consequent': {'livability': 'fair'},
                'weight': 0.8
            },
            
            # POOR LIVABILITY RULES
            {
                'id': 9,
                'description': 'Noisy environment regardless of other factors',
                'antecedents': {
                    'noise_lden': 'noisy'
                },
                'consequent': {'livability': 'poor'},
                'weight': 1.0
            },
            {
                'id': 10,
                'description': 'Low daylight with poor views',
                'antecedents': {
                    'daylight': 'low',
                    'view_sky': 'poor',
                    'view_greenery': 'poor'
                },
                'consequent': {'livability': 'poor'},
                'weight': 1.0
            },
            {
                'id': 11,
                'description': 'Moderate noise with low daylight and poor views',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'daylight': 'low',
                    'view_sky': 'poor'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.9
            },
            {
                'id': 12,
                'description': 'Poor accessibility with low environmental quality',
                'antecedents': {
                    'location_poi': 'low',
                    'daylight': 'low',
                    'noise_lden': 'moderate'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.7
            },
            
            # ADDITIONAL NUANCED RULES
            {
                'id': 13,
                'description': 'Excellent daylight compensates for moderate noise',
                'antecedents': {
                    'noise_lden': 'moderate',
                    'daylight': 'high',
                    'location_poi': 'high'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.85
            },
            {
                'id': 14,
                'description': 'Good greenery view with quiet night environment',
                'antecedents': {
                    'noise_lnight': 'quiet',
                    'view_greenery': 'good',
                    'daylight': 'medium'
                },
                'consequent': {'livability': 'good'},
                'weight': 0.9
            },
            {
                'id': 15,
                'description': 'Noisy night environment degrades livability',
                'antecedents': {
                    'noise_lnight': 'noisy'
                },
                'consequent': {'livability': 'poor'},
                'weight': 0.95
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

