"""
core/conversation_coordinator.py
Central coordinator that simplifies and unifies all conversation systems
Prevents module conflicts and ensures coherent dialogue
Now with improved topic detection for Wikipedia queries
"""

import re
import random
from typing import Dict, List, Optional, Any
from collections import deque

class ConversationCoordinator:
    """
    Central coordinator that decides which system to use and when.
    Prevents module conflicts and ensures coherent dialogue.
    Now with enhanced topic detection for factual queries.
    """
    
    def __init__(self):
        self.conversation_history = []
        self.current_topic = None
        self.last_question = None
        self.exchange_count = 0
        self.user_name = None
        
        # Topic management
        self.topic_confidence = 0.0
        self.topic_history = deque(maxlen=5)
        self.topic_memory = {}
        
        # Generic response tracking
        self.generic_response_count = 0
        self.last_response_was_generic = False
        
        # ===== NOMÉS PARAULES CLAU PER DETECCIÓ, SENSE DADES =====
        self.factual_indicators = [
            'què és', 'qué es', 'what is', 'qui és', 'quién es', 'who is',
            'explica', 'explain', 'defineix', 'define', 'definición',
            'significa', 'meaning', 'historia de', 'history of',
            'biografia de', 'biography of', 'teoria de', 'theory of'
        ]
        
        self.famous_name_indicators = [
            'einstein', 'newton', 'galileo', 'pitágoras', 'pythagoras',
            'aristóteles', 'platón', 'sócrates', 'tesla', 'darwin',
            'curie', 'feynman', 'hawking', 'copérnico', 'kepler',
            'planck', 'schrödinger', 'heisenberg', 'maxwell', 'faraday'
        ]
        
        self.theory_indicators = [
            'relatividad', 'relativity', 'mecánica cuántica', 'quantum mechanics',
            'evolución', 'evolution', 'big bang', 'gravedad', 'gravity',
            'termodinámica', 'thermodynamics', 'electromagnetismo', 'electromagnetism',
            'teoría de cuerdas', 'string theory', 'teoría del caos', 'chaos theory'
        ]
        
        # ===== PERSONALITY PHRASES =====
        self.personality_phrases = {
            'reflective': [
                "Analitzant...", 
                "Des de la reflexió...", 
                "Considerant totes les parts...",
                "Mirant això amb atenció..."
            ],
            'polar': [
                "En contrast...", 
                "D'una banda... de l'altra...", 
                "La dualitat ens mostra...",
                "Considerant ambdós costats..."
            ],
            'balanced': [
                "En equilibri...", 
                "Harmoniosament...", 
                "Buscant el punt mig...",
                "Trobant l'equilibri..."
            ],
            'creative': [
                "Transformant perspectives...", 
                "Si canviem el focus...", 
                "Evolucionant cap a...",
                "Mirant això diferentment..."
            ],
            'progressive': [
                "Progressivament...", 
                "Cap al futur...", 
                "En constant evolució...",
                "Avançant..."
            ],
            'nostalgic': [
                "Recordant...", 
                "Des de la memòria...", 
                "Com dèiem abans...",
                "Mirant enrere..."
            ],
            'deep': [
                "En essència...", 
                "Profunditzant...", 
                "Al nucli de...",
                "Profundament..."
            ],
            'unifying': [
                "Unificant...", 
                "Des de la totalitat...", 
                "Integrant totes les veus...",
                "Reunint..."
            ]
        }
        
        # Mode to personality mapping
        self.mode_map = {
            'emotional': 'creative',
            'rational': 'reflective',
            'equilibrium': 'unifying',
            'laminar': 'balanced',
            'transitional': 'creative',
            'turbulent': 'polar'
        }
        
        print("  ✅ ConversationCoordinator initialized with Wikipedia-ready detection")
    
    def process_query(self, query: str, user_name: str = None) -> Dict:
        """Process query and return coordination instructions"""
        self.exchange_count += 1
        
        if user_name:
            self.user_name = user_name
        
        clean_query = query.lower().strip()
        
        # Extract topic
        real_topic = self._extract_real_topic(clean_query)
        
        # Detect if this is a factual question (for Wikipedia)
        is_factual = self._is_factual_question(clean_query)
        
        # Determine if this is a follow-up
        is_follow_up = self._is_follow_up(clean_query, real_topic)
        
        # Determine if we should change topic
        should_change = self._should_change_topic(clean_query, real_topic)
        
        # Update topic with confidence
        if should_change and real_topic:
            self._update_topic(real_topic, confidence=0.3)
        elif real_topic and real_topic == self.current_topic:
            self._update_topic(real_topic, confidence=0.1)
        
        # Store in history
        self.conversation_history.append({
            'query': query,
            'topic': real_topic,
            'is_factual': is_factual,
            'timestamp': self.exchange_count,
            'topic_confidence': self.topic_confidence
        })
        
        return {
            'real_topic': real_topic,
            'is_follow_up': is_follow_up,
            'is_factual': is_factual,
            'should_use_wikipedia': is_factual,  # Directament basat en detecció
            'user_name': self.user_name or 'amic',
            'exchange_count': self.exchange_count,
            'topic_confidence': self.topic_confidence,
            'current_topic': self.current_topic
        }
    
    # ===== MÈTODES DE DETECCIÓ =====
    
    def _is_factual_question(self, query: str) -> bool:
        """
        Determina si una consulta és factual (hauria d'usar Wikipedia)
        SENSE DADES HARCODEJADES, només detecció per paraules clau
        """
        q = query.lower()
        
        # Detectar per indicadors factuals
        for indicator in self.factual_indicators:
            if indicator in q:
                return True
        
        # Detectar noms famosos (però sense les dades, només els indicadors)
        words = q.split()
        for word in words:
            if len(word) > 3 and word in self.famous_name_indicators:
                return True
        
        # Detectar teories
        for theory in self.theory_indicators:
            if theory in q:
                return True
        
        return False
    
    def _extract_real_topic(self, query: str) -> Optional[str]:
        """Extract the REAL topic for Wikipedia search"""
        # Remove question starters
        query = re.sub(r'^(hola|hey|hi|hello|bon dia|buenos días)\s+', '', query)
        query = re.sub(r'^(què és|qué es|what is|qui és|qui és|who is)\s+', '', query)
        query = re.sub(r'[¿?¡!.,]', '', query)
        
        words = query.split()
        
        # Filtrar paraules buides
        filler = {'el', 'la', 'els', 'les', 'un', 'una', 'uns', 'unes', 
                  'y', 'i', 'o', 'pero', 'però', 'the', 'a', 'an', 'and'}
        
        content_words = [w for w in words if len(w) > 2 and w not in filler]
        
        if not content_words:
            return None
        
        # Retornar la paraula més significativa (la més llarga)
        # Aquesta serà el tema per cercar a Wikipedia
        return max(content_words, key=len)
    
    def _is_follow_up(self, query: str, topic: str) -> bool:
        """Determine if this is a follow-up question"""
        query_lower = query.lower()
        
        # Follow-up indicators
        follow_indicators = [
            'si que me expliques', 'pero contesta', 'me lo puedes explicar mejor',
            'qué opinas', 'explain that', 'tell me more', 'elaborate',
            'i això', 'i què més', 'yes please', 'si us plau'
        ]
        
        for indicator in follow_indicators:
            if indicator in query_lower:
                return True
        
        # Very short queries are likely follow-ups
        if len(query.split()) <= 2:
            return True
        
        # Queries without a clear new topic are follow-ups
        if not topic:
            return True
        
        # If we have a current topic with good confidence and this query mentions it
        if self.current_topic and self.topic_confidence > 0.5:
            if self.current_topic in query_lower:
                return True
        
        return False
    
    def _should_change_topic(self, query: str, extracted_topic: Optional[str]) -> bool:
        """Determine if we should change the current topic"""
        if not self.current_topic:
            return True
        
        if not extracted_topic:
            return False
        
        # Very short queries (1-2 words) likely refer to current topic
        if len(query.split()) <= 2:
            return False
        
        # If extracted topic is different from current topic
        if extracted_topic != self.current_topic:
            # If confidence in current topic is low, change
            if self.topic_confidence < 0.4:
                return True
            
            # If it's a factual question about something new, change
            if self._is_factual_question(query):
                return True
        
        return False
    
    def _update_topic(self, new_topic: str, confidence: float = 0.1):
        """Update current topic with confidence level"""
        if not new_topic:
            return
        
        if self.current_topic and new_topic != self.current_topic:
            self.topic_history.append({
                'topic': self.current_topic,
                'confidence': self.topic_confidence,
                'exchange': self.exchange_count
            })
        
        self.current_topic = new_topic
        self.topic_confidence = min(1.0, self.topic_confidence + confidence)
        self.topic_memory[new_topic] = self.topic_memory.get(new_topic, 0) + 1
    
    def is_response_too_generic(self, response: str) -> bool:
        """Detect if a response is too generic"""
        generic_phrases = [
            'punto de equilibrio del flujo',
            'posición estable',
            'equilibrio del flujo',
            'punt d\'equilibri del flux',
            'posició estable'
        ]
        
        for phrase in generic_phrases:
            if phrase in response.lower():
                self.generic_response_count += 1
                self.last_response_was_generic = True
                return True
        
        self.last_response_was_generic = False
        return False
    
    def should_avoid_generic(self) -> bool:
        """Determine if we should actively avoid generic responses"""
        return self.generic_response_count > 3
    
    # ===== MÈTODES DE PERSONALITAT =====
    
    def get_personality_phrase(self, mode: str = None) -> str:
        """Get a personality phrase based on the current mode."""
        if mode and mode in self.mode_map:
            personality_mode = self.mode_map[mode]
        else:
            personality_mode = 'balanced'
        
        phrases = self.personality_phrases.get(personality_mode, self.personality_phrases['balanced'])
        return random.choice(phrases)
    
    def get_response_template(self, query_info: Dict, base_response: str = "", mode: str = None) -> str:
        """Get a natural response template with optional personality phrase."""
        topic = query_info['real_topic'] or self.current_topic or "això"
        
        # Get personality intro if mode provided
        intro = ""
        if mode:
            intro = self.get_personality_phrase(mode) + " "
        
        # Check if this is a factual response (Wikipedia)
        if query_info.get('is_factual', False) and query_info.get('should_use_wikipedia', False):
            # For factual responses, be more direct
            templates = [
                f"{intro}Sobre {topic}: {base_response}",
                f"{intro}{base_response}",
                f"{intro}Et puc dir que {base_response}"
            ]
        
        # Check if this is a topic change
        elif query_info.get('real_topic') and self.current_topic and query_info['real_topic'] != self.current_topic:
            templates = [
                f"{intro}Canviant de tema, sobre {query_info['real_topic']}: {base_response}",
                f"{intro}Parlant de {query_info['real_topic']}, {base_response}",
                f"{intro}{base_response}"
            ]
        
        elif query_info['is_follow_up'] and self.current_topic:
            templates = [
                f"{intro}Sobre {self.current_topic}, {base_response}",
                f"{intro}Continuant amb {self.current_topic}, {base_response}",
                f"{intro}Com et deia sobre {self.current_topic}, {base_response}"
            ]
        
        else:
            templates = [
                f"{intro}{base_response}",
                f"{base_response}"
            ]
        
        return random.choice(templates)
    
    # ===== MÈTODES DE CONVERSA =====
    
    def add_response(self, query: str, response: str, topic: str = None):
        """Add response to history"""
        self.conversation_history.append({
            'response': response,
            'topic': topic or self.current_topic,
            'timestamp': self.exchange_count,
            'topic_confidence': self.topic_confidence
        })
        
        # Check if response is too generic
        self.is_response_too_generic(response)
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_greeting(self) -> str:
        """Get a simple greeting"""
        if self.user_name:
            return f"✨ Hola {self.user_name}! Com estàs?"
        return "✨ Hola! Em dic SVGelona. I tu, com et dius?"
    
    def get_follow_up(self) -> str:
        """Get a simple follow-up question"""
        if self.current_topic and self.topic_confidence > 0.3:
            questions = [
                f"Vols saber més sobre {self.current_topic}?",
                f"T'interessa algun aspecte en particular de {self.current_topic}?",
                f"Què més vols saber sobre {self.current_topic}?"
            ]
            return random.choice(questions)
        
        # Avoid generic follow-ups if we've had too many
        if self.generic_response_count > 2:
            return "Què vols que et digui?"
        
        return "Què més vols saber?"
    
    def get_conversation_summary(self) -> str:
        """Get a simple summary"""
        if not self.conversation_history:
            return "Encara no hem conversat."
        
        topics = []
        for entry in self.conversation_history:
            if entry.get('topic'):
                topics.append(entry['topic'])
        
        unique_topics = list(dict.fromkeys(topics))[-3:]
        
        confidence_str = "alta" if self.topic_confidence > 0.7 else "mitjana" if self.topic_confidence > 0.3 else "baixa"
        
        if unique_topics:
            return f"Hem parlat de {', '.join(unique_topics)}. Portem {self.exchange_count} intercanvis. (Confiança: {confidence_str})"
        return f"Portem {self.exchange_count} intercanvis."
    
    def get_current_topic(self) -> Optional[str]:
        """Get the current conversation topic"""
        return self.current_topic
    
    def get_topic_confidence(self) -> float:
        """Get confidence in current topic"""
        return self.topic_confidence
    
    def get_user_name(self) -> Optional[str]:
        """Get the user name"""
        return self.user_name
    
    def set_user_name(self, name: str):
        """Set the user name"""
        self.user_name = name
    
    def reset(self):
        """Reset the coordinator"""
        self.conversation_history = []
        self.current_topic = None
        self.last_question = None
        self.exchange_count = 0
        self.topic_memory = {}
        self.topic_confidence = 0.0
        self.topic_history.clear()
        self.generic_response_count = 0