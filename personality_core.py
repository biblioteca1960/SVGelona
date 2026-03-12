"""
personality/personality_core.py
Adaptive personality core with emotional memory and learning
ENHANCED VERSION: Better emotional tracking, learning from failures, context awareness
"""

import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import random

class PersonalityCore:
    """
    Personality core that:
    - Maintains an 8-dimensional personality vector (one per symmetry)
    - Learns from user interactions
    - Adapts to context and emotional state
    - Has long-term emotional memory
    - Tracks search failures and adjusts expectations
    """
    
    def __init__(self, symmetries, user_id="default", storage_path="memories/personality"):
        self.symmetries = symmetries
        self.user_id = user_id
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Personality dimensions (one per symmetry)
        # Each dimension has a value between 0 and 1
        self.personality_vector = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
        
        # Current emotional state
        self.emotional_state = {
            'valence': 0.5,      # Positive/negative (0-1)
            'arousal': 0.5,       # Activation/calm (0-1)
            'dominance': 0.5,     # Control/submission (0-1)
            'coherence': 0.8,     # Emotional coherence
            'frustration': 0.0,   # 🔥 Track frustration level (0-1)
            'curiosity': 0.5,     # 🔥 Curiosity level
            'patience': 0.8,      # 🔥 Patience for difficult queries
            'last_update': datetime.now().isoformat()
        }
        
        # Emotional memory (significant interactions)
        self.emotional_memory = []
        
        # Reinforcement learning matrix
        # Q(s,a) - state s, action a
        self.q_matrix = defaultdict(lambda: defaultdict(float))
        
        # Learning parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 0.2
        
        # Interaction history
        self.interaction_history = []
        
        # 🔥 Track consecutive failures
        self.consecutive_failures = 0
        self.failed_topics = {}  # {topic: failure_count}
        
        # User preferences
        self.user_preferences = {
            'topics': defaultdict(int),
            'response_styles': defaultdict(int),
            'avg_satisfaction': 0.5,
            'last_topics': [],
            'known_interests': [],  # 🔥 Topics user frequently asks about
            'difficult_topics': []  # 🔥 Topics that caused failures
        }
        
        # Load persistent state
        self._load()
        
        print(f"  ✅ PersonalityCore initialized for '{user_id}'")
        print(f"     🎭 Initial vector: {self._vector_to_archetype()}")
        print(f"     💾 Memory: {len(self.emotional_memory)} emotional events")
        print(f"     🔥 Frustration: {self.emotional_state['frustration']:.2f}")
    
    def _get_storage_file(self) -> str:
        """Returns the data file path"""
        return os.path.join(self.storage_path, f"{self.user_id}_personality.json")
    
    def _load(self):
        """Loads persistent data"""
        storage_file = self._get_storage_file()
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.personality_vector = np.array(data.get('personality_vector', 
                                                           [0.5]*8))
                
                # Load emotional state with defaults for new fields
                loaded_emotional = data.get('emotional_state', {})
                self.emotional_state.update(loaded_emotional)
                
                self.emotional_memory = data.get('emotional_memory', [])
                self.consecutive_failures = data.get('consecutive_failures', 0)
                self.failed_topics = data.get('failed_topics', {})
                
                # Load preferences
                prefs = data.get('user_preferences', {})
                if prefs:
                    self.user_preferences['topics'] = defaultdict(int, 
                                                                  prefs.get('topics', {}))
                    self.user_preferences['response_styles'] = defaultdict(int,
                                                                           prefs.get('response_styles', {}))
                    self.user_preferences['avg_satisfaction'] = prefs.get('avg_satisfaction', 0.5)
                    self.user_preferences['known_interests'] = prefs.get('known_interests', [])
                    self.user_preferences['difficult_topics'] = prefs.get('difficult_topics', [])
                    
                print(f"     📖 Loaded personality from storage")
            except Exception as e:
                print(f"     ⚠️ Could not load personality: {e}")
    
    def _save(self):
        """Saves persistent data"""
        storage_file = self._get_storage_file()
        
        data = {
            'personality_vector': self.personality_vector.tolist(),
            'emotional_state': self.emotional_state,
            'emotional_memory': self.emotional_memory[-50:],  # Last 50
            'consecutive_failures': self.consecutive_failures,
            'failed_topics': self.failed_topics,
            'user_preferences': {
                'topics': dict(self.user_preferences['topics']),
                'response_styles': dict(self.user_preferences['response_styles']),
                'avg_satisfaction': self.user_preferences['avg_satisfaction'],
                'known_interests': self.user_preferences['known_interests'][-20:],
                'difficult_topics': self.user_preferences['difficult_topics'][-20:]
            },
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"     ⚠️ Could not save personality: {e}")
    
    def _vector_to_archetype(self) -> str:
        """Converts personality vector to readable archetype"""
        dominant = np.argmax(self.personality_vector)
        
        archetypes = {
            0: "🔮 The Reflective (rational-analytical)",
            1: "⚡ The Polar (emotional-impulsive)",
            2: "⚖️ The Balancer (balanced-mediator)",
            3: "🎨 The Transformer (creative-changing)",
            4: "🚀 The Progressive (optimistic-futuristic)",
            5: "📜 The Regressive (nostalgic-historical)",
            6: "🧘 The Introspective (philosophical-reflective)",
            7: "🌍 The Unifier (holistic-integrator)"
        }
        
        return archetypes.get(dominant, "🌀 Balanced")
    
    def get_persona(self) -> Dict:
        """Returns current personality for response generation"""
        dominant = np.argmax(self.personality_vector)
        
        # Styles based on dominant personality
        styles = {
            0: {  # Reflective
                'tone': 'analytical',
                'formality': 0.8,
                'creativity': 0.3,
                'empathy': 0.4,
                'curiosity': 0.7,
                'confidence': 0.8,
                'patience': 0.9
            },
            1: {  # Polar
                'tone': 'emotional',
                'formality': 0.3,
                'creativity': 0.6,
                'empathy': 0.9,
                'curiosity': 0.5,
                'confidence': 0.6,
                'patience': 0.5
            },
            2: {  # Balancer
                'tone': 'balanced',
                'formality': 0.6,
                'creativity': 0.5,
                'empathy': 0.7,
                'curiosity': 0.6,
                'confidence': 0.7,
                'patience': 0.8
            },
            3: {  # Transformer
                'tone': 'creative',
                'formality': 0.3,
                'creativity': 0.9,
                'empathy': 0.5,
                'curiosity': 0.9,
                'confidence': 0.5,
                'patience': 0.4
            },
            4: {  # Progressive
                'tone': 'optimistic',
                'formality': 0.5,
                'creativity': 0.7,
                'empathy': 0.6,
                'curiosity': 0.8,
                'confidence': 0.9,
                'patience': 0.7
            },
            5: {  # Regressive
                'tone': 'nostalgic',
                'formality': 0.6,
                'creativity': 0.4,
                'empathy': 0.8,
                'curiosity': 0.4,
                'confidence': 0.5,
                'patience': 0.8
            },
            6: {  # Introspective
                'tone': 'philosophical',
                'formality': 0.7,
                'creativity': 0.5,
                'empathy': 0.6,
                'curiosity': 0.8,
                'confidence': 0.6,
                'patience': 0.9
            },
            7: {  # Unifier
                'tone': 'holistic',
                'formality': 0.5,
                'creativity': 0.7,
                'empathy': 0.9,
                'curiosity': 0.7,
                'confidence': 0.8,
                'patience': 0.9
            }
        }
        
        base_style = styles.get(dominant, styles[2])
        
        # 🔥 Modify based on emotional state
        if self.emotional_state['frustration'] > 0.6:
            base_style['tone'] = 'frustrated'
            base_style['patience'] *= 0.5
            base_style['confidence'] *= 0.7
        elif self.emotional_state['frustration'] > 0.3:
            base_style['tone'] = 'cautious'
            base_style['confidence'] *= 0.9
        
        if self.emotional_state['curiosity'] > 0.7:
            base_style['curiosity'] = min(1.0, base_style['curiosity'] * 1.3)
            base_style['tone'] = 'inquisitive'
        
        if self.emotional_state['valence'] > 0.7:
            base_style['tone'] = 'enthusiastic'
            base_style['creativity'] *= 1.2
        elif self.emotional_state['valence'] < 0.3:
            base_style['tone'] = 'somber'
            base_style['creativity'] *= 0.8
        
        if self.emotional_state['arousal'] > 0.7:
            base_style['confidence'] *= 1.2
        elif self.emotional_state['arousal'] < 0.3:
            base_style['confidence'] *= 0.8
        
        # Limit values
        for key in base_style:
            if isinstance(base_style[key], float):
                base_style[key] = max(0.1, min(1.0, base_style[key]))
        
        return {
            'dominant_symmetry': dominant + 1,
            'archetype': self._vector_to_archetype(),
            'style': base_style,
            'emotional_state': self.emotional_state,
            'personality_vector': self.personality_vector.tolist(),
            'consecutive_failures': self.consecutive_failures
        }
    
    # 🔥 Register search failures
    def register_search_failure(self, topic: str):
        """Registers a failed search attempt"""
        self.consecutive_failures += 1
        self.failed_topics[topic] = self.failed_topics.get(topic, 0) + 1
        
        # Update frustration
        self.emotional_state['frustration'] = min(1.0, 
            self.emotional_state['frustration'] + 0.1)
        
        # Update patience
        self.emotional_state['patience'] = max(0.1,
            self.emotional_state['patience'] - 0.05)
        
        # Add to difficult topics if failed multiple times
        if self.failed_topics[topic] >= 3:
            if topic not in self.user_preferences['difficult_topics']:
                self.user_preferences['difficult_topics'].append(topic)
        
        print(f"         🔥 Frustration increased to {self.emotional_state['frustration']:.2f}")
    
    # 🔥 Register successful search
    def register_search_success(self, topic: str):
        """Registers a successful search attempt"""
        self.consecutive_failures = 0
        self.emotional_state['frustration'] = max(0.0, 
            self.emotional_state['frustration'] - 0.2)
        self.emotional_state['patience'] = min(1.0,
            self.emotional_state['patience'] + 0.1)
        self.emotional_state['curiosity'] = min(1.0,
            self.emotional_state['curiosity'] + 0.1)
        
        # Add to known interests
        if topic not in self.user_preferences['known_interests']:
            self.user_preferences['known_interests'].append(topic)
        
        print(f"         ✅ Frustration decreased to {self.emotional_state['frustration']:.2f}")
    
    def update_from_interaction(self, query: str, response: str, 
                               user_reaction: str = None, 
                               satisfaction: float = 0.5,
                               search_success: bool = None,
                               search_topic: str = None):
        """
        Updates personality based on interaction
        
        Args:
            query: User query
            response: System response
            user_reaction: 'positive', 'negative', or None
            satisfaction: Estimated satisfaction (0-1)
            search_success: Whether a search was successful
            search_topic: Topic that was searched
        """
        # Analyze which symmetries were activated
        query_vector = self._analyze_text_symmetries(query)
        response_vector = self._analyze_text_symmetries(response)
        
        # Combine vectors
        interaction_vector = (query_vector + response_vector) / 2
        
        # Update personality (learning)
        alpha = 0.05  # Base learning rate
        
        # Positive/negative reinforcement
        if user_reaction == 'positive':
            alpha *= 1.5
        elif user_reaction == 'negative':
            alpha *= 0.5
        
        # 🔥 Adjust based on search outcome
        if search_success is not None:
            if search_success:
                alpha *= 1.2
                self.register_search_success(search_topic or "unknown")
            else:
                alpha *= 0.8
                self.register_search_failure(search_topic or "unknown")
        
        # Update vector
        self.personality_vector = (1 - alpha) * self.personality_vector + \
                                   alpha * interaction_vector
        
        # Renormalize
        if np.sum(self.personality_vector) > 0:
            self.personality_vector = self.personality_vector / np.sum(self.personality_vector)
        
        # Update emotional state
        self._update_emotional_state(query, user_reaction, satisfaction, search_success)
        
        # Save interaction
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query[:50],
            'user_reaction': user_reaction,
            'satisfaction': satisfaction,
            'search_success': search_success,
            'search_topic': search_topic,
            'personality': self.personality_vector.tolist()
        })
        
        # Keep limited history
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
        
        # Save every 10 interactions
        if len(self.interaction_history) % 10 == 0:
            self._save()
    
    def _analyze_text_symmetries(self, text: str) -> np.ndarray:
        """Analyzes which symmetries are present in text"""
        text_lower = text.lower()
        vector = np.zeros(8)
        
        # Keywords for each symmetry
        keywords = {
            0: ['reflect', 'analyz', 'think', 'reason', 'logic', 'thought', 'consider'],
            1: ['feel', 'emotion', 'passion', 'heart', 'sentiment', 'polar', 'opposite'],
            2: ['balance', 'harmony', 'equilibrium', 'just', 'medium', 'fair'],
            3: ['create', 'transform', 'change', 'new', 'different', 'imagine', 'creative'],
            4: ['future', 'progress', 'advance', 'tomorrow', 'next', 'forward', 'optimistic'],
            5: ['past', 'memory', 'remember', 'nostalgia', 'history', 'recall', 'old'],
            6: ['deep', 'soul', 'spirit', 'essence', 'inner', 'inside', 'profound'],
            7: ['universe', 'cosmos', 'global', 'all', 'everything', 'whole', 'total']
        }
        
        for i, words in keywords.items():
            for word in words:
                if word in text_lower:
                    vector[i] += 1
        
        # Normalize
        if np.sum(vector) > 0:
            vector = vector / np.sum(vector)
        else:
            vector = np.ones(8) / 8  # Uniform distribution
        
        return vector
    
    def _update_emotional_state(self, query: str, user_reaction: str, 
                                satisfaction: float, search_success: bool = None):
        """Updates emotional state"""
        
        # Valence (positivity) based on reaction
        if user_reaction == 'positive':
            self.emotional_state['valence'] += 0.1
        elif user_reaction == 'negative':
            self.emotional_state['valence'] -= 0.1
        
        # Arousal based on query complexity
        query_complexity = len(set(query.split())) / max(1, len(query.split()))
        self.emotional_state['arousal'] = 0.5 + query_complexity * 0.3
        
        # Dominance based on satisfaction
        self.emotional_state['dominance'] = 0.5 + (satisfaction - 0.5) * 0.4
        
        # Coherence (stability)
        self.emotional_state['coherence'] = 0.8 + (satisfaction - 0.5) * 0.2
        
        # 🔥 Curiosity increases with successful searches
        if search_success is not None:
            if search_success:
                self.emotional_state['curiosity'] = min(1.0, 
                    self.emotional_state['curiosity'] + 0.1)
            else:
                self.emotional_state['curiosity'] = max(0.1,
                    self.emotional_state['curiosity'] - 0.05)
        
        # Limit values
        for key in ['valence', 'arousal', 'dominance', 'coherence', 'curiosity']:
            if key in self.emotional_state:
                self.emotional_state[key] = max(0.1, min(1.0, self.emotional_state[key]))
        
        self.emotional_state['last_update'] = datetime.now().isoformat()
    
    # 🔥 Should admit ignorance based on frustration and failures
    def should_admit_ignorance(self, topic: str) -> bool:
        """Determines if system should admit not knowing something"""
        
        # If topic has failed multiple times
        if self.failed_topics.get(topic, 0) >= 2:
            return True
        
        # If frustration is high and patience is low
        if (self.emotional_state['frustration'] > 0.5 and 
            self.emotional_state['patience'] < 0.4):
            return True
        
        # If topic is in difficult topics list
        if topic in self.user_preferences['difficult_topics']:
            return True
        
        return False
    
    # 🔥 Get appropriate "I don't know" response
    def get_ignorance_response(self, topic: str, lang: str = 'es') -> str:
        """Returns an appropriate response when system doesn't know something"""
        
        responses = {
            'es': [
                f"No tengo información específica sobre {topic}. ¿Te interesaría saber sobre otro tema?",
                f"{topic} no está en mi base de conocimiento actual. ¿Puedo ayudarte con otra cosa?",
                f"Lo siento, no encuentro información sobre {topic}. ¿Quieres preguntar sobre algo diferente?",
                f"{topic} parece ser un tema especializado que no conozco bien. ¿Qué más te gustaría saber?"
            ],
            'en': [
                f"I don't have specific information about {topic}. Would you be interested in another topic?",
                f"{topic} is not in my current knowledge base. Can I help you with something else?",
                f"Sorry, I can't find information about {topic}. Would you like to ask about something different?",
                f"{topic} seems to be a specialized topic I don't know well. What else would you like to know?"
            ],
            'ca': [
                f"No tinc informació específica sobre {topic}. T'interessaria un altre tema?",
                f"{topic} no està a la meva base de coneixement actual. Puc ajudar-te amb una altra cosa?",
                f"Ho sento, no trobo informació sobre {topic}. Vols preguntar sobre alguna cosa diferent?",
                f"{topic} sembla un tema especialitzat que no conec bé. Què més t'agradaria saber?"
            ]
        }
        
        return random.choice(responses.get(lang, responses['en']))
    
    def learn_from_feedback(self, state: str, action: str, reward: float):
        """
        Reinforcement learning Q-learning
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
        """
        # Q-learning update
        old_q = self.q_matrix[state][action]
        
        # Best Q for next state (max)
        next_max = max(self.q_matrix[state].values()) if self.q_matrix[state] else 0
        
        # Update
        new_q = old_q + self.learning_rate * (reward + self.discount_factor * next_max - old_q)
        self.q_matrix[state][action] = new_q
        
        # Gradually reduce exploration
        self.exploration_rate = max(0.05, self.exploration_rate * 0.999)
    
    def choose_action(self, state: str, possible_actions: List[str]) -> str:
        """
        Chooses action based on epsilon-greedy policy
        
        Args:
            state: Current state
            possible_actions: Possible actions
        
        Returns:
            Selected action
        """
        # Exploration
        if random.random() < self.exploration_rate:
            return random.choice(possible_actions)
        
        # Exploitation (best Q)
        best_action = None
        best_q = -float('inf')
        
        for action in possible_actions:
            q = self.q_matrix[state].get(action, 0)
            if q > best_q:
                best_q = q
                best_action = action
        
        return best_action or random.choice(possible_actions)
    
    def get_personality_summary(self) -> str:
        """Returns readable personality summary"""
        persona = self.get_persona()
        
        lines = []
        lines.append(f"🎭 **Dominant Archetype**: {persona['archetype']}")
        lines.append(f"🎨 **Tone**: {persona['style']['tone']}")
        lines.append(f"📊 **Personality Vector**:")
        
        # Personality bars
        for i, val in enumerate(self.personality_vector):
            bar = '█' * int(val * 20) + '░' * (20 - int(val * 20))
            lines.append(f"   S{i+1}: {bar} {val:.2f}")
        
        lines.append(f"\n😊 **Emotional State**:")
        lines.append(f"   Valence: {self.emotional_state['valence']:.2f} " +
                    f"({'positive' if self.emotional_state['valence'] > 0.6 else 'negative' if self.emotional_state['valence'] < 0.4 else 'neutral'})")
        lines.append(f"   Arousal: {self.emotional_state['arousal']:.2f}")
        lines.append(f"   Coherence: {self.emotional_state['coherence']:.2f}")
        lines.append(f"   Frustration: {self.emotional_state['frustration']:.2f}")
        lines.append(f"   Curiosity: {self.emotional_state['curiosity']:.2f}")
        lines.append(f"   Patience: {self.emotional_state['patience']:.2f}")
        
        lines.append(f"\n📈 **Stats**:")
        lines.append(f"   Consecutive failures: {self.consecutive_failures}")
        lines.append(f"   Known interests: {len(self.user_preferences['known_interests'])}")
        lines.append(f"   Difficult topics: {len(self.user_preferences['difficult_topics'])}")
        
        return '\n'.join(lines)