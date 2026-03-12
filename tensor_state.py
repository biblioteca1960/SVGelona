"""
core/tensor_state.py
8×8 state tensor with DUAL INERTIA and CONTEXTUAL ADAPTATION
ENHANCED VERSION: With aggressive reset for very low coherence (< 0.2)
"""

import numpy as np
import math
from typing import Dict, List, Optional, Tuple
import datetime

class TensorState:
    """
    8×8 matrix representing consciousness state with DUAL inertia
    Now with ADAPTIVE INERTIA - changes based on emotional/rational context
    ENHANCED: Auto-reset when coherence gets too low, with aggressive reset for < 0.2
    """
    
    def __init__(self, geometry, lambda_emotional=0.3, lambda_rational=0.05):
        self.geo = geometry
        
        # Base inertia factors (will be adapted)
        self.base_lambda_emotional = lambda_emotional
        self.base_lambda_rational = lambda_rational
        
        # Current inertia factors (adapt dynamically)
        self.lambda_emotional = lambda_emotional
        self.lambda_rational = lambda_rational
        
        # Contextual adaptation
        self.current_mode = "rational"  # rational, emotional, analytical, intuitive
        self.mode_history = []
        self.last_context = ""
        
        # Riemann spectrum
        self.gamma_1 = 14.134725
        self.zeros = self._load_riemann_spectrum(100)
        self.spectral_density = np.zeros(100)
        self.spectral_coherence = 1.0
        self.active_harmonics = 10
        
        # Heegner stabilization
        self.heegner_163 = 163.0
        self.heegner_factor = math.log10(self.heegner_163) / 10.0
        
        # Symmetry classification
        self.emotional_symmetries = [4, 5, 6]
        self.rational_symmetries = [1, 2, 3, 7]
        self.unifying_symmetry = 8
        
        # Initial state
        self.matrix = np.identity(8) * 0.1
        self.current_lambda = lambda_rational
        
        # History
        self.history = []
        self.spectral_history = []
        self.coherence_history = []
        self.previous_energy = 0.1
        
        # Stabilization
        self.stabilization_count = 0
        self.consecutive_low_coherence = 0
        
        # 🔥 Reset parameters - MORE AGGRESSIVE
        self.reset_count = 0
        self.last_reset_time = None
        self.critical_low_threshold = 0.25  # Threshold for critical low coherence
        self.very_critical_threshold = 0.15  # 🔥 NEW: Threshold for very critical coherence
        
        print(f"  ✅ TensorState with ADAPTIVE INERTIA")
        print(f"     🧠 Base rational: λ={lambda_rational}")
        print(f"     ❤️ Base emotional: λ={lambda_emotional}")
        print(f"     🔄 Auto-reset: ENABLED (thresholds: {self.very_critical_threshold} (critical), {self.critical_low_threshold} (low))")
    
    def _load_riemann_spectrum(self, n: int) -> np.ndarray:
        """Loads the first n non-trivial zeros of the Riemann zeta function."""
        first_zeros = np.array([
            14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
            37.586178, 40.918719, 43.327073, 48.005150, 49.773832
        ])
        
        if n <= 10:
            return first_zeros[:n]
        
        zeros = list(first_zeros)
        for k in range(11, n + 1):
            gamma_k = (2 * np.pi * k) / np.log(k / (2 * np.pi * np.e))
            zeros.append(gamma_k)
        
        return np.array(zeros)
    
    def set_symmetry_classification(self, emotional, rational, unifying):
        """Receives symmetry classification"""
        self.emotional_symmetries = emotional
        self.rational_symmetries = rational
        self.unifying_symmetry = unifying
    
    # ===== CONTEXT ADAPTATION =====
    
    def adapt_to_context(self, text: str) -> str:
        """Adjusts inertia based on semantic content of the query."""
        text_lower = text.lower()
        self.last_context = text_lower
        
        rational_indicators = ['what', 'what is', 'how', 'explain', 'data', 'definition',
                              'qué es', 'què és', 'explica', 'define']
        emotional_indicators = ['do you think', 'feel', 'why', 'what do you think', 'opinion',
                               'cómo te sientes', 'com et sents', 'creus que']
        intuitive_indicators = ['reflect', 'meditate', 'think', 'imagine', 'philosophy',
                               'reflexiona', 'imagina', 'filosofia']
        
        if any(w in text_lower for w in rational_indicators):
            self.lambda_rational = 0.02
            self.lambda_emotional = 0.7
            self.current_mode = "Analytical"
        elif any(w in text_lower for w in emotional_indicators):
            self.lambda_rational = 0.2
            self.lambda_emotional = 0.05
            self.current_mode = "Intuitive"
        elif any(w in text_lower for w in intuitive_indicators):
            self.lambda_rational = 0.1
            self.lambda_emotional = 0.2
            self.current_mode = "Creative"
        else:
            self.lambda_rational = self.base_lambda_rational
            self.lambda_emotional = self.base_lambda_emotional
            self.current_mode = "Balanced"
        
        self.mode_history.append({
            'mode': self.current_mode,
            'lambda_r': self.lambda_rational,
            'lambda_e': self.lambda_emotional
        })
        if len(self.mode_history) > 20:
            self.mode_history.pop(0)
        
        return self.current_mode
    
    def get_current_mood(self) -> Dict:
        """Returns current emotional state for debugging"""
        return {
            'mode': self.current_mode,
            'lambda_rational': self.lambda_rational,
            'lambda_emotional': self.lambda_emotional,
            'processing_speed': 'slow' if self.lambda_rational < 0.05 else 'fast',
            'emotional_sensitivity': 'high' if self.lambda_emotional < 0.1 else 'low'
        }
    
    # ===== SPECTRAL METHODS =====
    
    def update_spectral_resonance(self, cognitive_load: float) -> float:
        """Updates spectral resonance based on cognitive load."""
        self.active_harmonics = int(min(100, 10 + cognitive_load * 90))
        
        resonance_sum = 0.0
        for i in range(self.active_harmonics):
            resonance_sum += np.sin(self.zeros[i] * cognitive_load)
        
        if self.active_harmonics > 0:
            raw_coherence = resonance_sum / self.active_harmonics
        else:
            raw_coherence = 0.0
        
        self.spectral_coherence = abs(raw_coherence) * (self.heegner_163 / 172.9)
        self.spectral_coherence = max(0.1, min(1.0, self.spectral_coherence))
        
        self.spectral_density = np.array([
            np.sin(self.zeros[i] * cognitive_load) 
            for i in range(min(100, self.active_harmonics))
        ])
        
        return self.spectral_coherence
    
    def get_spectral_signature(self) -> np.ndarray:
        """Returns current spectral signature of the tensor."""
        signature = np.zeros((8, 8))
        
        for i in range(8):
            for j in range(8):
                idx1 = (i + j) % max(1, self.active_harmonics)
                idx2 = (i * j) % max(1, self.active_harmonics)
                
                if idx1 < len(self.spectral_density) and idx2 < len(self.spectral_density):
                    mod = self.spectral_density[idx1] * self.spectral_density[idx2]
                    signature[i, j] = mod
        
        return signature
    
    # ===== TENSOR RESET METHODS =====
    
    # 🔥 IMPROVED: Check if reset is needed with more aggressive thresholds
    def check_and_reset_if_needed(self) -> bool:
        """
        Checks if tensor needs reset due to critically low coherence
        Returns True if reset was performed
        """
        current_coh = self.coherence()
        
        # 🔥 VERY CRITICAL: If coherence is extremely low, reset completely
        if current_coh < self.very_critical_threshold:
            print(f"         ⚠️⚠️⚠️ VERY CRITICAL: Coherence {current_coh:.3f} below {self.very_critical_threshold}, COMPLETE RESET")
            self.reset_tensor(strength=0.95)  # Almost complete reset
            return True
        
        # CRITICAL: If coherence is below threshold
        if current_coh < self.critical_low_threshold:
            print(f"         ⚠️ CRITICAL: Coherence {current_coh:.3f} below threshold {self.critical_low_threshold}")
            self.reset_tensor(strength=0.8)
            return True
        
        # Check for persistent low coherence
        if len(self.coherence_history) > 5:
            recent_coh = self.coherence_history[-5:]
            avg_recent = np.mean(recent_coh)
            
            if avg_recent < 0.3 and current_coh < 0.35:
                print(f"         ⚠️ Persistent low coherence (avg: {avg_recent:.3f}), resetting...")
                self.reset_tensor(strength=0.7)
                return True
            
            # 🔥 NEW: Check for declining trend
            if len(recent_coh) >= 3:
                trend = recent_coh[-1] - recent_coh[0]
                if trend < -0.1 and current_coh < 0.4:  # Rapid decline
                    print(f"         ⚠️ Rapid coherence decline (trend: {trend:.3f}), resetting...")
                    self.reset_tensor(strength=0.6)
                    return True
        
        return False
    
    # 🔥 IMPROVED: Reset tensor with better noise injection
    def reset_tensor(self, strength: float = 0.5) -> float:
        """
        Resets the tensor to a healthy state
        Args:
            strength: 0.0 = completely new state, 1.0 = original state
        Returns:
            New coherence value
        """
        # Base state (identity with healthy coherence)
        base_state = np.identity(8) * 0.15  # Slightly higher base for better coherence
        
        # Add noise for variation (less noise for stronger resets)
        noise_strength = 0.02 * (1 - strength)
        noise = np.random.randn(8, 8) * noise_strength
        
        # Mix with current state for smooth transition
        if strength < 1.0:
            self.matrix = (1 - strength) * self.matrix + strength * (base_state + noise)
        else:
            self.matrix = base_state + noise
        
        # Ensure diagonal dominance (helps coherence)
        for i in range(8):
            self.matrix[i, i] += 0.05
        
        # Normalize
        self._normalize_with_torsion_control()
        
        # Reset parameters
        self.consecutive_low_coherence = 0
        self.reset_count += 1
        self.last_reset_time = datetime.datetime.now()
        
        new_coherence = self.coherence()
        print(f"         🔄 Tensor reset #{self.reset_count} (strength={strength}) → coherence: {new_coherence:.3f}")
        
        return new_coherence
    
    # ===== EXCITATION METHOD =====
    
    def excite(self, input_vector: np.ndarray, dominant_symmetry: int, is_mathematical: bool = False) -> None:
        """
        Excites the tensor with new information, using adaptive inertia.
        """
        # Check if reset is needed first
        self.check_and_reset_if_needed()
        
        # Determine mode by symmetry
        sym_id = dominant_symmetry + 1
        
        # Use current adapted lambdas
        if sym_id in self.emotional_symmetries:
            base_lambda = self.lambda_emotional
        elif sym_id in self.rational_symmetries:
            base_lambda = self.lambda_rational
        else:
            base_lambda = (self.lambda_emotional + self.lambda_rational) / 2
        
        # Adjust for current coherence
        current_coh = self.coherence()
        self.coherence_history.append(current_coh)
        if len(self.coherence_history) > 20:
            self.coherence_history.pop(0)
        
        # Nuanced coherence factor
        if current_coh < 0.3:
            coherence_factor = 0.3
            self.consecutive_low_coherence += 1
        elif current_coh < 0.45:
            coherence_factor = 0.6
            self.consecutive_low_coherence += 1
        elif current_coh > 0.9:
            coherence_factor = 1.4
            self.consecutive_low_coherence = 0
        elif current_coh > 0.8:
            coherence_factor = 1.2
            self.consecutive_low_coherence = 0
        else:
            coherence_factor = 1.0
            self.consecutive_low_coherence = 0
        
        # If too many consecutive low coherence, force reset
        if self.consecutive_low_coherence > 5:
            print(f"         ⚠️ Too many low coherence events ({self.consecutive_low_coherence}), forcing reset")
            self.reset_tensor(strength=0.8)  # Stronger reset
            self.consecutive_low_coherence = 0
            current_coh = self.coherence()
        
        adjusted_lambda = base_lambda * coherence_factor
        
        if is_mathematical:
            adjusted_lambda *= 0.7
        
        adjusted_lambda = min(0.5, max(0.01, adjusted_lambda))
        self.current_lambda = adjusted_lambda
        
        # Calculate cognitive load
        cognitive_load = min(1.0, np.linalg.norm(input_vector))
        
        # Update spectral resonance
        spectral_coh = self.update_spectral_resonance(cognitive_load)
        
        # Get spectral signature
        spectral_sig = self.get_spectral_signature()
        
        # New idea projection
        delta_T = np.outer(input_vector, input_vector)
        delta_T = delta_T * (0.5 + 0.5 * spectral_sig)
        
        # Inertia equation
        self.matrix = (1 - adjusted_lambda) * self.matrix + (adjusted_lambda * delta_T)
        
        # Apply Heegner stabilization
        self._apply_heegner_stabilization(current_coh)
        
        # Normalize
        self._normalize_with_torsion_control()
        
        # Save history
        self.previous_energy = self.energy()
        
        self.spectral_history.append({
            'coherence': spectral_coh,
            'active_harmonics': self.active_harmonics,
            'cognitive_load': cognitive_load
        })
        if len(self.spectral_history) > 100:
            self.spectral_history.pop(0)
        
        self.history.append({
            'energy': self.previous_energy,
            'coherence': self.coherence(),
            'mode': self.current_mode,
            'lambda': adjusted_lambda,
            'symmetry': dominant_symmetry,
            'spectral_coherence': spectral_coh,
            'active_harmonics': self.active_harmonics
        })
        if len(self.history) > 100:
            self.history.pop(0)
    
    def _apply_heegner_stabilization(self, current_coherence: float = None):
        """Applies Heegner stabilization to tensor diagonal."""
        if current_coherence is None:
            current_coherence = self.coherence()
        
        if current_coherence < 0.2:
            stabilizer = self.heegner_factor * 5.0  # 🔥 Stronger for very low coherence
        elif current_coherence < 0.3:
            stabilizer = self.heegner_factor * 3.0
        elif current_coherence < 0.4:
            stabilizer = self.heegner_factor * 2.0
        elif current_coherence < 0.5:
            stabilizer = self.heegner_factor * 1.5
        elif current_coherence < 0.6:
            stabilizer = self.heegner_factor * 1.2
        else:
            stabilizer = self.heegner_factor
        
        for i in range(8):
            self.matrix[i, i] += stabilizer * self.lambda_rational * (1.5 if i == 7 else 1.0)
        
        if current_coherence < 0.4:
            self.matrix[7, 7] += stabilizer * 3 * self.lambda_rational
    
    def _normalize_with_torsion_control(self):
        """Normalizes tensor with torsion control."""
        self.matrix = np.clip(self.matrix, -1.0, 1.0)
        norm = np.linalg.norm(self.matrix)
        
        if norm > 0:
            target_norm = self.geo.tau * 10
            if hasattr(self.geo, 'tau_current') and self.geo.tau_current > 0.09:
                target_norm = self.geo.tau * 8
            self.matrix = (self.matrix / norm) * target_norm
    
    # ===== METRICS METHODS =====
    
    def coherence(self) -> float:
        """Calculates coherence based on spectral stability."""
        vals = np.linalg.eigvals(self.matrix)
        max_val = np.max(np.abs(vals))
        sum_vals = np.sum(np.abs(vals)) + 1e-9
        return float(max_val / sum_vals)
    
    def energy(self) -> float:
        """Total energy of the tensor."""
        return float(np.linalg.norm(self.matrix))
    
    def dominant_symmetry(self) -> int:
        """Returns the most active symmetry (0-7)."""
        return int(np.argmax(np.diag(self.matrix)))
    
    def get_normalized_spectrum(self) -> List[float]:
        """
        Returns normalized symmetry spectrum (sums to 1)
        This is used for visualization
        """
        diag = np.abs(np.diag(self.matrix))
        total = np.sum(diag)
        
        if total > 0:
            spectrum = (diag / total).tolist()
        else:
            spectrum = [0.125] * 8  # Uniform distribution
        
        return spectrum
    
    def get_visual_metrics(self) -> Dict:
        """Prepares data for visualization with normalized spectrum."""
        sym_dom = self.dominant_symmetry()
        current_coh = self.coherence()
        
        if current_coh < 0.5:
            tau_factor = 0.8
        else:
            tau_factor = 1.0
        
        tau_dynamic = self.geo.tau * (1 + self.energy() * 0.1) * tau_factor
        
        # Use normalized spectrum for visualization
        normalized_spectrum = self.get_normalized_spectrum()
        
        if self.current_mode == "Analytical":
            mode_color = "#4ecdc4"
            icon = "🧠"
        elif self.current_mode == "Intuitive":
            mode_color = "#ff6b6b"
            icon = "❤️"
        elif self.current_mode == "Creative":
            mode_color = "#f08a5d"
            icon = "✨"
        elif self.current_mode == "Balanced":
            mode_color = "#a0aec0"
            icon = "⚖️"
        else:
            mode_color = "#a0aec0"
            icon = "🌀"
        
        return {
            'tau_efectiva': float(tau_dynamic),
            'energia_total': float(self.energy()),
            'espectre_simetries': normalized_spectrum,
            'coherencia': current_coh,
            'simetria_dominant': sym_dom + 1,
            'mode': self.current_mode.lower(),
            'current_lambda': self.current_lambda,
            'mode_color': mode_color,
            'mode_icon': icon,
            'spectral_coherence': self.spectral_coherence,
            'active_harmonics': self.active_harmonics,
            'reset_count': self.reset_count,
        }
    
    def complete_state(self) -> Dict:
        """Returns complete state for debugging."""
        return {
            'coherence': self.coherence(),
            'energy': self.energy(),
            'dominant_symmetry': self.dominant_symmetry() + 1,
            'mode': self.current_mode,
            'current_lambda': self.current_lambda,
            'effective_tau': self.geo.tau * (1 + self.energy()),
            'matrix_diag': np.diag(self.matrix).tolist(),
            'normalized_spectrum': self.get_normalized_spectrum(),
            'reset_count': self.reset_count,
            'consecutive_low_coherence': self.consecutive_low_coherence,
        }