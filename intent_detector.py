"""
intent/intent_detector.py
Advanced intent detector with multi-language support
IMPROVED VERSION: Detection of compound names ("Albert Einstein")
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

class IntentDetector:
    """
    Advanced intent detector with:
    - Multiple languages (Catalan, Spanish, English)
    - Subtlety detection
    - Confidence scoring
    - Compound intentions
    - 🔥 Compound name detection (Albert Einstein)
    """
    
    def __init__(self):
        # Patterns by language
        self.patterns = {
            'ca': {
                'greeting': [
                    r'^(hola|bon dia|bona tarda|bona nit|ei)',
                    r'(com estàs|com va|què tal)',
                ],
                'farewell': [
                    r'(adeu|fins ara|fins després|ens veiem)',
                    r'(a reveure|fins aviat)',
                ],
                'factual': [
                    r'(què és|qui és|què significa|com es diu)',
                    r'(explica\'m|defineix|descriu)',
                    r'(història de|origen de|biografia de)',
                ],
                'opinion': [
                    r'(què penses|quina és la teva opinió|creus que)',
                    r'(estàs d\'acord|què et sembla)',
                ],
                'comparison': [
                    r'(diferència entre|comparació|versus|vs)',
                    r'(millor que|pitjor que|igual que)',
                ],
                'temporal': [
                    r'(quan|quina data|quin any|en quin moment)',
                    r'(abans de|després de|durant)',
                ],
                'creative': [
                    r'(imagina|inventa|crea|genera)',
                    r'(fes-me un relat|explica\'m una història)',
                ],
                'help': [
                    r'(ajuda|què saps fer|com funciona|help)',
                    r'(quines són les teves capacitats)',
                ],
                'personal': [
                    r'(qui ets|què ets|com et dius|d\'on ets)',
                    r'(explica\'m sobre tu|presenta\'t)',
                ],
                'location': [
                    r'(on és|on està|localització de)',
                    r'(com arribar a|direcció de)',
                ],
                'math': [
                    r'(calcula|quina és la fórmula|demostra)',
                    r'(teorema|equació|funció|derivada|integral)',
                ]
            },
            'es': {
                'greeting': [
                    r'^(hola|buenos días|buenas tardes|buenas noches|hey)',
                    r'(cómo estás|cómo va|qué tal)',
                ],
                'farewell': [
                    r'(adiós|hasta luego|hasta pronto|nos vemos)',
                ],
                'factual': [
                    r'(qué es|quién es|qué significa|cómo se llama)',
                    r'(explícame|define|describe)',
                    r'(historia de|origen de|biografía de)',
                ],
                'opinion': [
                    r'(qué piensas|cuál es tu opinión|crees que)',
                    r'(estás de acuerdo|qué te parece)',
                ],
                'comparison': [
                    r'(diferencia entre|comparación|versus|vs)',
                    r'(mejor que|peor que|igual que)',
                ],
                'temporal': [
                    r'(cuándo|qué fecha|qué año|en qué momento)',
                    r'(antes de|después de|durante)',
                ],
                'creative': [
                    r'(imagina|inventa|crea|genera)',
                    r'(hazme un relato|cuéntame una historia)',
                ],
                'help': [
                    r'(ayuda|qué sabes hacer|cómo funcionas|help)',
                    r'(cuáles son tus capacidades)',
                ],
                'personal': [
                    r'(quién eres|qué eres|cómo te llamas|de dónde eres)',
                    r'(explícame sobre ti|preséntate)',
                ],
                'location': [
                    r'(dónde está|localización de)',
                    r'(cómo llegar a|dirección de)',
                ],
                'math': [
                    r'(calcula|cuál es la fórmula|demuestra)',
                    r'(teorema|ecuación|función|derivada|integral)',
                ]
            },
            'en': {
                'greeting': [
                    r'^(hello|hi|hey|good morning|good afternoon)',
                    r'(how are you|how\'s it going|what\'s up)',
                ],
                'farewell': [
                    r'(goodbye|bye|see you|farewell)',
                ],
                'factual': [
                    r'(what is|who is|what does it mean|how do you call)',
                    r'(explain|define|describe)',
                    r'(history of|origin of|biography of)',
                ],
                'opinion': [
                    r'(what do you think|what\'s your opinion|do you think)',
                    r'(do you agree|how do you feel about)',
                ],
                'comparison': [
                    r'(difference between|comparison|versus|vs)',
                    r'(better than|worse than|similar to)',
                ],
                'temporal': [
                    r'(when|what date|what year|at what time)',
                    r'(before|after|during)',
                ],
                'creative': [
                    r'(imagine|invent|create|generate)',
                    r'(tell me a story|write a tale)',
                ],
                'help': [
                    r'(help|what can you do|how do you work)',
                    r'(what are your capabilities)',
                ],
                'personal': [
                    r'(who are you|what are you|what\'s your name)',
                    r'(tell me about yourself|introduce yourself)',
                ],
                'location': [
                    r'(where is|location of)',
                    r'(how to get to|address of)',
                ],
                'math': [
                    r'(calculate|what\'s the formula|prove)',
                    r'(theorem|equation|function|derivative|integral)',
                ]
            }
        }
        
        # 🔥 List of words indicating compound proper names
        self.name_indicators = [
            'albert', 'einstein', 'isaac', 'newton', 'leonhard', 'euler',
            'carl', 'friedrich', 'gauss', 'nikola', 'tesla', 'marie', 'curie',
            'thomas', 'edison', 'alexander', 'graham', 'bell', 'galileo',
            'galilei', 'aristotle', 'plato', 'socrates', 'pythagoras',
            'leonardo', 'da vinci', 'michelangelo', 'vincent', 'van gogh',
            'pablo', 'picasso', 'salvador', 'dali', 'frida', 'kahlo'
        ]
        
        # Intent to response style mapping
        self.response_styles = {
            'greeting': {'style': 'friendly', 'needs_wikipedia': False, 'energy': 'high'},
            'farewell': {'style': 'warm', 'needs_wikipedia': False, 'energy': 'medium'},
            'factual': {'style': 'informative', 'needs_wikipedia': True, 'energy': 'medium'},
            'opinion': {'style': 'reflective', 'needs_wikipedia': False, 'energy': 'low'},
            'comparison': {'style': 'analytical', 'needs_wikipedia': True, 'energy': 'medium'},
            'temporal': {'style': 'narrative', 'needs_wikipedia': True, 'energy': 'medium'},
            'creative': {'style': 'creative', 'needs_wikipedia': False, 'energy': 'high'},
            'help': {'style': 'helpful', 'needs_wikipedia': False, 'energy': 'medium'},
            'personal': {'style': 'personal', 'needs_wikipedia': False, 'energy': 'medium'},
            'location': {'style': 'informative', 'needs_wikipedia': True, 'energy': 'medium'},
            'math': {'style': 'precise', 'needs_wikipedia': False, 'energy': 'low'},
            'conversational': {'style': 'balanced', 'needs_wikipedia': False, 'energy': 'medium'}
        }
        
        # Language detection by keywords
        self.lang_keywords = {
            'ca': ['hola', 'bon', 'com', 'què', 'ets', 'estàs', 'si us plau', 'gràcies'],
            'es': ['hola', 'buenos', 'cómo', 'qué', 'eres', 'estás', 'por favor', 'gracias'],
            'en': ['hello', 'how', 'what', 'are', 'you', 'please', 'thanks', 'thank']
        }
        
        print("  ✅ IntentDetector initialized (ENHANCED with compound name detection)")
        print("     🌐 Languages: Català, Español, English")
        print("     🎯 Intents: 12 categories")
    
    def detect_language(self, text: str) -> str:
        """Detects the language of the text"""
        text_lower = text.lower()
        scores = {lang: 0 for lang in self.lang_keywords}
        
        for lang, keywords in self.lang_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[lang] += 1
        
        # Normalize by length
        words = text_lower.split()
        for lang in scores:
            scores[lang] = scores[lang] / max(1, len(words))
        
        if max(scores.values()) > 0.1:
            return max(scores, key=scores.get)
        return 'en'  # Default
    
    # 🔥 NEW: Detect compound names
    def _detect_compound_names(self, query: str) -> List[str]:
        """Detects compound names like 'Albert Einstein'"""
        words = query.split()
        compounds = []
        
        # Look for word pairs where the first is a common name
        for i in range(len(words) - 1):
            # Check if current word and next are candidates
            word1_lower = words[i].lower()
            word2_lower = words[i+1].lower()
            
            # If first word is in name indicators list
            if word1_lower in self.name_indicators:
                compounds.append(f"{words[i]} {words[i+1]}")
            # If both start with capital letters and length > 2
            elif (words[i][0].isupper() and words[i+1][0].isupper() and 
                  len(words[i]) > 2 and len(words[i+1]) > 2):
                compounds.append(f"{words[i]} {words[i+1]}")
        
        return compounds
    
    def detect(self, query: str) -> Dict:
        """
        Detects the main intent and secondary intents
        
        Returns:
            Dict with primary intent, secondary intents, scores, and metadata
        """
        # Detect language
        lang = self.detect_language(query)
        query_lower = query.lower()
        
        # 🔥 Check for compound names first
        compound_names = self._detect_compound_names(query)
        if compound_names:
            print(f"         📌 Detected compound name: {compound_names[0]}")
            # Return factual intent with high confidence
            return {
                'primary': 'factual',
                'secondary': [],
                'scores': {'factual': 0.95},
                'matches': {'factual': compound_names},
                'language': lang,
                'confidence': 0.95,
                'subtleties': [],
                'needs_wikipedia': True,
                'response_style': 'informative',
                'energy': 'medium',
                'compound_names': compound_names,
                'raw_query': query
            }
        
        # Scoring for each intent
        scores = defaultdict(float)
        matches = defaultdict(list)
        
        # Search patterns in detected language
        patterns = self.patterns.get(lang, self.patterns['en'])
        
        for intent, intent_patterns in patterns.items():
            for pattern in intent_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    # Score based on position (words at beginning are more important)
                    pos = match.start()
                    weight = 1.0 - (pos / len(query_lower)) * 0.3
                    scores[intent] += weight
                    matches[intent].append(match.group())
        
        # Normalize scores
        total_matches = sum(scores.values())
        if total_matches > 0:
            for intent in scores:
                scores[intent] = scores[intent] / total_matches
        
        # Detect additional subtleties
        subtleties = self._detect_subtleties(query_lower)
        
        # Determine primary intent
        if scores:
            primary = max(scores, key=scores.get)
            # Secondary intents (score > 0.2 but not primary)
            secondary = [i for i, s in scores.items() 
                        if i != primary and s > 0.2]
        else:
            # If no intent detected, assign default
            if any(c in query_lower for c in ['?', '¿']):
                primary = 'factual'
            elif len(query_lower.split()) < 3:
                primary = 'greeting'
            else:
                primary = 'conversational'
            secondary = []
            scores[primary] = 1.0
        
        # Enrich with subtleties
        if subtleties:
            for subtlety in subtleties:
                if subtlety not in scores or scores[subtlety] < 0.3:
                    secondary.append(subtlety)
        
        # Remove duplicates
        secondary = list(set(secondary))
        
        # Get response styles
        primary_style = self.response_styles.get(primary, self.response_styles['conversational'])
        
        # Detection confidence
        confidence = max(scores.values()) if scores else 0.5
        
        return {
            'primary': primary,
            'secondary': secondary,
            'scores': dict(scores),
            'matches': dict(matches),
            'language': lang,
            'confidence': confidence,
            'subtleties': subtleties,
            'needs_wikipedia': primary_style['needs_wikipedia'] or 
                              any(self.response_styles.get(i, {}).get('needs_wikipedia', False) 
                                  for i in secondary),
            'response_style': primary_style['style'],
            'energy': primary_style['energy'],
            'compound_names': compound_names,
            'raw_query': query
        }
    
    def _detect_subtleties(self, query: str) -> List[str]:
        """Detects additional subtleties"""
        subtleties = []
        
        # Rhetorical questions
        if re.search(r'(no creus|no és veritat|oi que sí)', query):
            subtleties.append('opinion')
        
        # Emotional questions
        if re.search(r'!(està bé|genial|fantàstic|meravellós)', query):
            subtleties.append('emotional')
        
        # Doubt
        if re.search(r'(potser|tal vegada|igual|maybe|perhaps)', query):
            subtleties.append('uncertainty')
        
        # Emphasis
        if '!' in query:
            subtleties.append('emphatic')
        
        return subtleties
    
    def get_response_guidance(self, intent_info: Dict) -> Dict:
        """Returns guidance for response generation based on intent"""
        primary = intent_info['primary']
        style = self.response_styles.get(primary, self.response_styles['conversational'])
        
        guidance = {
            'should_be_concise': primary in ['factual', 'location'],
            'should_be_detailed': primary in ['comparison', 'temporal', 'math'],
            'should_be_creative': primary == 'creative',
            'should_be_personal': primary == 'personal',
            'should_ask_followup': primary in ['greeting', 'opinion', 'help'],
            'energy_level': style['energy'],
            'formality': 'medium' if primary == 'conversational' else 
                        'high' if primary in ['factual', 'math'] else 'low',
            'suggested_length': 'short' if primary in ['greeting', 'farewell'] else
                               'medium' if primary in ['factual', 'location'] else
                               'long'
        }
        
        return guidance
    
    def get_example_queries(self, intent: str) -> List[str]:
        """Returns example queries for an intent"""
        examples = {
            'greeting': ['Hello', 'Good morning', 'Hi', 'How are you?'],
            'farewell': ['Goodbye', 'See you later', 'Bye'],
            'factual': ['What is a black hole?', 'Who is Einstein?', 'Define consciousness'],
            'opinion': ['What do you think about AI?', 'Do you think AI is dangerous?'],
            'comparison': ['Difference between atom and molecule', 'Compare cats and dogs'],
            'temporal': ['When was Mozart born?', 'History of mathematics'],
            'creative': ['Imagine a world without gravity', 'Create a story about a conscious AI'],
            'help': ['What can you do?', 'How can you help me?'],
            'personal': ['Who are you?', 'Tell me about yourself'],
            'location': ['Where is Barcelona?', 'Location of the Eiffel Tower'],
            'math': ['Calculate 2+2', 'What is the Pythagorean theorem?']
        }
        return examples.get(intent, [])