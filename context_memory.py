"""
memory/context_memory.py
Memòria de context real amb persistència i recuperació semàntica
"""

import json
import os
import numpy as np
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional, Any
import hashlib
import re

class ContextMemory:
    """
    Memòria de context real amb:
    - Memòria a curt termini (últims 50 intercanvis)
    - Memòria a llarg termini (temes importants persistents)
    - Recuperació per similitud semàntica
    - Persistència a disc
    """
    
    def __init__(self, memory_path="memories/context"):
        self.memory_path = memory_path
        os.makedirs(memory_path, exist_ok=True)
        
        # Memòria a curt termini (per sessió)
        self.short_term = deque(maxlen=50)
        
        # Memòria a llarg termini (persistent)
        self.long_term = self._load_long_term()
        
        # Índex per recuperació ràpida
        self.index = self._build_index()
        
        # Estadístiques
        self.stats = {
            'total_exchanges': 0,
            'important_memories': len(self.long_term),
            'last_access': datetime.now().isoformat()
        }
        
        print(f"  ✅ ContextMemory initialized")
        print(f"     📝 Short-term: 50 slots")
        print(f"     💾 Long-term: {len(self.long_term)} memories")
    
    def _load_long_term(self) -> Dict:
        """Carrega memòria a llarg termini de disc"""
        long_term = {}
        memory_file = os.path.join(self.memory_path, "long_term.json")
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convertir claus a tuple si cal
                    for key, value in data.items():
                        # Si la clau és string de tuple, convertir
                        if key.startswith('(') and key.endswith(')'):
                            try:
                                tuple_key = eval(key)
                                long_term[tuple_key] = value
                            except:
                                long_term[key] = value
                        else:
                            long_term[key] = value
                print(f"     📖 Loaded {len(long_term)} long-term memories")
            except Exception as e:
                print(f"     ⚠️ Could not load long-term memory: {e}")
        
        return long_term
    
    def _save_long_term(self):
        """Guarda memòria a llarg termini a disc"""
        memory_file = os.path.join(self.memory_path, "long_term.json")
        
        # Convertir claus tuple a string per JSON
        serializable = {}
        for key, value in self.long_term.items():
            if isinstance(key, tuple):
                serializable[str(key)] = value
            else:
                serializable[key] = value
        
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"     ⚠️ Could not save long-term memory: {e}")
    
    def _build_index(self) -> Dict:
        """Construeix índex per paraules clau"""
        index = {}
        
        # Indexar memòria a llarg termini
        for key, memory in self.long_term.items():
            if isinstance(memory, dict):
                text = memory.get('query', '') + ' ' + memory.get('response', '')
                words = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower()))
                for word in words:
                    if word not in index:
                        index[word] = []
                    index[word].append(key)
        
        return index
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extreu entitats potencials del text"""
        entities = []
        
        # Paraules amb majúscula (possibles noms propis)
        words = text.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                entities.append(word.lower())
        
        # Números (possibles anys, quantitats)
        numbers = re.findall(r'\b\d+\b', text)
        entities.extend(numbers)
        
        # Paraules llargues (possibles conceptes importants)
        long_words = re.findall(r'\b[a-zA-Záéíóúñ]{8,}\b', text.lower())
        entities.extend(long_words[:3])  # Limitar
        
        return list(set(entities))  # Eliminar duplicats
    
    def _compute_importance(self, query: str, response: str, topic: str) -> float:
        """Calcula la importància d'un intercanvi"""
        importance = 0.5  # Base
        
        # Més important si té pregunta
        if '?' in query:
            importance += 0.1
        
        # Més important si és llarg
        if len(query) > 100:
            importance += 0.1
        if len(response) > 200:
            importance += 0.1
        
        # Més important si té entitats
        entities = self._extract_entities(query + ' ' + response)
        importance += len(entities) * 0.05
        
        # Més important si té tema definit
        if topic and topic != 'general':
            importance += 0.1
        
        return min(1.0, importance)
    
    def store_exchange(self, user: str, query: str, response: str, 
                      topic: str = None, importance: float = None) -> str:
        """
        Emmagatzema un intercanvi a la memòria
        
        Returns:
            ID de la memòria
        """
        # Calcular importància si no es proveeix
        if importance is None:
            importance = self._compute_importance(query, response, topic)
        
        # Crear ID únic
        timestamp = datetime.now()
        memory_id = hashlib.md5(
            f"{user}_{query[:50]}_{timestamp.isoformat()}".encode()
        ).hexdigest()[:12]
        
        exchange = {
            'id': memory_id,
            'timestamp': timestamp.isoformat(),
            'user': user,
            'query': query,
            'response': response,
            'topic': topic,
            'importance': importance,
            'entities': self._extract_entities(query + ' ' + response),
            'access_count': 0,
            'last_accessed': None
        }
        
        # Afegir a memòria a curt termini
        self.short_term.append(exchange)
        
        # Si és important, afegir a llarg termini
        if importance > 0.7:
            lt_key = (user, topic, memory_id) if topic else (user, 'general', memory_id)
            self.long_term[lt_key] = exchange
            self._update_index_for_exchange(exchange)
            self._save_long_term()
        
        self.stats['total_exchanges'] += 1
        if importance > 0.7:
            self.stats['important_memories'] = len(self.long_term)
        
        return memory_id
    
    def _update_index_for_exchange(self, exchange: Dict):
        """Actualitza l'índex per un nou intercanvi"""
        text = exchange['query'] + ' ' + exchange['response']
        words = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower()))
        
        for word in words:
            if word not in self.index:
                self.index[word] = []
            if exchange['id'] not in self.index[word]:
                self.index[word].append(exchange['id'])
    
    def get_relevant_context(self, query: str, user: str = None, 
                            max_items: int = 5) -> List[Dict]:
        """
        Recupera context rellevant per la query actual
        
        Args:
            query: Consulta actual
            user: Usuari (per filtrar)
            max_items: Màxim d'items a retornar
        
        Returns:
            Llista d'intercanvis rellevants ordenats per rellevància
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', query_lower))
        query_entities = self._extract_entities(query)
        
        relevant = []
        seen_ids = set()
        
        # 1. Buscar a curt termini (més recent)
        for exchange in reversed(self.short_term):
            if exchange['id'] in seen_ids:
                continue
            
            # Calcular rellevància
            relevance = 0.0
            
            # Coincidència per usuari
            if user and exchange['user'] == user:
                relevance += 0.2
            
            # Coincidència per paraules
            exchange_text = exchange['query'].lower() + ' ' + exchange['response'].lower()
            exchange_words = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', exchange_text))
            word_overlap = len(query_words & exchange_words)
            if word_overlap > 0:
                relevance += word_overlap * 0.1
            
            # Coincidència per entitats
            entity_overlap = len(set(query_entities) & set(exchange['entities']))
            if entity_overlap > 0:
                relevance += entity_overlap * 0.15
            
            # Coincidència per tema
            if exchange['topic'] and exchange['topic'] in query_lower:
                relevance += 0.3
            
            # Factor de novetat (més recent = més rellevant)
            recency = 1.0 - (len(self.short_term) - self.short_term.index(exchange)) / len(self.short_term) * 0.2
            
            final_relevance = relevance * recency
            
            if final_relevance > 0.3:  # Llindar mínim
                exchange_copy = exchange.copy()
                exchange_copy['relevance'] = final_relevance
                relevant.append(exchange_copy)
                seen_ids.add(exchange['id'])
        
        # 2. Si no n'hi ha prou, buscar a llarg termini
        if len(relevant) < max_items:
            for word in query_words:
                if word in self.index:
                    for mem_id in self.index[word][:3]:  # Limitar
                        # Buscar la memòria corresponent
                        for key, mem in self.long_term.items():
                            if mem.get('id') == mem_id and mem['id'] not in seen_ids:
                                # Calcular rellevància similar
                                relevance = 0.5  # Base per memòria llarga
                                if user and mem.get('user') == user:
                                    relevance += 0.2
                                
                                mem_copy = mem.copy()
                                mem_copy['relevance'] = relevance
                                mem_copy['from_long_term'] = True
                                relevant.append(mem_copy)
                                seen_ids.add(mem['id'])
                                break
        
        # Ordenar per rellevància
        relevant.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Actualitzar access count
        for item in relevant[:max_items]:
            item['access_count'] = item.get('access_count', 0) + 1
            item['last_accessed'] = datetime.now().isoformat()
        
        return relevant[:max_items]
    
    def get_conversation_summary(self, user: str = None) -> Dict:
        """Retorna resum de la conversa"""
        user_exchanges = [e for e in self.short_term if not user or e['user'] == user]
        
        # Extreure temes
        topics = {}
        for e in user_exchanges:
            if e.get('topic'):
                topics[e['topic']] = topics.get(e['topic'], 0) + 1
        
        # Paraules més freqüents
        words = {}
        for e in user_exchanges:
            for word in re.findall(r'\b[a-záéíóúñ]{4,}\b', e['query'].lower()):
                words[word] = words.get(word, 0) + 1
        
        top_words = sorted(words.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_exchanges': len(user_exchanges),
            'unique_topics': list(topics.keys()),
            'main_topic': max(topics.items(), key=lambda x: x[1])[0] if topics else None,
            'top_words': [w for w, _ in top_words],
            'avg_response_length': sum(len(e['response']) for e in user_exchanges) / len(user_exchanges) if user_exchanges else 0
        }
    
    def forget_old_memories(self, days=30):
        """Oblida memòries antigues (per mantenir espai)"""
        from datetime import timedelta
        
        now = datetime.now()
        threshold = now - timedelta(days=days)
        
        to_delete = []
        for key, mem in self.long_term.items():
            mem_time = datetime.fromisoformat(mem['timestamp'])
            if mem_time < threshold and mem.get('access_count', 0) < 2:
                to_delete.append(key)
        
        for key in to_delete:
            del self.long_term[key]
        
        # Reconstruir índex
        self.index = self._build_index()
        self._save_long_term()
        
        print(f"     🧹 Forgot {len(to_delete)} old memories")