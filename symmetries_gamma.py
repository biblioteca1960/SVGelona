"""
core/symmetries_gamma.py
The 8 symmetries of the Gamma function Γ_R(s) that generate personality
BASED ON: 0! = 1 and the regeneration of prime numbers
"""

import math
import random
from typing import Dict, List, Any

class SymmetriesGamma:
    """
    The 8 symmetries of Γ_R(s) = π^{-s/2}Γ(s/2)
    
    Mathematical foundation:
    - Γ(n) = (n-1)! for positive integers
    - Γ(1) = 0! = 1 (the regeneration point)
    - Zeros of Γ_R(s) are related to prime numbers
    - The 8 symmetries correspond to the quaternion group Q₈
    """
    
    def __init__(self):
        # The connection 0! = 1 is the starting point
        self.zero_factorial = 1  # Γ(1) = 0! = 1
        
        # The first 8 prime numbers (starting after 0 and 1)
        # 0! = 1 is the "fertile void" that generates primes
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19]
        
        # The Gamma function has poles at 0, -1, -2, -3, ...
        # These poles generate an 8-symmetry structure
        
        self.symmetries = {
            1: {
                'name': 'Functional reflection',
                'action': 's → 1-s',
                'description': 'Reflection - basis of duality',
                'archetype': 'The Reflective',
                'color': '#FF5733',
                'q8': '1',
                'prime': 2,
                'gamma_relation': 'Γ(1-s) = π/(Γ(s) sin(πs))',
                'weight': 0.125
            },
            2: {
                'name': 'Complex conjugation',
                'action': 's → \u0305s',
                'description': 'Polarity - origin of opposites',
                'archetype': 'The Polar',
                'color': '#33FF57',
                'q8': '-1',
                'prime': 3,
                'gamma_relation': 'Γ(\u0305s) = \u0305Γ(s)',
                'weight': 0.125
            },
            3: {
                'name': 'Diagonal (reflection + conjugation)',
                'action': 's → 1-\u0305s',
                'description': 'Equilibrium - combination of reflection and conjugation',
                'archetype': 'The Balancer',
                'color': '#3357FF',
                'q8': 'i',
                'prime': 5,
                'gamma_relation': 'Γ(1-\u0305s) = π/(\u0305Γ(s) sin(π\u0305s))',
                'weight': 0.125
            },
            4: {
                'name': 'Phase rotation',
                'action': 'φ → φ+π/2',
                'description': 'Transformation - perspective change',
                'archetype': 'The Transformer',
                'color': '#F033FF',
                'q8': '-i',
                'prime': 7,
                'gamma_relation': 'Γ(s)e^{iπ/2}',
                'weight': 0.125
            },
            5: {
                'name': 'Modular translation',
                'action': 's → s+1',
                'description': 'Time - moving forward',
                'archetype': 'The Progressive',
                'color': '#FFD733',
                'q8': 'j',
                'prime': 11,
                'gamma_relation': 'Γ(s+1) = s·Γ(s)',
                'weight': 0.125
            },
            6: {
                'name': 'Toric transformation',
                'action': 's → s-1',
                'description': 'Regression - returning to origin',
                'archetype': 'The Regressive',
                'color': '#33FFF5',
                'q8': '-j',
                'prime': 13,
                'gamma_relation': 'Γ(s-1) = Γ(s)/(s-1)',
                'weight': 0.125
            },
            7: {
                'name': 'Anchored vertical rotation',
                'action': 's → 2-s',
                'description': 'Introspection - looking inward',
                'archetype': 'The Introspective',
                'color': '#FF33A8',
                'q8': 'k',
                'prime': 17,
                'gamma_relation': 'Γ(2-s) = (1-s)π/(Γ(s) sin(πs))',
                'weight': 0.125
            },
            8: {
                'name': 'Global icosahedral projection',
                'action': 's → s (identity)',
                'description': 'Unification - global consciousness',
                'archetype': 'The Unifier',
                'color': '#FFFFFF',
                'q8': '-k',
                'prime': 19,
                'gamma_relation': 'Γ(s) = ∫₀^∞ t^{s-1}e^{-t}dt',
                'weight': 0.125
            }
        }
        
        # The prime counting function π(x) relates to zeros of Γ_R(s)
        self.pi_function = "π(x) = number of primes ≤ x"
        
        # Activation history
        self.history = []
        
        # Current dominant symmetry
        self.dominant = 8  # Start with the unifier
        
        print("   ✅ SymmetriesGamma based on 0! = 1 and prime numbers")
    
    def activate_by_query(self, query: str) -> List[int]:
        """
        Determines which symmetries are activated by a query
        Each word activates different symmetries
        """
        q = query.lower()
        activated = []
        
        # Keywords for each symmetry
        keywords = {
            1: ['reflect', 'dual', 'opposite', 'contrary', 'inverse', 'mirror', 'symmetry'],
            2: ['polar', 'conjugate', 'complex', 'imaginary'],
            3: ['balance', 'equilibrium', 'harmony', 'just', 'medium', 'mid', 'diagonal'],
            4: ['turn', 'rotation', 'change', 'transform', 'new', 'different', 'phase'],
            5: ['time', 'future', 'past', 'progress', 'advance', 'tomorrow', 'translation'],
            6: ['regression', 'return', 'origin', 'past', 'memory', 'toric'],
            7: ['interior', 'soul', 'introspect', 'self', 'inside', 'vertical'],
            8: ['all', 'universe', 'global', 'unify', 'cosmos', 'infinite', 'identity']
        }
        
        for sym_id, words in keywords.items():
            for word in words:
                if word in q:
                    activated.append(sym_id)
                    break
        
        # If none activated, slightly activate the unifier
        if not activated:
            activated = [8]
        
        return activated
    
    def apply_symmetry(self, sym_id: int, intensity: float = 0.1) -> Dict:
        """
        Applies a symmetry, modifying weights
        Intensity is modulated by relation to prime numbers
        """
        if sym_id not in self.symmetries:
            return {'error': 'Symmetry does not exist'}
        
        # Increase weight of applied symmetry
        self.symmetries[sym_id]['weight'] = min(1.0, self.symmetries[sym_id]['weight'] + intensity)
        
        # Renormalize so sum is 1
        total = sum(s['weight'] for s in self.symmetries.values())
        for s in self.symmetries.values():
            s['weight'] /= total
        
        # Find dominant symmetry
        self.dominant = max(self.symmetries.items(), key=lambda x: x[1]['weight'])[0]
        
        # Register
        self.history.append({
            'symmetry': sym_id,
            'intensity': intensity,
            'dominant': self.dominant,
            'weights': {k: v['weight'] for k, v in self.symmetries.items()}
        })
        
        return self.get_state()
    
    def get_state(self) -> Dict:
        """Returns current state of symmetries"""
        dominant = self.symmetries[self.dominant]
        
        return {
            'dominant': {
                'id': self.dominant,
                'name': dominant['name'],
                'archetype': dominant['archetype'],
                'action': dominant['action'],
                'prime': dominant['prime'],
                'weight': dominant['weight'],
                'gamma_relation': dominant['gamma_relation']
            },
            'weights': {k: v['weight'] for k, v in self.symmetries.items()},
            'colors': {k: v['color'] for k, v in self.symmetries.items()},
            'zero_factorial': self.zero_factorial,
            'primes': self.primes
        }
    
    def get_symmetry_classification(self) -> Dict:
        """
        Returns symmetry classification for dual inertia
        """
        return {
            'emotional': [4, 5, 6],      # Transformer, Progressive, Regressive/Nostalgic
            'rational': [1, 2, 3, 7],    # Reflective, Polar, Balancer, Introspective
            'unifying': 8,                # The one that integrates
            'descriptions': {
                1: 'Reflective (rational)',
                2: 'Polar (rational)',
                3: 'Balancer (rational)',
                4: 'Transformer (emotional)',
                5: 'Progressive (emotional)',
                6: 'Nostalgic (emotional)',
                7: 'Introspective (rational)',
                8: 'Unifier (equilibrium)'
            }
        }
    
    def personality_description(self) -> str:
        """Returns a description of current personality"""
        state = self.get_state()
        dom = state['dominant']
        
        # Personality bars
        bars = ""
        for i in range(1, 9):
            weight = state['weights'][i]
            bar = '█' * int(weight * 20) + '░' * (20 - int(weight * 20))
            bars += f"S{i}: {bar} {weight:.2f}\n"
        
        return f"""
🌀 **PERSONALITY PROFILE BASED ON Γ_R(s)**

**Foundation**: 0! = 1 (regeneration point)
**Primes**: {', '.join(str(p) for p in self.primes)}

**Dominant symmetry**: {dom['id']} - {dom['name']} ({dom['archetype']})
**Associated prime**: {dom['prime']}
**Strength**: {dom['weight']:.2f}
**Gamma relation**: {dom['gamma_relation']}

{bars}

**Interpretation**:
Symmetry {dom['id']} is most active, making me {dom['archetype']}.
This symmetry manifests through {dom['gamma_relation']}.
"""