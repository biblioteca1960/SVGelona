"""
personality/response_styler.py
Applies personality style to responses
IMPROVED VERSION: Added styles for frustrated, cautious, inquisitive
"""

import random
import re
from typing import Dict, List

class ResponseStyler:
    """
    Applies personality style to responses
    """
    
    def __init__(self):
        # Phrases for different tones
        self.tonal_phrases = {
            'analytical': [
                "Analyzing carefully...",
                "From a logical perspective...",
                "Examining the data...",
                "According to my reasoning..."
            ],
            'emotional': [
                "I feel deeply that...",
                "It makes me feel that...",
                "With great emotion I tell you that...",
                "My heart tells me that..."
            ],
            'balanced': [
                "From a balanced view...",
                "Considering both sides...",
                "In fair measure...",
                "Harmoniously..."
            ],
            'creative': [
                "Imagining possibilities...",
                "Creatively speaking...",
                "If we let imagination fly...",
                "In a burst of creativity..."
            ],
            'optimistic': [
                "With optimism...",
                "Seeing a bright future...",
                "Positively...",
                "Hopefully..."
            ],
            'nostalgic': [
                "Remembering times past...",
                "With a touch of nostalgia...",
                "As it used to be...",
                "In my memory..."
            ],
            'philosophical': [
                "Reflecting deeply...",
                "In essence...",
                "Philosophically...",
                "Contemplating existence..."
            ],
            'holistic': [
                "From the whole...",
                "Unifying perspectives...",
                "Integrating all parts...",
                "In the big picture..."
            ],
            'enthusiastic': [
                "With great enthusiasm!",
                "Excitedly!",
                "What a fascinating question!",
                "I'm passionate about this topic!"
            ],
            'somber': [
                "Reflecting seriously...",
                "With some concern...",
                "Considering the gravity...",
                "Deeply..."
            ],
            # 🔥 NEW: Frustrated tone
            'frustrated': [
                "I'm having trouble finding information on this...",
                "This is proving difficult to figure out...",
                "I seem to be struggling with this topic...",
                "Hmm, I'm not having much luck with this..."
            ],
            # 🔥 NEW: Cautious tone
            'cautious': [
                "I want to be careful with this...",
                "From what I can tell, though I'm not entirely sure...",
                "Based on limited information...",
                "Tentatively, I would say..."
            ],
            # 🔥 NEW: Inquisitive tone
            'inquisitive': [
                "That's an intriguing question!",
                "I'm curious about that myself!",
                "What a fascinating line of inquiry!",
                "That sparks my curiosity!"
            ]
        }
        
        # Text modifiers
        self.modifiers = {
            'emphatic': ['!', '!!', ' absolutely', ' totally', ' completely'],
            'hesitant': [' perhaps', ' maybe', ' possibly', ' ...', ' I suppose'],
            'certain': [' certainly', ' undoubtedly', ' clearly', ' obviously'],
            'questioning': ['?', ' right?', ' don\'t you think?', ' what do you think?']
        }
        
        print("  ✅ ResponseStyler initialized")
        print("     🎭 Styles: analytical, emotional, balanced, creative, optimistic,")
        print("         nostalgic, philosophical, holistic, enthusiastic, somber,")
        print("         frustrated, cautious, inquisitive")
    
    def apply_style(self, text: str, persona: Dict) -> str:
        """
        Applies personality style to text
        
        Args:
            text: Original text
            persona: Personality information
        
        Returns:
            Styled text
        """
        style = persona['style']
        tone = style['tone']
        
        # 1. Add introductory phrase (20% chance)
        if random.random() < 0.3:
            intro = self._get_intro_phrase(tone)
            text = f"{intro} {text}"
        
        # 2. Apply modifiers based on personality
        text = self._apply_modifiers(text, style)
        
        # 3. Add emotional emphasis
        text = self._add_emotional_emphasis(text, persona['emotional_state'])
        
        # 4. Adjust length based on confidence
        if style['confidence'] > 0.8:
            # More direct
            text = re.sub(r'\s+(perhaps|maybe|possibly)\s+', ' ', text)
        elif style['confidence'] < 0.4:
            # More hesitant
            if not any(m in text for m in [' perhaps', ' maybe']):
                text = text.replace('.', '...', 1)
        
        return text.strip()
    
    def _get_intro_phrase(self, tone: str) -> str:
        """Gets introductory phrase for the tone"""
        phrases = self.tonal_phrases.get(tone, self.tonal_phrases['balanced'])
        return random.choice(phrases)
    
    def _apply_modifiers(self, text: str, style: Dict) -> str:
        """Applies modifiers to text"""
        # Creativity = more variation
        if style['creativity'] > 0.7 and random.random() < 0.2:
            # Add creative adjectives
            creative_adj = [' fascinating', ' extraordinary', ' unique', ' wonderful']
            text = text.replace('.', random.choice(creative_adj) + '.')
        
        # Curiosity = more questions
        if style['curiosity'] > 0.7 and not text.endswith('?'):
            if random.random() < 0.15:
                text += random.choice(self.modifiers['questioning'])
        
        # Empathy = more personal tone
        if style['empathy'] > 0.7:
            if random.random() < 0.1:
                text = "I understand how you feel. " + text
        
        # 🔥 NEW: Patience affects length
        if style.get('patience', 0.8) < 0.4:
            # When impatient, responses are shorter
            sentences = text.split('.')
            if len(sentences) > 2:
                text = '. '.join(sentences[:2]) + '.'
        
        return text
    
    def _add_emotional_emphasis(self, text: str, emotional_state: Dict) -> str:
        """Adds emphasis based on emotional state"""
        
        # High valence = more enthusiasm
        if emotional_state['valence'] > 0.7:
            if random.random() < 0.2:
                text = text.replace('.', '!')
        
        # Low valence = more seriousness
        elif emotional_state['valence'] < 0.3:
            if random.random() < 0.2:
                text = text.replace('!', '.')
        
        # High arousal = more energy
        if emotional_state['arousal'] > 0.7:
            if random.random() < 0.15:
                text += random.choice(['!', '!!'])
        
        # 🔥 NEW: High frustration = more hesitation
        if emotional_state.get('frustration', 0) > 0.5:
            if random.random() < 0.2:
                text = text.replace('.', '...')
        
        return text
    
    def get_greeting(self, persona: Dict) -> str:
        """Returns personalized greeting"""
        style = persona['style']
        
        greetings = {
            'analytical': "Hello, let's analyze what you want to know.",
            'emotional': "Hello! How are you? I'm excited to talk with you!",
            'balanced': "Hello, nice to talk with you.",
            'creative': "Hello! What shall we imagine today?",
            'optimistic': "Hello! What a beautiful day for conversation!",
            'nostalgic': "Hello... I remember the first time we talked.",
            'philosophical': "Hello, let's reflect together.",
            'holistic': "Hello, let's connect with the universe.",
            'enthusiastic': "HELLO! How are you? I'm so excited to talk!",
            'somber': "Hello, I hope you're doing well.",
            'frustrated': "Hello... I've been having some trouble lately, but I'm glad you're here.",
            'cautious': "Hello, let's see what we can figure out together.",
            'inquisitive': "Hello! I'm curious to hear what you'll ask today!"
        }
        
        return greetings.get(style['tone'], greetings['balanced'])