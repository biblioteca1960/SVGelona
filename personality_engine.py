"""
personality/personality_engine.py
Complete personality engine integrating all components
IMPROVED VERSION: Connected with search success/failure
"""

from .personality_core import PersonalityCore
from .emotional_memory import EmotionalMemory
from .response_styler import ResponseStyler
from typing import Dict, Optional
import random

class PersonalityEngine:
    """
    Complete personality engine integrating:
    - Personality core
    - Emotional memory
    - Response styler
    - 🔥 Search success/failure tracking
    """
    
    def __init__(self, symmetries, user_id="default"):
        self.core = PersonalityCore(symmetries, user_id)
        self.memory = EmotionalMemory()
        self.styler = ResponseStyler()
        
        # Conversation state
        self.conversation_mood = 0.5  # 0-1
        self.last_emotion = None
        
        # 🔥 Search tracking
        self.search_attempts = 0
        self.search_successes = 0
        self.search_failures = 0
        
        print(f"  ✅ PersonalityEngine ready for '{user_id}'")
        print(f"     🔍 Search tracking: ENABLED")
    
    def process_interaction(self, query: str, response: str, 
                           user_reaction: str = None,
                           search_success: bool = None,
                           search_topic: str = None) -> Dict:
        """
        Processes a complete interaction
        
        Args:
            query: User query
            response: System response
            user_reaction: User reaction (optional)
            search_success: Whether search was successful
            search_topic: Topic that was searched
        
        Returns:
            Personality information for response
        """
        # Estimate satisfaction
        satisfaction = self._estimate_satisfaction(query, response, user_reaction, search_success)
        
        # 🔥 Update search statistics
        if search_success is not None:
            self.search_attempts += 1
            if search_success:
                self.search_successes += 1
            else:
                self.search_failures += 1
        
        # Update core
        self.core.update_from_interaction(
            query, response, 
            user_reaction, satisfaction,
            search_success, search_topic
        )
        
        # Update emotional memory if significant
        if user_reaction or len(query) > 50:
            self._store_emotional_memory(query, response, user_reaction, search_success)
        
        # Get current persona
        persona = self.core.get_persona()
        
        # Update conversation mood
        self._update_conversation_mood(user_reaction, search_success)
        
        # Add search statistics to persona
        persona['search_stats'] = {
            'attempts': self.search_attempts,
            'successes': self.search_successes,
            'failures': self.search_failures,
            'success_rate': self.search_successes / max(1, self.search_attempts)
        }
        
        # Retrieve relevant emotional memory
        emotional_recall = self.memory.recall_by_context(persona['emotional_state'])
        if emotional_recall:
            persona['emotional_recall'] = emotional_recall
        
        return persona
    
    def _estimate_satisfaction(self, query: str, response: str, 
                               user_reaction: str, search_success: bool) -> float:
        """Estimates user satisfaction"""
        if user_reaction == 'positive':
            return 0.9
        elif user_reaction == 'negative':
            return 0.2
        
        # Estimation based on response and query length
        base = 0.5
        
        # Very short responses may be unsatisfactory
        if len(response) < 50:
            base -= 0.1
        
        # Long queries are usually more important
        if len(query) > 100:
            base += 0.1
        
        # 🔥 Successful searches increase satisfaction
        if search_success:
            base += 0.2
        elif search_success is False:
            base -= 0.1
        
        return max(0.1, min(1.0, base))
    
    def _store_emotional_memory(self, query: str, response: str, 
                                 user_reaction: str, search_success: bool):
        """Stores emotional memory if relevant"""
        intensity = 0.7 if user_reaction else 0.4
        
        # 🔥 Successful searches are more memorable
        if search_success:
            intensity += 0.2
        
        # Detect dominant emotion
        emotion = self._detect_emotion(query, user_reaction)
        
        self.memory.add_memory(
            content=query[:100],
            emotions=[emotion],
            intensity=intensity,
            context={
                'response': response[:100],
                'user_reaction': user_reaction,
                'search_success': search_success
            }
        )
    
    def _detect_emotion(self, text: str, user_reaction: str) -> str:
        """Detects dominant emotion in text"""
        text_lower = text.lower()
        
        # Emotion keywords
        emotion_keywords = {
            'joy': ['happy', 'glad', 'great', 'wonderful', 'excellent'],
            'trust': ['trust', 'believe', 'confident', 'sure'],
            'fear': ['scared', 'afraid', 'worried', 'anxious'],
            'surprise': ['wow', 'surprised', 'amazing', 'incredible'],
            'sadness': ['sad', 'unfortunate', 'sorry', 'regret'],
            'anger': ['angry', 'frustrated', 'annoyed', 'mad'],
            'anticipation': ['hope', 'expect', 'anticipate', 'soon']
        }
        
        # If explicit reaction
        if user_reaction == 'positive':
            return 'joy'
        elif user_reaction == 'negative':
            return 'sadness'
        
        # Detect by keywords
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return emotion
        
        return 'neutral'
    
    def _update_conversation_mood(self, user_reaction: str, search_success: bool):
        """Updates conversation mood"""
        if user_reaction == 'positive':
            self.conversation_mood += 0.1
        elif user_reaction == 'negative':
            self.conversation_mood -= 0.1
        
        # 🔥 Search success improves mood
        if search_success:
            self.conversation_mood += 0.05
        elif search_success is False:
            self.conversation_mood -= 0.05
        
        self.conversation_mood = max(0.1, min(1.0, self.conversation_mood))
    
    def style_response(self, text: str) -> str:
        """
        Applies personality style to a response
        
        Args:
            text: Original text
        
        Returns:
            Styled text
        """
        persona = self.core.get_persona()
        return self.styler.apply_style(text, persona)
    
    def get_greeting(self) -> str:
        """Returns personalized greeting"""
        persona = self.core.get_persona()
        return self.styler.get_greeting(persona)
    
    def should_express_emotion(self) -> bool:
        """Determines if emotion should be expressed at this moment"""
        persona = self.core.get_persona()
        
        # Express emotion based on personality and state
        emotional_threshold = 0.5
        
        if persona['style']['empathy'] > 0.7:
            emotional_threshold = 0.3
        
        if persona['emotional_state']['arousal'] > 0.7:
            emotional_threshold = 0.4
        
        # 🔥 High frustration increases chance of expressing emotion
        if persona['emotional_state'].get('frustration', 0) > 0.5:
            emotional_threshold = 0.3
        
        return random.random() > emotional_threshold
    
    # 🔥 NEW: Should admit ignorance
    def should_admit_ignorance(self, topic: str) -> bool:
        """Determines if system should admit not knowing something"""
        return self.core.should_admit_ignorance(topic)
    
    # 🔥 NEW: Get ignorance response
    def get_ignorance_response(self, topic: str, lang: str = 'es') -> str:
        """Returns appropriate response when system doesn't know something"""
        return self.core.get_ignorance_response(topic, lang)
    
    def get_personality_summary(self) -> str:
        """Returns complete personality summary"""
        core_summary = self.core.get_personality_summary()
        emotional_summary = self.memory.get_emotional_summary()
        
        search_stats = f"\n📊 **Search Statistics**:\n"
        search_stats += f"   Attempts: {self.search_attempts}\n"
        search_stats += f"   Success rate: {self.search_successes/max(1,self.search_attempts):.1%}"
        
        return f"{core_summary}\n\n{emotional_summary}\n{search_stats}"