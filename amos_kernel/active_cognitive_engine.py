#!/usr/bin/env python3
"""Active Cognitive Engine - Uses Legacy Brain for Live Reasoning."""

import json
from pathlib import Path
from typing import Any

CORE_PATH = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/_00_AMOS_CANON/_LEGACY BRAIN2/Core")


class ActiveCognitiveEngine:
    """Cognitive engine that actively uses legacy brain laws."""
    
    def __init__(self):
        self.cognition = self._load_cognition_engine()
        self.laws = self.cognition.get('layer_1_meta_logic_kernel', {}).get('core_laws', {})
    
    def _load_cognition_engine(self) -> dict:
        """Load the cognition engine definition."""
        filepath = CORE_PATH / "AMOS_Cognition_Engine_v0.json"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('amos_cognition_infinity_kernel', {})
        except Exception as e:
            print(f"Error loading cognition engine: {e}")
            return {}
    
    def apply_law_of_law(self, proposition: str, context: dict) -> dict:
        """Apply Law of Law: check for internal consistency."""
        law = self.laws.get('law_of_law', {})
        
        # Check for contradictions
        contradictions = []
        if 'assumptions' in context:
            for i, a1 in enumerate(context['assumptions']):
                for a2 in context['assumptions'][i+1:]:
                    if self._are_contradictory(a1, a2):
                        contradictions.append((a1, a2))
        
        return {
            'law': 'law_of_law',
            'proposition': proposition,
            'consistent': len(contradictions) == 0,
            'contradictions': contradictions,
            'properties_checked': law.get('properties', []),
            'recommendation': 'VALID' if not contradictions else 'REJECT - Fix contradictions'
        }
    
    def apply_rule_of_2(self, hypothesis: str) -> dict:
        """Apply Rule of 2: construct structural opposite."""
        law = self.laws.get('rule_of_2', {})
        
        # Generate structural opposite
        opposite = self._generate_opposite(hypothesis)
        
        return {
            'law': 'rule_of_2',
            'primary_hypothesis': hypothesis,
            'structural_opposite': opposite,
            'operations': law.get('operations', []),
            'instruction': 'Evaluate both against evidence before deciding'
        }
    
    def apply_rule_of_4(self, problem: str) -> dict:
        """Apply Rule of 4: decompose into quadrants."""
        law = self.laws.get('rule_of_4', {})
        
        return {
            'law': 'rule_of_4',
            'problem': problem,
            'quadrants': {
                'biological_state': f'Physical/biological aspects of: {problem}',
                'experiential_history': f'Past experiences related to: {problem}',
                'logical_structure': f'Formal logic and structure of: {problem}',
                'systemic_context': f'System/environment context of: {problem}'
            },
            'benefits': law.get('benefits', []),
            'instruction': 'Analyze all 4 quadrants before concluding'
        }
    
    def reason(self, problem: str, context: dict = None) -> dict:
        """Full cognitive reasoning pipeline using all laws."""
        if context is None:
            context = {}
        
        print(f"\n[ACTIVE COGNITION] Processing: {problem[:50]}...")
        
        # Step 1: Law of Law - check consistency
        law_result = self.apply_law_of_law(problem, context)
        print(f"  [Law of Law] Consistent: {law_result['consistent']}")
        
        # Step 2: Rule of 2 - duality check
        rule2_result = self.apply_rule_of_2(problem)
        print(f"  [Rule of 2] Opposite: {rule2_result['structural_opposite'][:40]}...")
        
        # Step 3: Rule of 4 - quadrant decomposition
        rule4_result = self.apply_rule_of_4(problem)
        print(f"  [Rule of 4] Quadrants: {len(rule4_result['quadrants'])}")
        
        return {
            'problem': problem,
            'law_of_law': law_result,
            'rule_of_2': rule2_result,
            'rule_of_4': rule4_result,
            'cognitive_status': 'COMPLETE',
            'recommendation': self._synthesize_recommendation(law_result, rule2_result, rule4_result)
        }
    
    def _are_contradictory(self, a1: str, a2: str) -> bool:
        """Check if two assumptions are contradictory."""
        # Simple contradiction detection
        opposites = [
            ('true', 'false'), ('yes', 'no'), ('valid', 'invalid'),
            ('consistent', 'inconsistent'), ('all', 'none')
        ]
        a1_lower, a2_lower = a1.lower(), a2.lower()
        for op1, op2 in opposites:
            if (op1 in a1_lower and op2 in a2_lower) or (op2 in a1_lower and op1 in a2_lower):
                return True
        return False
    
    def _generate_opposite(self, hypothesis: str) -> str:
        """Generate structural opposite of hypothesis."""
        # Simple negation strategies
        if 'is ' in hypothesis.lower():
            return hypothesis.replace('is ', 'is not ')
        if 'will ' in hypothesis.lower():
            return hypothesis.replace('will ', 'will not ')
        if 'can ' in hypothesis.lower():
            return hypothesis.replace('can ', 'cannot ')
        return f"Opposite of: {hypothesis}"
    
    def _synthesize_recommendation(self, law, rule2, rule4) -> str:
        """Synthesize final recommendation from all laws."""
        if not law['consistent']:
            return "REJECT: Fix contradictions before proceeding"
        return "ACCEPT: All laws satisfied. Consider opposite hypothesis and all 4 quadrants before final decision."


def main():
    """Demonstrate active cognitive reasoning."""
    print("="*70)
    print("ACTIVE COGNITIVE ENGINE - Using Legacy Brain for Live Reasoning")
    print("="*70)
    
    # Initialize cognitive engine
    engine = ActiveCognitiveEngine()
    
    # Active reasoning task
    problem = "Should we deploy this code to production?"
    context = {
        'assumptions': [
            'The code is tested',
            'All tests pass',
            'Production is stable'
        ]
    }
    
    print(f"\nInput Problem: {problem}")
    print(f"Context: {context}")
    
    # Run full cognitive pipeline
    result = engine.reason(problem, context)
    
    print(f"\n{'='*70}")
    print("COGNITIVE OUTPUT:")
    print(f"Status: {result['cognitive_status']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"{'='*70}")
    
    return result


if __name__ == "__main__":
    main()
