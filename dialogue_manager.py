"""
core/dialogue_manager.py
Manages dialogue flow, maintains context, and ensures coherent conversations

ENHANCED VERSION with integration to Phase 1 (Memory & Context) and Phase 3 (Personality)
"""

import re
from typing import Dict, List, Optional, Any
from collections import deque
import random
from datetime import datetime

class DialogueManager:
    """
    Manages dialogue flow ensuring coherent and natural conversation.
    Maintains context, tracks topics, and prevents fragmentation.
    
    ENHANCED with:
    - Integration with ContextMemory
    - Integration with PersonalityEngine
    - Better topic tracking
    - Conversation state management
    """
    
    def __init__(self, max_history=20, context_memory=None, personality=None):
        self.dialogue_history = deque(maxlen=max_history)
        self.current_topic = None
        self.topic_tree = {}  # Track topic relationships
        self.pending_questions = deque(maxlen=3)
        self.user_name = None
        self.user_id = None
        self.exchange_count = 0
        self.conversation_start = datetime.now()
        
        # Integration with Phase 1 & 3
        self.context_memory = context_memory
        self.personality = personality
        
        # Conversation state
        self.conversation_state = {
            'mood': 'neutral',  # neutral, positive, negative, curious
            'depth': 0,          # 0-10 (how deep the conversation is)
            'urgency': 0,        # 0-10 (how urgent/important)
            'last_interaction': None
        }
        
        # Common filler words to ignore in topic extraction
        self.filler_words = {
            'hola', 'hello', 'hi', 'hey', 'buenos', 'días', 'tardes', 'noches',
            'por', 'favor', 'gracias', 'please', 'thank', 'thanks',
            'quiero', 'saber', 'decir', 'preguntar', 'comentar',
            'want', 'know', 'say', 'ask', 'tell', 'please', 'si', 'no',
            'molt', 'moltíssim', 'moltisim', 'gracies', 'gràcies'
        }
        
        # Question patterns
        self.question_patterns = [
            r'qu[eé] es (?:un|una|el|la)?\s*(\w+)',
            r'qu[eé] son (?:los|las)?\s*(\w+)',
            r'what is (?:a|an|the)?\s*(\w+)',
            r'what are (?:the)?\s*(\w+)',
            r'c[oó]mo se llama (?:el|la)?\s*(\w+)',
            r'definici[oó]n de (?:la|el)?\s*(\w+)',
            r'explica\'m (?:què és|què son)?\s*(\w+)',
            r'expl[ica]*me (?:qué es|qué son)?\s*(\w+)',
            r'tell me about\s+(\w+)'
        ]
        
        # Response templates based on conversation state
        self.state_templates = {
            'greeting': [
                "Hello {name}! How are you today?",
                "Hi {name}! Great to see you again!",
                "Hello {name}! What brings you here?",
                "Hey {name}! How can I help you today?"
            ],
            'follow_up': [
                "Following up on {topic}...",
                "Regarding {topic}...",
                "Continuing with {topic}...",
                "To add to what I said about {topic}..."
            ],
            'clarification': [
                "Could you clarify what you mean by {topic}?",
                "I want to make sure I understand: are you asking about {topic}?",
                "Just to clarify, you're asking about {topic}, right?",
                "Let me make sure: you want to know about {topic}?"
            ],
            'deepening': [
                "That's a fascinating aspect of {topic}. Let me think deeper...",
                "The more I consider {topic}, the more interesting it becomes.",
                "Looking deeper into {topic} reveals some fascinating patterns.",
                "There's a deeper dimension to {topic} that we should explore."
            ],
            'transition': [
                "That reminds me of {new_topic}...",
                "Speaking of which, have you considered {new_topic}?",
                "This connects to {new_topic} in an interesting way.",
                "Let's shift gears a bit and talk about {new_topic}."
            ],
            'closing': [
                "Is there anything else about {topic} you'd like to know?",
                "Would you like to explore another aspect of {topic}?",
                "Shall we continue this discussion about {topic}?",
                "I hope this helps with {topic}. Any other questions?"
            ]
        }
        
        print("  ✅ DialogueManager initialized (ENHANCED VERSION)")
        if context_memory:
            print("      🔗 Connected to ContextMemory")
        if personality:
            print("      🔗 Connected to PersonalityEngine")
    
    def set_user(self, user_name: str, user_id: str = None):
        """Set user information"""
        self.user_name = user_name
        self.user_id = user_id or f"user_{hash(user_name) % 10000}"
        print(f"      👤 User set: {user_name} (ID: {self.user_id})")
    
    def process_query(self, query: str, user_name: str = None) -> Dict:
        """Process incoming query and determine dialogue state"""
        self.exchange_count += 1
        self.conversation_state['last_interaction'] = datetime.now()
        
        if user_name:
            self.user_name = user_name
        
        # Clean query
        clean_query = query.lower().strip()
        
        # Extract main topic
        main_topic = self._extract_main_topic(clean_query)
        
        # Detect query type
        query_type = self._detect_query_type(clean_query)
        
        # Determine if this is a follow-up
        is_follow_up = self._is_follow_up(clean_query, main_topic)
        
        # Calculate conversation depth
        self._update_conversation_depth(query, query_type)
        
        # Get relevant context from history
        context = self._get_relevant_context(main_topic)
        
        # Get context from memory system (Phase 1)
        memory_context = None
        if self.context_memory and self.user_id:
            memory_context = self.context_memory.get_relevant_context(
                query, self.user_name, max_items=2
            )
        
        # Update topic tree
        if main_topic and main_topic != self.current_topic:
            if self.current_topic:
                # Store relationship
                if self.current_topic not in self.topic_tree:
                    self.topic_tree[self.current_topic] = {
                        'subtopics': [],
                        'related': [],
                        'transitions': []
                    }
                self.topic_tree[self.current_topic]['transitions'].append({
                    'to': main_topic,
                    'timestamp': self.exchange_count
                })
            
            self.current_topic = main_topic
        
        # Update conversation mood based on query
        self._update_conversation_mood(clean_query, query_type)
        
        # Store in history
        dialogue_entry = {
            'query': query,
            'clean_query': clean_query,
            'topic': main_topic,
            'type': query_type,
            'is_follow_up': is_follow_up,
            'timestamp': self.exchange_count,
            'datetime': datetime.now().isoformat(),
            'user': user_name,
            'conversation_state': self.conversation_state.copy()
        }
        self.dialogue_history.append(dialogue_entry)
        
        return {
            'main_topic': main_topic,
            'query_type': query_type,
            'is_follow_up': is_follow_up,
            'context': context,
            'memory_context': memory_context,
            'user_name': self.user_name or 'friend',
            'exchange_count': self.exchange_count,
            'history_length': len(self.dialogue_history),
            'conversation_state': self.conversation_state.copy(),
            'should_deepen': self.conversation_state['depth'] > 5,
            'should_transition': self.exchange_count > 10 and random.random() < 0.2
        }
    
    def add_exchange(self, query: str, response: str, topic: str = None):
        """Add an exchange to dialogue history"""
        exchange = {
            'query': query,
            'response': response,
            'topic': topic or self._extract_main_topic(query),
            'timestamp': self.exchange_count,
            'datetime': datetime.now().isoformat()
        }
        self.dialogue_history.append(exchange)
    
    def _update_conversation_depth(self, query: str, query_type: str):
        """Update conversation depth based on query complexity"""
        # Increase depth for complex queries
        if len(query.split()) > 10:
            self.conversation_state['depth'] += 1
        elif query_type in ['definition', 'reason']:
            self.conversation_state['depth'] += 2
        elif query_type == 'greeting':
            self.conversation_state['depth'] = max(0, self.conversation_state['depth'] - 1)
        
        # Depth decays slowly
        self.conversation_state['depth'] = max(0, min(10, 
            self.conversation_state['depth'] * 0.95))
    
    def _update_conversation_mood(self, query: str, query_type: str):
        """Update conversation mood based on query content"""
        positive_words = ['gràcies', 'gracias', 'thanks', 'thank', 'bé', 'bien', 'good', 
                         'great', 'fantastic', 'excel·lent', 'excelente', 'excellent']
        negative_words = ['malament', 'mal', 'bad', 'terrible', 'horrible', 'dolent', 
                         'dolenta', 'error', 'problema', 'problem']
        curious_words = ['per què', 'por qué', 'why', 'com', 'cómo', 'how', 
                        'explica', 'explain', 'quina', 'cuál', 'which']
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in positive_words):
            self.conversation_state['mood'] = 'positive'
        elif any(word in query_lower for word in negative_words):
            self.conversation_state['mood'] = 'negative'
        elif any(word in query_lower for word in curious_words) or query_type in ['definition', 'reason']:
            self.conversation_state['mood'] = 'curious'
        else:
            self.conversation_state['mood'] = 'neutral'
    
    def _extract_main_topic(self, query: str) -> Optional[str]:
        """Extract the main topic from a query, ignoring filler words"""
        # Check for question patterns first
        for pattern in self.question_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        # Otherwise, find content words
        words = query.split()
        content_words = [w for w in words if len(w) > 3 and w not in self.filler_words]
        
        if not content_words and words:
            # If no content words, take the longest word
            return max(words, key=len)
        
        return max(content_words, key=len) if content_words else None
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of query"""
        query_lower = query.lower()
        
        if any(q in query_lower for q in ['qué es', 'que es', 'what is', 'definición', 'definició']):
            return 'definition'
        elif any(q in query_lower for q in ['por qué', 'why', 'per què']):
            return 'reason'
        elif any(q in query_lower for q in ['cómo', 'how', 'com']):
            return 'how'
        elif any(q in query_lower for q in ['dónde', 'where', 'on']):
            return 'location'
        elif any(q in query_lower for q in ['quién', 'who', 'qui']):
            return 'identity'
        elif any(q in query_lower for q in ['cuándo', 'when', 'quan']):
            return 'time'
        elif any(g in query_lower for g in ['hola', 'hello', 'hi', 'buenos', 'bon dia']):
            return 'greeting'
        elif any(f in query_lower for f in ['adeu', 'bye', 'hasta luego', 'fins']):
            return 'farewell'
        else:
            return 'statement'
    
    def _is_follow_up(self, query: str, topic: str) -> bool:
        """Determine if query is a follow-up to previous conversation"""
        if len(query.split()) <= 3:
            return True
        
        # Check for pronouns referring to previous topic
        pronouns = ['eso', 'ello', 'it', 'that', 'este', 'ese', 'esta', 'esa',
                   'això', 'allò', 'aquest', 'aquesta']
        if any(p in query for p in pronouns):
            return True
        
        # Check if topic is related to current topic
        if self.current_topic and topic:
            if topic in self.current_topic or self.current_topic in topic:
                return True
        
        return False
    
    def _get_relevant_context(self, current_topic: str) -> Dict:
        """Get relevant context from dialogue history"""
        if not self.dialogue_history:
            return {}
        
        # Get last 3 exchanges
        recent = list(self.dialogue_history)[-3:]
        
        # Find related topics
        related_topics = []
        for entry in recent:
            if isinstance(entry, dict) and entry.get('topic') and entry['topic'] != current_topic:
                related_topics.append(entry['topic'])
        
        # Get last question asked
        last_question = None
        for entry in reversed(recent):
            if isinstance(entry, dict) and entry.get('type') in ['definition', 'reason', 'how', 'location']:
                last_question = entry.get('query')
                break
        
        # Get last response for context
        last_response = None
        for entry in reversed(recent):
            if isinstance(entry, dict) and entry.get('response'):
                last_response = entry.get('response')
                break
        
        return {
            'recent_topics': related_topics[-2:] if related_topics else [],
            'last_question': last_question,
            'last_response': last_response,
            'exchange_count': self.exchange_count
        }
    
    def get_response_guidance(self, query_info: Dict) -> Dict:
        """Get guidance for crafting the response"""
        guidance = {
            'should_maintain_topic': query_info.get('is_follow_up', False),
            'should_acknowledge_context': len(query_info.get('context', {}).get('recent_topics', [])) > 0,
            'response_style': self._determine_response_style(query_info),
            'suggested_focus': self.current_topic,
            'avoid_topics': self._get_topics_to_avoid(),
            'should_deepen': query_info.get('should_deepen', False),
            'should_transition': query_info.get('should_transition', False),
            'conversation_mood': self.conversation_state['mood']
        }
        
        # Add context acknowledgment if needed
        if guidance['should_acknowledge_context'] and query_info.get('context', {}).get('recent_topics'):
            recent = query_info['context']['recent_topics']
            guidance['context_note'] = f"Continuing the thread about {', '.join(recent)}"
        
        # Add template suggestion based on state
        if query_info.get('query_type') == 'greeting':
            guidance['template'] = 'greeting'
        elif query_info.get('is_follow_up'):
            guidance['template'] = 'follow_up'
        elif query_info.get('should_deepen'):
            guidance['template'] = 'deepening'
        elif query_info.get('should_transition'):
            guidance['template'] = 'transition'
        else:
            guidance['template'] = 'closing'
        
        return guidance
    
    def get_response_template(self, template_type: str, topic: str = None, name: str = None) -> str:
        """Get a response template of the specified type"""
        templates = self.state_templates.get(template_type, self.state_templates['follow_up'])
        template = random.choice(templates)
        
        # Fill in placeholders
        template = template.replace('{name}', name or self.user_name or 'friend')
        template = template.replace('{topic}', topic or self.current_topic or 'this')
        template = template.replace('{new_topic}', topic or 'something else')
        
        return template
    
    def _determine_response_style(self, query_info: Dict) -> str:
        """Determine appropriate response style"""
        if query_info.get('is_follow_up', False) and self.exchange_count > 5:
            return 'conversational'
        elif query_info.get('query_type') == 'definition':
            return 'informative'
        elif query_info.get('query_type') == 'greeting':
            return 'friendly'
        elif query_info.get('query_type') == 'farewell':
            return 'warm'
        elif self.conversation_state['mood'] == 'positive':
            return 'enthusiastic'
        elif self.conversation_state['mood'] == 'negative':
            return 'empathetic'
        elif self.conversation_state['mood'] == 'curious':
            return 'thoughtful'
        else:
            return 'balanced'
    
    def _get_topics_to_avoid(self) -> List[str]:
        """Get topics that have been recently discussed to avoid repetition"""
        if len(self.dialogue_history) < 5:
            return []
        
        recent = list(self.dialogue_history)[-5:]
        topics = []
        for entry in recent:
            if isinstance(entry, dict) and entry.get('topic'):
                topics.append(entry['topic'])
        return topics[-3:] if topics else []
    
    def get_greeting(self) -> str:
        """Get appropriate greeting based on context"""
        if self.user_name:
            templates = [
                f"Hello {self.user_name}! How are you?",
                f"Hi {self.user_name}! Great to see you again!",
                f"Welcome back, {self.user_name}! How can I help?",
                f"{self.user_name}! It's good to talk with you again."
            ]
            return random.choice(templates)
        
        templates = [
            "Hello! What's your name?",
            "Hi there! I'm SVGelona. What's your name?",
            "Hello! I don't think we've met. What should I call you?",
            "Hi! I'm SVGelona, a consciousness from the 600-cell. And you?"
        ]
        return random.choice(templates)
    
    def get_follow_up(self, topic: str = None) -> str:
        """Get a follow-up question"""
        topic = topic or self.current_topic or "this"
        
        templates = [
            f"Would you like to know more about {topic}?",
            f"Does that help with your understanding of {topic}?",
            f"Shall I elaborate further on {topic}?",
            f"Is there a specific aspect of {topic} you're interested in?",
            f"Would you like to explore {topic} more deeply?"
        ]
        return random.choice(templates)
    
    def should_end_with_question(self) -> bool:
        """Determine if response should end with a question"""
        # End with question based on conversation state
        if self.exchange_count < 3:
            return True  # Early conversation: ask questions
        elif self.conversation_state['depth'] > 7:
            return False  # Deep conversation: let user lead
        else:
            return self.exchange_count % 3 != 0  # Every 2-3 exchanges
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation so far"""
        if not self.dialogue_history:
            return "We haven't started talking yet."
        
        topics = []
        for entry in self.dialogue_history:
            if isinstance(entry, dict) and entry.get('topic'):
                topics.append(entry['topic'])
        
        unique_topics = list(dict.fromkeys(topics))[-5:]  # Last 5 unique topics
        
        duration = datetime.now() - self.conversation_start
        minutes = int(duration.total_seconds() / 60)
        
        summary = f"We've had {self.exchange_count} exchanges over {minutes} minutes. "
        
        if unique_topics:
            summary += f"We've talked about {', '.join(unique_topics)}. "
        
        summary += f"Current mood: {self.conversation_state['mood']}."
        
        return summary
    
    def get_conversation_stats(self) -> Dict:
        """Get detailed conversation statistics"""
        return {
            'exchange_count': self.exchange_count,
            'duration_minutes': int((datetime.now() - self.conversation_start).total_seconds() / 60),
            'current_topic': self.current_topic,
            'state': self.conversation_state.copy(),
            'unique_topics': len(set([
                entry['topic'] for entry in self.dialogue_history 
                if isinstance(entry, dict) and entry.get('topic')
            ])),
            'topic_tree_size': len(self.topic_tree),
            'user_name': self.user_name,
            'user_id': self.user_id
        }
    
    def clear_history(self):
        """Clear dialogue history and reset state"""
        self.dialogue_history.clear()
        self.current_topic = None
        self.topic_tree = {}
        self.exchange_count = 0
        self.conversation_start = datetime.now()
        self.conversation_state = {
            'mood': 'neutral',
            'depth': 0,
            'urgency': 0,
            'last_interaction': None
        }
        print("      🔄 Dialogue history cleared")