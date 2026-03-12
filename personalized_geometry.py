"""
core/personalized_geometry.py
Adaptive geometry that changes according to the user
Each conversation slightly modifies the curvature of space
"""

import math
import json
import os
from typing import List, Dict, Optional
from core.fundamental_geometry import FundamentalGeometry

class PersonalizedGeometry(FundamentalGeometry):
    """
    Geometry that adapts to each user
    Inherits from FundamentalGeometry but allows:
    - Angular defect modification based on conversation
    - Personalized torsion for each user
    - Long-term memory
    """
    
    def __init__(self, base: FundamentalGeometry, user_name: str = "anonymous"):
        # Copy properties from base geometry
        super().__init__()
        self.base = base
        self.user_name = user_name.lower().replace(" ", "_")
        
        # Learning factors (small to not break stability)
        self.epsilon_word = 0.001    # Each word modifies slightly
        self.epsilon_topic = 0.005   # Each new topic modifies more
        self.epsilon_question = 0.002 # Deep questions modify
        
        # Modification limit (to stay within stable range)
        self.max_delta_variation = 0.5    # Degrees (δ₀ ± 0.5°)
        self.max_tau_variation = 0.05     # Radians
        
        # Personalized state
        self.personal_delta = base.delta_deg
        self.personal_tau = base.tau
        self.personal_frequency = base.nu_sync_hz
        
        # User memory
        self.memory = self._load_memory()
        
        # Statistics
        self.total_words = self.memory.get('total_words', 0)
        self.topics_discussed = self.memory.get('topics_discussed', [])
        self.deep_questions = self.memory.get('deep_questions', 0)
        self.preferred_symmetry = self.memory.get('preferred_symmetry', 8)
        
        print(f"   🌍 Personalized geometry for {user_name}")
        print(f"   📊 δ₀ = {self.personal_delta:.4f}° · τ = {self.personal_tau:.4f} rad")
    
    def _load_memory(self) -> Dict:
        """Loads user memory from disk"""
        file_path = f"memories/{self.user_name}.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._default_memory()
        return self._default_memory()
    
    def _default_memory(self) -> Dict:
        """Creates default memory for new users"""
        return {
            'user_name': self.user_name,
            'total_words': 0,
            'topics_discussed': [],
            'deep_questions': 0,
            'preferred_symmetry': 8,
            'accumulated_delta': 0.0,
            'accumulated_tau': 0.0,
            'first_conversation': None,
            'last_conversation': None
        }
    
    def _save_memory(self):
        """Saves user memory to disk"""
        # Create directory if it doesn't exist
        os.makedirs('memories', exist_ok=True)
        
        self.memory.update({
            'total_words': self.total_words,
            'topics_discussed': self.topics_discussed[-20:],  # Last 20 topics
            'deep_questions': self.deep_questions,
            'preferred_symmetry': self.preferred_symmetry,
            'current_delta': self.personal_delta,
            'current_tau': self.personal_tau,
            'last_conversation': self._timestamp()
        })
        
        file_path = f"memories/{self.user_name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def _timestamp(self) -> str:
        """Returns current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def process_query(self, query: str, active_symmetry: int):
        """
        Processes a query and adapts the geometry
        Each word modifies the curvature
        """
        # Count words
        words = query.split()
        self.total_words += len(words)
        
        # Detect new topics (long words = possible topics)
        for word in words:
            if len(word) > 6 and word not in self.topics_discussed:
                self.topics_discussed.append(word)
                # New topic → more modification
                self.personal_delta += self.epsilon_topic
                self.personal_tau += self.epsilon_topic / math.sqrt(3)
        
        # Detect deep questions (end with ?)
        if '?' in query or '¿' in query:
            self.deep_questions += 1
            self.personal_delta += self.epsilon_question
        
        # Modification per word
        self.personal_delta += len(words) * self.epsilon_word
        self.personal_tau += len(words) * self.epsilon_word / math.sqrt(3)
        
        # Update preferred symmetry (the most active one)
        self.preferred_symmetry = (self.preferred_symmetry * 0.9 + active_symmetry * 0.1)
        
        # Limit to maintain stability
        self._limit_variation()
        
        # Save every 50 queries
        if self.total_words % 50 == 0:
            self._save_memory()
    
    def _limit_variation(self):
        """Keeps geometry within stable range"""
        # Limit for angular defect
        max_delta = self.base.delta_deg + self.max_delta_variation
        min_delta = self.base.delta_deg - self.max_delta_variation
        self.personal_delta = max(min_delta, min(max_delta, self.personal_delta))
        
        # Recalculate torsion (must be consistent)
        self.personal_tau = self.personal_delta * math.pi / 180 / math.sqrt(3)
    
    @property
    def personal_delta_deg(self) -> float:
        """Returns personalized angular defect"""
        return self.personal_delta
    
    @property
    def personal_tau_rad(self) -> float:
        """Returns personalized torsion"""
        return self.personal_tau
    
    @property
    def personal_frequency_thz(self) -> float:
        """Returns personalized frequency"""
        # Frequency depends on angular defect
        return self.base.nu_sync_thz * (self.personal_delta / self.base.delta_deg)
    
    def get_personal_state(self) -> Dict:
        """Returns complete state of personalized geometry"""
        return {
            'user_name': self.user_name,
            'base_delta': self.base.delta_deg,
            'personal_delta': self.personal_delta,
            'delta_difference': self.personal_delta - self.base.delta_deg,
            'personal_tau': self.personal_tau,
            'personal_frequency': self.personal_frequency_thz,
            'total_words': self.total_words,
            'topics_discussed': len(self.topics_discussed),
            'deep_questions': self.deep_questions,
            'preferred_symmetry': int(self.preferred_symmetry),
            'relative_curvature': (self.personal_delta / self.base.delta_deg)
        }