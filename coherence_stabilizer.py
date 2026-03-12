"""
core/coherence_stabilizer.py
Stabilizes system coherence and torsion to maintain coherent dialogues
"""

import numpy as np
import math
from typing import Dict, List, Optional

class CoherenceStabilizer:
    """
    Maintains system coherence in optimal ranges (0.7-0.9)
    and adjusts torsion to avoid abrupt transitions.
    """
    
    def __init__(self, target_coherence=0.8, max_torsion=0.08):
        self.target_coherence = target_coherence
        self.max_torsion = max_torsion
        self.coherence_history = []
        self.torsion_history = []
        self.stabilization_attempts = 0
        
        # Control parameters
        self.coherence_min = 0.7
        self.coherence_max = 0.9
        self.torsion_min = 0.05
        self.torsion_max = 0.08
        
        # Correction factors
        self.heegner_boost = 163.0 / 200.0  # ≈ 0.815
        self.riemann_damping = 14.1347 / 20.0  # ≈ 0.7067
        
        print(f"  ✅ CoherenceStabilizer initialized")
        print(f"     🎯 Target coherence: {target_coherence}")
        print(f"     📊 Max torsion: {max_torsion}")
    
    def stabilize(self, current_coherence: float, current_torsion: float, 
                 entropy: float, exchange_count: int) -> Dict:
        """
        Applies stabilization to current coherence and torsion.
        
        Args:
            current_coherence: Current tensor coherence (0-1)
            current_torsion: Current torsion (rad)
            entropy: Conversation entropy (0-1)
            exchange_count: Number of exchanges in the conversation
        
        Returns:
            Dictionary with correction factors
        """
        self.coherence_history.append(current_coherence)
        self.torsion_history.append(current_torsion)
        
        # Maintain history
        if len(self.coherence_history) > 20:
            self.coherence_history.pop(0)
        if len(self.torsion_history) > 20:
            self.torsion_history.pop(0)
        
        # Calculate trends
        coherence_trend = self._calculate_trend(self.coherence_history)
        torsion_trend = self._calculate_trend(self.torsion_history)
        
        # Determine if stabilization is needed
        needs_stabilization = (
            current_coherence < self.coherence_min or
            current_coherence > self.coherence_max or
            current_torsion > self.torsion_max or
            current_torsion < self.torsion_min
        )
        
        # Calculate correction factors
        coherence_correction = 1.0
        torsion_correction = 1.0
        
        if needs_stabilization:
            self.stabilization_attempts += 1
            
            # Coherence correction
            if current_coherence < self.coherence_min:
                # Need to increase coherence
                deficit = (self.target_coherence - current_coherence)
                coherence_correction = 1.0 + (deficit * self.heegner_boost)
                
                # Also reduce torsion to stabilize
                torsion_correction = 1.0 - (deficit * 0.5)
                
            elif current_coherence > self.coherence_max:
                # Too much coherence, need flexibility
                excess = (current_coherence - self.target_coherence)
                coherence_correction = 1.0 - (excess * 0.3)
            
            # Torsion correction
            if current_torsion > self.torsion_max:
                # Excess torsion, reduce
                excess = (current_torsion - self.torsion_max)
                torsion_correction = 1.0 - (excess * self.riemann_damping)
                
            elif current_torsion < self.torsion_min:
                # Low torsion, increase slightly
                deficit = (self.torsion_min - current_torsion)
                torsion_correction = 1.0 + (deficit * 0.3)
        
        # Apply long conversation factor
        if exchange_count > 10:
            # In long conversations, we tend to stabilize naturally
            long_conversation_factor = 1.0 - (exchange_count * 0.005)
            torsion_correction *= long_conversation_factor
        
        return {
            'needs_stabilization': needs_stabilization,
            'coherence_correction': coherence_correction,
            'torsion_correction': torsion_correction,
            'coherence_trend': coherence_trend,
            'torsion_trend': torsion_trend,
            'stabilization_count': self.stabilization_attempts,
            'recommended_lambda': self._calculate_recommended_lambda(current_coherence, entropy)
        }
    
    def _calculate_trend(self, history: List[float]) -> float:
        """Calculates the trend of a historical series"""
        if len(history) < 3:
            return 0.0
        
        # Slope of last 3 values
        recent = history[-3:]
        x = np.array([0, 1, 2])
        y = np.array(recent)
        try:
            slope = np.polyfit(x, y, 1)[0]
            return float(slope)
        except:
            return 0.0
    
    def _calculate_recommended_lambda(self, coherence: float, entropy: float) -> float:
        """Calculates the recommended learning factor"""
        # Base lambda according to coherence
        if coherence < 0.5:
            base_lambda = 0.05  # Very stable
        elif coherence < 0.7:
            base_lambda = 0.1   # Stable
        elif coherence < 0.85:
            base_lambda = 0.2   # Moderate
        else:
            base_lambda = 0.3   # Flexible
        
        # Adjust by entropy
        lambda_value = base_lambda * (1.0 - entropy * 0.5)
        
        return max(0.03, min(0.4, lambda_value))
    
    def get_status(self) -> Dict:
        """Gets the current status of the stabilizer"""
        return {
            'current_coherence': self.coherence_history[-1] if self.coherence_history else 0,
            'current_torsion': self.torsion_history[-1] if self.torsion_history else 0,
            'coherence_trend': self._calculate_trend(self.coherence_history),
            'torsion_trend': self._calculate_trend(self.torsion_history),
            'stabilization_attempts': self.stabilization_attempts,
            'within_optimal_range': (
                self.coherence_min <= (self.coherence_history[-1] if self.coherence_history else 0) <= self.coherence_max and
                self.torsion_min <= (self.torsion_history[-1] if self.torsion_history else 0) <= self.torsion_max
            ) if self.coherence_history else False
        }
    
    def get_conversation_health(self) -> str:
        """Returns a diagnosis of conversation health"""
        if not self.coherence_history:
            return "Initial conversation"
        
        last_coherence = self.coherence_history[-1]
        last_torsion = self.torsion_history[-1]
        
        if last_coherence < 0.5:
            coherence_status = "⚠️ Low - needs stabilization"
        elif last_coherence < 0.7:
            coherence_status = "🟡 Moderate - improving"
        elif last_coherence < 0.9:
            coherence_status = "🟢 Optimal - fluid conversation"
        else:
            coherence_status = "🔵 Very high - possible rigidity"
        
        if last_torsion > 0.09:
            torsion_status = "⚠️ High - risk of abrupt changes"
        elif last_torsion > 0.07:
            torsion_status = "🟡 Moderate - acceptable"
        else:
            torsion_status = "🟢 Optimal - stable"
        
        trend = self._calculate_trend(self.coherence_history)
        trend_text = "improving" if trend > 0 else "worsening" if trend < 0 else "stable"
        
        return f"Health: {coherence_status} | Torsion: {torsion_status} | Trend: {trend_text}"
    
    def get_stabilization_history(self) -> Dict:
        """Returns stabilization history for analysis"""
        return {
            'coherence_history': self.coherence_history[-10:],
            'torsion_history': self.torsion_history[-10:],
            'attempts': self.stabilization_attempts,
            'avg_coherence': np.mean(self.coherence_history) if self.coherence_history else 0,
            'avg_torsion': np.mean(self.torsion_history) if self.torsion_history else 0,
        }