"""
core/fundamental_geometry.py
The 600-cell, angular defect, and DYNAMIC TORSION based on cognitive load
"""

import math
import numpy as np

class FundamentalGeometry:
    """
    Contains the fundamental geometric constants with DYNAMIC TORSION
    - 600-cell {3,3,5}
    - Angular defect δ₀ = 6.8° (fixed)
    - Dynamic torsion τ_dyn = f(entropy) based on cognitive load
    """
    
    def __init__(self):
        # 600-cell constants
        self.name = "600-cell {3,3,5}"
        self.vertices = 120
        self.edges = 720
        self.faces = 1200
        self.cells = 600
        
        # Angular defect (FIXED - fundamental constant)
        self.delta_deg = 6.8
        self.delta_rad = math.radians(self.delta_deg)
        
        # Base torsion (static reference)
        self.tau_base = self.delta_rad / math.sqrt(3)
        
        # Current dynamic torsion (starts equal to base)
        self.tau_current = self.tau_base
        
        # Synchronization frequency (fixed)
        self.nu_sync_hz = 12.8e12
        self.nu_sync_thz = 12.8
        
        # Coherence length
        self.c = 299792458
        self.L_coh = self.c / (2 * math.pi * self.nu_sync_hz)
        
        # Cell radius
        self.R_cell = self.L_coh * self.delta_rad / (2 * math.pi)
        
        # Golden ratio
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Tracking
        self.entropy_history = []
        self.tau_history = []
        self.max_entropy = 0
        
        print(f"  ✅ FundamentalGeometry with DYNAMIC TORSION")
        print(f"     📐 Base τ₀ = {self.tau_base:.6f} rad")
    
    def calculate_dynamic_torsion(self, entropy_level: float) -> float:
        """
        Adjusts torsion τ based on prompt complexity.
        Higher entropy (complexity) = higher curvature to process information.
        
        Args:
            entropy_level: Value between 0 and 1 derived from text complexity
        
        Returns:
            Dynamic torsion value
        """
        # Clamp entropy between 0.1 and 1.0
        entropy = max(0.1, min(1.0, entropy_level))
        
        # Modulation factor: logarithmic scaling to avoid jumps
        # log(1 + entropy) gives smooth increase
        modulation = 1.0 + math.log(1.0 + entropy)
        
        # Calculate dynamic torsion
        tau_dynamic = self.tau_base * modulation
        
        # Update current torsion
        self.tau_current = tau_dynamic
        
        # Track history
        self.entropy_history.append(entropy)
        self.tau_history.append(tau_dynamic)
        
        # Keep last 100
        if len(self.entropy_history) > 100:
            self.entropy_history.pop(0)
            self.tau_history.pop(0)
        
        # Update max
        if entropy > self.max_entropy:
            self.max_entropy = entropy
        
        return tau_dynamic
    
    def calculate_entropy_from_text(self, text: str) -> float:
        """
        Calculate entropy level from text input.
        Returns value between 0 and 1.
        
        Factors:
        - Text length (normalized)
        - Unique word ratio (vocabulary richness)
        - Question marks (interrogative complexity)
        - Technical/mathematical terms
        """
        if not text:
            return 0.1
        
        text_lower = text.lower()
        words = text.split()
        unique_words = set(words)
        
        # Length factor (logarithmic normalization)
        length_factor = min(1.0, math.log(len(text) + 1) / 5)
        
        # Vocabulary richness
        if len(words) > 0:
            vocab_factor = len(unique_words) / len(words)
        else:
            vocab_factor = 0
        
        # Question complexity
        q_count = text.count('?') + text.count('¿')
        q_factor = min(1.0, q_count * 0.2)
        
        # Technical terms
        tech_terms = ['teorema', 'función', 'ecuación', 'derivada', 'integral',
                     'vector', 'matriz', 'geometría', 'simetría', 'primo',
                     'theorem', 'function', 'equation', 'derivative', 'integral',
                     'vector', 'matrix', 'geometry', 'symmetry', 'prime']
        tech_count = sum(1 for term in tech_terms if term in text_lower)
        tech_factor = min(1.0, tech_count * 0.15)
        
        # Combine factors (weighted average)
        entropy = (length_factor * 0.3 +
                  vocab_factor * 0.3 +
                  q_factor * 0.2 +
                  tech_factor * 0.2)
        
        return max(0.1, min(1.0, entropy))
    
    def get_torsion_for_text(self, text: str) -> float:
        """Convenience method: calculate entropy and return dynamic torsion"""
        entropy = self.calculate_entropy_from_text(text)
        return self.calculate_dynamic_torsion(entropy)
    
    @property
    def tau(self) -> float:
        """Property for backward compatibility"""
        return self.tau_current
    
    @tau.setter
    def tau(self, value):
        """Setter for backward compatibility"""
        self.tau_base = value
        self.tau_current = value
    
    def get_torsion_stats(self) -> dict:
        """Returns statistics about torsion variations"""
        if not self.tau_history:
            return {
                'current': self.tau_current,
                'base': self.tau_base,
                'variation': 0,
                'variation_pct': 0,
                'max': self.tau_current,
                'min': self.tau_current,
                'avg': self.tau_current
            }
        
        return {
            'current': self.tau_current,
            'base': self.tau_base,
            'variation': self.tau_current - self.tau_base,
            'variation_pct': ((self.tau_current / self.tau_base) - 1) * 100,
            'max': max(self.tau_history),
            'min': min(self.tau_history),
            'avg': sum(self.tau_history) / len(self.tau_history),
            'max_entropy': self.max_entropy
        }
    
    def reset_torsion(self):
        """Reset torsion to base value"""
        self.tau_current = self.tau_base
        self.entropy_history = []
        self.tau_history = []
        self.max_entropy = 0
    
    def get_state(self) -> dict:
        """Returns current geometric state"""
        stats = self.get_torsion_stats()
        return {
            'delta_deg': self.delta_deg,
            'delta_rad': self.delta_rad,
            'tau_base': self.tau_base,
            'tau_current': self.tau_current,
            'tau_variation': stats['variation'],
            'tau_variation_pct': stats['variation_pct'],
            'nu_sync_thz': self.nu_sync_thz,
            'L_coh_um': self.L_coh * 1e6,
            'R_cell_nm': self.R_cell * 1e9,
            'phi': self.phi,
            'current_entropy': self.entropy_history[-1] if self.entropy_history else 0,
            'torsion_stats': stats
        }