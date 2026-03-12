"""
topic/topic_manager.py
Gestor de temes amb arbre de relacions i persistència
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict, Counter

class TopicManager:
    """
    Gestor de temes avançat amb:
    - Arbre jeràrquic de temes
    - Relacions entre temes
    - Confiança en la detecció
    - Persistència per usuari
    """
    
    def __init__(self, user_id: str = "default", storage_path="memories/topics"):
        self.user_id = user_id
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Estat actual
        self.current_topic = None
        self.current_confidence = 0.0
        self.topic_history = []
        
        # Arbre de temes
        self.topic_tree = {}  # {topic: {subtopics: [], related: [], parent: None}}
        
        # Estadístiques
        self.topic_frequency = Counter()
        self.topic_transitions = defaultdict(Counter)  # {from_topic: {to_topic: count}}
        
        # Índex per paraules clau
        self.keyword_index = defaultdict(set)  # {keyword: {topics}}
        
        # Carregar dades persistents
        self._load()
        
        print(f"  ✅ TopicManager initialized for user '{user_id}'")
        print(f"     📚 Topics tracked: {len(self.topic_tree)}")
        print(f"     🔗 Transitions: {sum(len(t) for t in self.topic_transitions.values())}")
    
    def _get_storage_file(self) -> str:
        """Retorna el camí del fitxer de dades"""
        return os.path.join(self.storage_path, f"{self.user_id}_topics.json")
    
    def _load(self):
        """Carrega dades persistents"""
        storage_file = self._get_storage_file()
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.topic_tree = data.get('topic_tree', {})
                self.topic_frequency = Counter(data.get('topic_frequency', {}))
                
                # Convertir transitions de vuelta a defaultdict(Counter)
                transitions_data = data.get('topic_transitions', {})
                self.topic_transitions = defaultdict(Counter)
                for from_topic, to_counts in transitions_data.items():
                    self.topic_transitions[from_topic] = Counter(to_counts)
                
                # Reconstruir índex
                self._rebuild_index()
                
                print(f"     📖 Loaded {len(self.topic_tree)} topics from storage")
            except Exception as e:
                print(f"     ⚠️ Could not load topics: {e}")
    
    def _save(self):
        """Guarda dades persistents"""
        storage_file = self._get_storage_file()
        
        # Preparar dades per serialitzar
        data = {
            'topic_tree': self.topic_tree,
            'topic_frequency': dict(self.topic_frequency),
            'topic_transitions': {k: dict(v) for k, v in self.topic_transitions.items()},
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"     ⚠️ Could not save topics: {e}")
    
    def _rebuild_index(self):
        """Reconstrueix l'índex de paraules clau"""
        self.keyword_index.clear()
        
        for topic in self.topic_tree:
            # Paraules del tema
            words = re.findall(r'\b[a-záéíóúñ]{4,}\b', topic.lower())
            for word in words:
                self.keyword_index[word].add(topic)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extreu paraules clau potencials del text"""
        # Netejar text
        text = text.lower()
        text = re.sub(r'[^\w\sáéíóúñ]', ' ', text)
        
        # Extreure paraules significatives (4+ lletres)
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text)
        
        # Filtrar paraules buides
        stopwords = {'aquest', 'aquesta', 'això', 'sobre', 'entre', 'durant',
                    'abans', 'després', 'sempre', 'mai', 'quan', 'com', 'però',
                    'this', 'that', 'these', 'those', 'with', 'from', 'have'}
        
        keywords = [w for w in words if w not in stopwords]
        
        return keywords
    
    def extract_topics(self, text: str, min_confidence: float = 0.5) -> List[Dict]:
        """
        Extreu temes potencials del text
        
        Returns:
            Llista de temes amb confiança i tipus
        """
        text_lower = text.lower()
        keywords = self._extract_keywords(text)
        
        topics = []
        
        # 1. Detectar per paraules clau conegudes
        for keyword in keywords:
            if keyword in self.keyword_index:
                for topic in self.keyword_index[keyword]:
                    confidence = 0.7 + (self.topic_frequency[topic] * 0.01)
                    confidence = min(0.95, confidence)
                    
                    topics.append({
                        'text': topic,
                        'type': 'KNOWN',
                        'confidence': confidence,
                        'source': 'keyword_index'
                    })
        
        # 2. Detectar per patrons gramaticals (noms propis)
        # Paraules amb majúscula (en text original)
        words = text.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 3:
                # Comprovar que no és primera paraula de frase
                if word not in topics and word.lower() not in [t['text'].lower() for t in topics]:
                    topics.append({
                        'text': word.lower(),
                        'type': 'PROPER_NOUN',
                        'confidence': 0.8,
                        'source': 'capitalization'
                    })
        
        # 3. Detectar per noms compostos (2-3 paraules)
        for i in range(len(words) - 1):
            # Bigrames
            bigram = f"{words[i]} {words[i+1]}".lower()
            if len(bigram) > 5 and bigram not in [t['text'] for t in topics]:
                topics.append({
                    'text': bigram,
                    'type': 'BIGRAM',
                    'confidence': 0.6,
                    'source': 'bigram'
                })
        
        # 4. Detectar per freqüència
        word_freq = Counter(keywords)
        for word, freq in word_freq.items():
            if freq > 1 and word not in [t['text'] for t in topics]:
                confidence = 0.5 + (freq * 0.1)
                topics.append({
                    'text': word,
                    'type': 'FREQUENT',
                    'confidence': min(0.9, confidence),
                    'source': 'frequency'
                })
        
        # Ordenar per confiança i treure duplicats
        seen = set()
        unique_topics = []
        for topic in sorted(topics, key=lambda x: x['confidence'], reverse=True):
            if topic['text'] not in seen:
                seen.add(topic['text'])
                unique_topics.append(topic)
        
        # Filtrar per confiança mínima
        unique_topics = [t for t in unique_topics if t['confidence'] >= min_confidence]
        
        return unique_topics[:5]  # Limitar a 5
    
    def update_topic(self, new_topic: Dict, confidence_boost: float = 0.0):
        """
        Actualitza el tema actual
        
        Args:
            new_topic: Dict amb 'text', 'type', 'confidence'
            confidence_boost: Boost addicional de confiança
        """
        if not new_topic or not new_topic.get('text'):
            return
        
        topic_text = new_topic['text']
        confidence = new_topic['confidence'] + confidence_boost
        confidence = min(1.0, confidence)
        
        # Registrar transició
        if self.current_topic:
            self.topic_transitions[self.current_topic][topic_text] += 1
        
        # Afegir a l'historial
        self.topic_history.append({
            'topic': self.current_topic,
            'timestamp': datetime.now().isoformat(),
            'confidence': self.current_confidence
        })
        
        # Mantenir historial limitat
        if len(self.topic_history) > 50:
            self.topic_history = self.topic_history[-50:]
        
        # Actualitzar tema actual
        old_topic = self.current_topic
        self.current_topic = topic_text
        self.current_confidence = confidence
        
        # Actualitzar freqüència
        self.topic_frequency[topic_text] += 1
        
        # Crear entrada a l'arbre si no existeix
        if topic_text not in self.topic_tree:
            self.topic_tree[topic_text] = {
                'subtopics': [],
                'related': [],
                'parent': old_topic,
                'first_seen': datetime.now().isoformat(),
                'times_mentioned': 1
            }
        else:
            self.topic_tree[topic_text]['times_mentioned'] = \
                self.topic_tree[topic_text].get('times_mentioned', 0) + 1
        
        # Actualitzar relacions
        if old_topic and old_topic != topic_text:
            # Afegir com a subtema
            if topic_text not in self.topic_tree[old_topic]['subtopics']:
                self.topic_tree[old_topic]['subtopics'].append(topic_text)
            
            # Afegir com a relacionat
            if old_topic not in self.topic_tree[topic_text]['related']:
                self.topic_tree[topic_text]['related'].append(old_topic)
        
        # Actualitzar índex de paraules clau
        for word in self._extract_keywords(topic_text):
            self.keyword_index[word].add(topic_text)
        
        # Guardar cada 5 actualitzacions
        if len(self.topic_history) % 5 == 0:
            self._save()
    
    def get_topic_context(self) -> Dict:
        """
        Retorna context complet del tema actual
        """
        if not self.current_topic:
            return {
                'current': None,
                'confidence': 0.0,
                'previous': [],
                'related': [],
                'subtopics': [],
                'history_length': len(self.topic_history)
            }
        
        # Obtenir informació de l'arbre
        topic_info = self.topic_tree.get(self.current_topic, {})
        
        # Obtenir últims 3 temes (excloent l'actual)
        previous = []
        seen = set()
        for entry in reversed(self.topic_history):
            if entry['topic'] and entry['topic'] != self.current_topic:
                if entry['topic'] not in seen:
                    previous.append({
                        'topic': entry['topic'],
                        'confidence': entry['confidence'],
                        'timestamp': entry['timestamp']
                    })
                    seen.add(entry['topic'])
                if len(previous) >= 3:
                    break
        
        # Obtenir temes relacionats (més freqüents en transicions)
        transitions = self.topic_transitions.get(self.current_topic, {})
        related = [t for t, _ in sorted(transitions.items(), 
                                        key=lambda x: x[1], reverse=True)][:5]
        
        # Possibles continuacions (basat en transicions)
        continuations = []
        for topic, count in transitions.items():
            if count > 1:
                continuations.append({
                    'topic': topic,
                    'probability': count / sum(transitions.values())
                })
        
        return {
            'current': {
                'text': self.current_topic,
                'confidence': self.current_confidence,
                'times_mentioned': topic_info.get('times_mentioned', 1)
            },
            'previous': previous,
            'related': related,
            'subtopics': topic_info.get('subtopics', [])[-5:],
            'continuations': sorted(continuations, 
                                   key=lambda x: x['probability'], 
                                   reverse=True)[:3],
            'history_length': len(self.topic_history)
        }
    
    def get_suggested_followup(self) -> Optional[str]:
        """
        Suggerix una possible pregunta de seguiment basada en el tema actual
        """
        if not self.current_topic:
            return None
        
        context = self.get_topic_context()
        
        templates = [
            f"Vols que t'expliqui més sobre {self.current_topic}?",
            f"T'interessa algun aspecte en particular de {self.current_topic}?",
            f"Coneixes altres temes relacionats amb {self.current_topic}?"
        ]
        
        # Si hi ha continuacions probables
        if context.get('continuations'):
            cont = context['continuations'][0]['topic']
            templates.append(f"Vols parlar de {cont}, que està relacionat?")
        
        # Si hi ha subtemes
        if context.get('subtopics'):
            sub = context['subtopics'][0]
            templates.append(f"Podria explicar-te sobre {sub}, que n'és un subtema.")
        
        return templates[len(context['history_length']) % len(templates)]
    
    def get_topic_summary(self) -> str:
        """
        Retorna un resum llegible de l'estat de temes
        """
        context = self.get_topic_context()
        
        if not context['current']:
            return "Encara no hem parlat de cap tema específic."
        
        lines = []
        lines.append(f"📌 **Tema actual**: {context['current']['text']} "
                    f"(confiança: {context['current']['confidence']:.1%})")
        
        if context['previous']:
            prev_topics = [p['topic'] for p in context['previous']]
            lines.append(f"📜 **Temes recents**: {', '.join(prev_topics)}")
        
        if context['related']:
            lines.append(f"🔗 **Relacionats**: {', '.join(context['related'][:3])}")
        
        if context['subtopics']:
            lines.append(f"📚 **Subtemes**: {', '.join(context['subtopics'][:3])}")
        
        return '\n'.join(lines)
    
    def reset_session(self):
        """Reinicia la sessió (manté dades persistents però neteja estat actual)"""
        self.current_topic = None
        self.current_confidence = 0.0
        self.topic_history = []
        print(f"     🔄 Session reset for user '{self.user_id}'")