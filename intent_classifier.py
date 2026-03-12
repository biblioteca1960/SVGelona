"""
intent/intent_classifier.py
Advanced intent classifier with learning
IMPROVED VERSION: Better theorem, location, and historical figure detection
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import numpy as np

class IntentClassifier:
    """
    Intent classifier with:
    - Pattern learning
    - Context-based classification
    - Subtlety detection
    - Success/failure history
    - 🔥 Improved theorem, location, and historical figure detection
    """
    
    def __init__(self, storage_path="memories/intent"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Intent categories
        self.intent_categories = {
            'salutation': {
                'patterns': ['hola', 'bon dia', 'hello', 'hi', 'hey', 'salut'],
                'subcategories': ['greeting', 'introduction', 'farewell'],
                'weight': 1.0
            },
            'information_request': {
                'patterns': ['what is', 'who is', 'define', 'explain', 'describe',
                           'què és', 'qué es', 'defineix', 'explica', 'descriu'],
                'subcategories': ['definition', 'explanation', 'biography', 'history'],
                'weight': 1.2
            },
            'opinion_request': {
                'patterns': ['what do you think', 'opinion', 'do you believe',
                           'què penses', 'opinió', 'creus que'],
                'subcategories': ['personal_opinion', 'analysis', 'reflection'],
                'weight': 1.1
            },
            'comparison': {
                'patterns': ['difference between', 'versus', 'vs', 'comparison',
                           'diferència', 'comparació', 'millor que'],
                'subcategories': ['direct_comparison', 'contrast', 'similarity'],
                'weight': 1.3
            },
            'temporal': {
                'patterns': ['when', 'history', 'origin', 'future', 'past',
                           'quan', 'història', 'origen', 'futur', 'passat'],
                'subcategories': ['past_event', 'future_prediction', 'historical_fact'],
                'weight': 1.0
            },
            'creative': {
                'patterns': ['imagine', 'create', 'invent', 'generate',
                           'imagina', 'crea', 'inventa', 'genera'],
                'subcategories': ['story', 'poem', 'idea', 'concept'],
                'weight': 1.0
            },
            'procedural': {
                'patterns': ['how to', 'procedure', 'steps', 'instructions',
                           'com es', 'procediment', 'passos', 'instruccions'],
                'subcategories': ['instructions', 'tutorial', 'guide'],
                'weight': 1.1
            },
            'analytical': {
                'patterns': ['analyze', 'examine', 'study', 'investigate',
                           'analitza', 'examina', 'estudia', 'investiga'],
                'subcategories': ['deep_analysis', 'critique', 'evaluation'],
                'weight': 1.2
            },
            'emotional': {
                'patterns': ['how do you feel', 'emotion', 'feeling', 'sad', 'happy',
                           'com et sents', 'emociona', 'sentiment', 'trist'],
                'subcategories': ['empathy', 'emotional_response', 'mood'],
                'weight': 0.9
            },
            'philosophical': {
                'patterns': ['reflect', 'philosophy', 'meaning', 'existence',
                           'reflexiona', 'filosofia', 'sentit', 'existència'],
                'subcategories': ['existential', 'metaphysical', 'ethical'],
                'weight': 1.0
            },
            'theorem': {
                'patterns': ['theorem', 'prove', 'demonstrate', 'proof',
                           'teorema', 'demostra', 'demostración'],
                'subcategories': ['mathematical', 'geometric', 'scientific'],
                'weight': 1.4
            },
            'location': {
                'patterns': ['where is', 'location of', 'find', 'dónde está',
                           'on és', 'ubicación de', 'localització'],
                'subcategories': ['city', 'country', 'landmark', 'address'],
                'weight': 1.3
            }
        }
        
        # 🔥 Known theorems
        self.known_theorems = [
            'pythagoras', 'pythagorean', 'pitágoras', 'euclid', 'euclidean',
            'thales', 'fermat', 'gauss', 'euler', 'riemann', 'hilbert',
            'noether', 'galois', 'lagrange', 'laplace', 'fourier', 'taylor',
            'newton', 'leibniz', 'binomial', 'bayes', 'cauchy', 'schwarz',
            'banach', 'tarski', 'gödel', 'church', 'turing', 'pascal'
        ]
        
        # 🔥 Known locations
        self.known_locations = [
            'barcelona', 'madrid', 'london', 'paris', 'berlin', 'rome', 'milan',
            'new york', 'los angeles', 'chicago', 'tokyo', 'kyoto', 'osaka',
            'beijing', 'shanghai', 'moscow', 'st petersburg', 'cairo', 'johannesburg',
            'sydney', 'melbourne', 'buenos aires', 'são paulo', 'rio de janeiro',
            'mexico city', 'toronto', 'vancouver', 'seoul', 'singapore', 'hong kong',
            'dubai', 'istanbul', 'athens', 'lisbon', 'amsterdam', 'brussels',
            'vienna', 'prague', 'budapest', 'warsaw', 'stockholm', 'oslo', 'helsinki'
        ]
        
        # 🔥 Historical figures
        self.historical_figures = [
            'napoleón', 'napoleon', 'bonaparte', 'nerón', 'nero', 'copérnico', 'copernicus',
            'césar', 'caesar', 'cleopatra', 'alejandro magno', 'alexander the great',
            'aristóteles', 'aristotle', 'platón', 'plato', 'sócrates', 'socrates',
            'pitágoras', 'pythagoras', 'euler', 'newton', 'galileo', 'kepler',
            'shakespeare', 'cervantes', 'da vinci', 'michelangelo', 'van gogh',
            'beethoven', 'mozart', 'bach', 'vivaldi', 'chopin', 'liszt',
            'colón', 'columbus', 'magallanes', 'magellan', 'elcano',
            'cortés', 'pizarro', 'bolívar', 'san martín', 'guerrero'
        ]
        
        # Learning statistics
        self.learning_stats = {
            'total_classifications': 0,
            'correct_classifications': 0,
            'category_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'pattern_weights': defaultdict(lambda: 1.0)
        }
        
        self.recent_classifications = []
        
        self._load()
        
        print(f"  ✅ IntentClassifier initialized")
        print(f"     📊 Categories: {len(self.intent_categories)}")
        print(f"     🔍 Theorem detection: ENABLED")
        print(f"     🌍 Location detection: ENABLED")
        print(f"     👤 Historical figure detection: ENABLED")
    
    def _get_storage_file(self) -> str:
        return os.path.join(self.storage_path, "intent_classifier.json")
    
    def _load(self):
        """Loads learning data"""
        storage_file = self._get_storage_file()
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                category_accuracy = data.get('category_accuracy', {})
                self.learning_stats['category_accuracy'] = defaultdict(
                    lambda: {'correct': 0, 'total': 0},
                    {k: v for k, v in category_accuracy.items()}
                )
                
                self.learning_stats['pattern_weights'] = defaultdict(
                    float, data.get('pattern_weights', {})
                )
                self.learning_stats['total_classifications'] = data.get('total_classifications', 0)
                self.learning_stats['correct_classifications'] = data.get('correct_classifications', 0)
                
                print(f"     📖 Loaded learning data")
            except Exception as e:
                print(f"     ⚠️ Could not load learning data: {e}")
    
    def _save(self):
        """Saves learning data"""
        storage_file = self._get_storage_file()
        
        data = {
            'category_accuracy': dict(self.learning_stats['category_accuracy']),
            'pattern_weights': dict(self.learning_stats['pattern_weights']),
            'total_classifications': self.learning_stats['total_classifications'],
            'correct_classifications': self.learning_stats['correct_classifications']
        }
        
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"     ⚠️ Could not save learning data: {e}")
    
    def _extract_features(self, query: str) -> Dict:
        """Extracts relevant features from the query"""
        query_lower = query.lower()
        words = query_lower.split()
        
        features = {
            'length': len(words),
            'has_question_mark': '?' in query or '¿' in query,
            'has_exclamation': '!' in query,
            'first_word': words[0] if words else '',
            'last_word': words[-1] if words else '',
            'question_words': [w for w in words if w in ['what', 'who', 'where', 'when', 'why', 'how',
                                                         'qué', 'que', 'què', 'qui', 'on', 'cómo']],
            'verbs': self._extract_verbs(query_lower),
            'nouns': self._extract_nouns(query_lower),
            'patterns_matched': []
        }
        
        return features
    
    def _extract_verbs(self, text: str) -> List[str]:
        """Extracts verbs approximately"""
        verb_indicators = [' is ', ' are ', ' was ', ' were ', ' have ', ' has ',
                          ' és ', ' són ', ' està ', ' estan ']
        verbs = []
        for indicator in verb_indicators:
            if indicator in text:
                verbs.append(indicator.strip())
        return verbs
    
    def _extract_nouns(self, text: str) -> List[str]:
        """Extracts nouns approximately"""
        words = text.split()
        return [w for w in words if len(w) > 5]
    
    def _detect_theorem(self, query: str) -> Tuple[bool, float, str]:
        """Detects if query is about a theorem"""
        query_lower = query.lower()
        
        theorem_indicators = ['theorem', 'teorema', 'proof', 'demostra', 'prove']
        has_indicator = any(ind in query_lower for ind in theorem_indicators)
        
        if not has_indicator:
            return False, 0.0, None
        
        for theorem in self.known_theorems:
            if theorem in query_lower:
                return True, 0.95, theorem
        
        match = re.search(r'(?:theorem of|teorema de)\s+([a-záéíóúñ\s]+)', query_lower)
        if match:
            theorem_name = match.group(1).strip()
            words = theorem_name.split()
            if words:
                return True, 0.9, words[0]
        
        return True, 0.7, None
    
    def _detect_location(self, query: str) -> Tuple[bool, float, str]:
        """Detects if query is about a location"""
        query_lower = query.lower()
        
        location_indicators = ['where is', 'dónde está', 'on és', 'location of']
        has_indicator = any(ind in query_lower for ind in location_indicators)
        
        if not has_indicator:
            return False, 0.0, None
        
        for pattern in location_indicators:
            if pattern in query_lower:
                parts = query_lower.split(pattern, 1)
                if len(parts) > 1:
                    location_candidate = parts[1].strip().split()[0]
                    
                    if location_candidate in self.known_locations:
                        return True, 0.95, location_candidate
                    
                    return True, 0.7, location_candidate
        
        return False, 0.0, None
    
    # 🔥 NEW: Detect historical figures
    def _detect_historical_figure(self, query: str) -> Tuple[bool, float, str]:
        """Detects if query is about a historical figure"""
        query_lower = query.lower()
        
        # Check if any historical figure appears in query
        for figure in self.historical_figures:
            if figure in query_lower:
                # Check for context indicators (biography, who was, etc.)
                biography_indicators = ['quién era', 'quién fue', 'who was', 'biografía', 'biography']
                has_indicator = any(ind in query_lower for ind in biography_indicators)
                
                confidence = 0.9 if has_indicator else 0.7
                return True, confidence, figure
        
        return False, 0.0, None
    
    def classify(self, query: str, context: Dict = None) -> Dict:
        """
        Classifies the intent of the query
        """
        # 🔥 First check for historical figures
        is_historical, hist_conf, hist_name = self._detect_historical_figure(query)
        if is_historical:
            print(f"         📌 Historical figure detected: {hist_name} (conf: {hist_conf})")
            return {
                'primary': 'information_request',
                'secondary': ['biography'],
                'subcategory': 'biography',
                'confidence': hist_conf,
                'scores': {'information_request': hist_conf},
                'features': self._extract_features(query),
                'figure_name': hist_name,
                'needs_wikipedia': True,
                'needs_analysis': False,
                'needs_creativity': False
            }
        
        # Then check for theorems
        is_theorem, theorem_conf, theorem_name = self._detect_theorem(query)
        if is_theorem:
            print(f"         📌 Theorem detected: {theorem_name or 'unknown'} (conf: {theorem_conf})")
            return {
                'primary': 'theorem',
                'secondary': ['information_request'],
                'subcategory': 'mathematical',
                'confidence': theorem_conf,
                'scores': {'theorem': theorem_conf, 'information_request': 0.5},
                'features': self._extract_features(query),
                'theorem_name': theorem_name,
                'needs_wikipedia': True,
                'needs_analysis': True,
                'needs_creativity': False
            }
        
        # Then check for locations
        is_location, loc_conf, loc_name = self._detect_location(query)
        if is_location:
            print(f"         📌 Location detected: {loc_name or 'unknown'} (conf: {loc_conf})")
            return {
                'primary': 'location',
                'secondary': ['information_request'],
                'subcategory': 'city',
                'confidence': loc_conf,
                'scores': {'location': loc_conf, 'information_request': 0.5},
                'features': self._extract_features(query),
                'location_name': loc_name,
                'needs_wikipedia': True,
                'needs_analysis': False,
                'needs_creativity': False
            }
        
        query_lower = query.lower()
        features = self._extract_features(query)
        
        scores = defaultdict(float)
        pattern_matches = defaultdict(list)
        
        for category, config in self.intent_categories.items():
            category_score = 0.0
            matches = []
            
            for pattern in config['patterns']:
                if pattern in query_lower:
                    base_weight = config['weight']
                    learned_weight = self.learning_stats['pattern_weights'].get(pattern, 1.0)
                    
                    pos = query_lower.find(pattern)
                    position_weight = 1.0 - (pos / len(query_lower)) * 0.5 if pos >= 0 else 0
                    
                    match_score = base_weight * learned_weight * position_weight
                    category_score += match_score
                    matches.append(pattern)
            
            if category_score > 0:
                scores[category] = category_score
                pattern_matches[category] = matches
        
        total_score = sum(scores.values())
        if total_score > 0:
            for category in scores:
                scores[category] /= total_score
        
        if scores:
            primary = max(scores.items(), key=lambda x: x[1])
            main_category = primary[0]
            confidence = primary[1]
            
            subcategory = self._determine_subcategory(query, main_category)
            secondary = [c for c, s in scores.items() 
                        if c != main_category and s > 0.2]
        else:
            main_category, confidence, subcategory = self._infer_intent(features, context)
            secondary = []
        
        result = {
            'primary': main_category,
            'secondary': secondary,
            'subcategory': subcategory,
            'confidence': confidence,
            'scores': dict(scores),
            'features': features,
            'pattern_matches': dict(pattern_matches),
            'needs_wikipedia': main_category in ['information_request', 'temporal', 'comparison', 'theorem', 'location'],
            'needs_analysis': main_category in ['analytical', 'philosophical', 'theorem'],
            'needs_creativity': main_category in ['creative', 'emotional']
        }
        
        self.recent_classifications.append(result)
        if len(self.recent_classifications) > 20:
            self.recent_classifications = self.recent_classifications[-20:]
        
        self.learning_stats['total_classifications'] += 1
        
        return result
    
    def _determine_subcategory(self, query: str, main_category: str) -> str:
        """Determines the specific subcategory"""
        query_lower = query.lower()
        
        subcategory_map = {
            'salutation': {
                'greeting': ['hola', 'bon dia', 'hello'],
                'introduction': ['present', 'introduce', 'call'],
                'farewell': ['adeu', 'fins', 'bye']
            },
            'information_request': {
                'definition': ['what is', 'define', 'què és'],
                'explanation': ['explain', 'describe', 'explica'],
                'biography': ['biography', 'life of', 'biografia', 'quién era', 'who was'],
                'history': ['history', 'origin', 'història']
            },
            'opinion_request': {
                'personal_opinion': ['you think', 'creus', 'think'],
                'analysis': ['analyze', 'examine', 'analitza'],
                'reflection': ['reflect', 'meditate', 'reflexiona']
            },
            'theorem': {
                'mathematical': ['pythagoras', 'euclid', 'mathematics'],
                'geometric': ['geometry', 'geometric', 'triangle'],
                'scientific': ['physics', 'science', 'scientific']
            },
            'location': {
                'city': ['city', 'ciudad', 'ciutat'],
                'country': ['country', 'país'],
                'landmark': ['monument', 'building', 'edificio']
            }
        }
        
        if main_category in subcategory_map:
            for subcat, patterns in subcategory_map[main_category].items():
                if any(p in query_lower for p in patterns):
                    return subcat
        
        return 'general'
    
    def _infer_intent(self, features: Dict, context: Dict = None) -> Tuple[str, float, str]:
        """Inference when no clear patterns are found"""
        
        if features['has_question_mark']:
            if features['length'] < 5:
                return 'salutation', 0.6, 'greeting'
            else:
                return 'information_request', 0.5, 'general'
        
        if features['length'] < 3:
            return 'salutation', 0.7, 'greeting'
        
        if features['question_words']:
            return 'information_request', 0.6, 'general'
        
        if context and context.get('last_intent'):
            return context['last_intent'], 0.4, 'continuation'
        
        return 'conversational', 0.3, 'general'
    
    def learn_from_feedback(self, query: str, predicted_intent: str, 
                           actual_intent: str, correct: bool):
        """
        Learns from feedback
        """
        self.learning_stats['category_accuracy'][predicted_intent]['total'] += 1
        if correct:
            self.learning_stats['correct_classifications'] += 1
            self.learning_stats['category_accuracy'][predicted_intent]['correct'] += 1
        
        query_lower = query.lower()
        for pattern in self.intent_categories.get(predicted_intent, {}).get('patterns', []):
            if pattern in query_lower:
                if correct:
                    self.learning_stats['pattern_weights'][pattern] *= 1.05
                else:
                    self.learning_stats['pattern_weights'][pattern] *= 0.95
                
                self.learning_stats['pattern_weights'][pattern] = max(0.5, min(2.0, 
                    self.learning_stats['pattern_weights'][pattern]))
        
        if self.learning_stats['total_classifications'] % 10 == 0:
            self._save()
    
    def get_accuracy_report(self) -> Dict:
        """Returns accuracy report"""
        total = self.learning_stats['total_classifications']
        correct = self.learning_stats['correct_classifications']
        
        category_accuracy = {}
        for cat, stats in self.learning_stats['category_accuracy'].items():
            if stats['total'] > 0:
                category_accuracy[cat] = stats['correct'] / stats['total']
        
        return {
            'overall_accuracy': correct / total if total > 0 else 0,
            'total_classifications': total,
            'correct_classifications': correct,
            'category_accuracy': category_accuracy,
            'best_category': max(category_accuracy.items(), key=lambda x: x[1])[0] if category_accuracy else None,
            'worst_category': min(category_accuracy.items(), key=lambda x: x[1])[0] if category_accuracy else None
        }