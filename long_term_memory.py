"""
memory/long_term_memory.py
Memòria a llarg termini amb persistència i indexació

VERSIÓ CORREGIDA: Accepta tant 'importance' com 'importancia' com a paràmetres
"""

import json
import os
import hashlib
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import re

class LongTermMemory:
    """
    Memòria a llarg termini amb:
    - Emmagatzematge persistent
    - Indexació per temes i paraules clau
    - Decaïment temporal
    - Consolidació de records importants
    """
    
    def __init__(self, storage_path="memories/long_term"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Memòria principal
        self.memories = []  # Llista de dicts
        self.memory_index = {
            'by_topic': defaultdict(list),
            'by_keyword': defaultdict(list),
            'by_date': defaultdict(list),
            'by_importance': defaultdict(list)
        }
        
        # Estadístiques d'accés
        self.access_stats = defaultdict(lambda: {
            'count': 0,
            'last_access': None,
            'avg_relevance': 0.0
        })
        
        # Paràmetres de consolidació
        self.importance_threshold = 0.7
        self.decay_rate = 0.01  # Decaïment per dia
        self.consolidation_interval = 7  # dies
        
        # Carregar dades persistents
        self._load()
        
        print(f"  ✅ LongTermMemory initialized")
        print(f"     📚 Total memories: {len(self.memories)}")
        print(f"     📊 Index size: {sum(len(v) for v in self.memory_index['by_topic'].values())} entries")
    
    def _get_memory_file(self) -> str:
        """Retorna el camí del fitxer de memòria"""
        return os.path.join(self.storage_path, "long_term_memory.pkl")
    
    def _get_index_file(self) -> str:
        """Retorna el camí del fitxer d'índex"""
        return os.path.join(self.storage_path, "memory_index.pkl")
    
    def _load(self):
        """Carrega memòria persistent"""
        memory_file = self._get_memory_file()
        index_file = self._get_index_file()
        
        if os.path.exists(memory_file):
            try:
                with open(memory_file, 'rb') as f:
                    self.memories = pickle.load(f)
            except Exception as e:
                print(f"     ⚠️ Could not load memories: {e}")
                self.memories = []
        
        if os.path.exists(index_file):
            try:
                with open(index_file, 'rb') as f:
                    self.memory_index = pickle.load(f)
            except Exception as e:
                print(f"     ⚠️ Could not load index: {e}")
                self._rebuild_index()
    
    def _save(self):
        """Guarda memòria persistent"""
        memory_file = self._get_memory_file()
        index_file = self._get_index_file()
        
        try:
            with open(memory_file, 'wb') as f:
                pickle.dump(self.memories[-1000:], f)  # Últimes 1000
        except Exception as e:
            print(f"     ⚠️ Could not save memories: {e}")
        
        try:
            with open(index_file, 'wb') as f:
                pickle.dump(self.memory_index, f)
        except Exception as e:
            print(f"     ⚠️ Could not save index: {e}")
    
    def _rebuild_index(self):
        """Reconstrueix l'índex des de zero"""
        self.memory_index = {
            'by_topic': defaultdict(list),
            'by_keyword': defaultdict(list),
            'by_date': defaultdict(list),
            'by_importance': defaultdict(list)
        }
        
        for mem in self.memories:
            mem_id = mem.get('id')
            if not mem_id:
                continue
            
            # Indexar per tema
            topic = mem.get('topic', 'general')
            self.memory_index['by_topic'][topic].append(mem_id)
            
            # Indexar per paraules clau
            text = mem.get('query', '') + ' ' + mem.get('response', '')
            keywords = self._extract_keywords(text)
            for kw in keywords:
                self.memory_index['by_keyword'][kw].append(mem_id)
            
            # Indexar per data
            date = mem.get('date', 'unknown')
            self.memory_index['by_date'][date[:10]].append(mem_id)
            
            # Indexar per importància
            importance = mem.get('importance', 0.5)
            imp_level = int(importance * 10)
            self.memory_index['by_importance'][imp_level].append(mem_id)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extreu paraules clau d'un text"""
        # Netejar text
        text = text.lower()
        text = re.sub(r'[^\w\sáéíóúñ]', ' ', text)
        
        # Extreure paraules significatives (4+ lletres)
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text)
        
        # Filtrar stopwords
        stopwords = {'aquest', 'aquesta', 'això', 'sobre', 'entre', 'durant',
                    'abans', 'després', 'sempre', 'mai', 'quan', 'com', 'però',
                    'this', 'that', 'these', 'those', 'with', 'from', 'have'}
        
        return [w for w in words if w not in stopwords][:10]  # Limitar
    
    def _compute_importance(self, query: str, response: str, context: Dict = None) -> float:
        """Calcula la importància d'un record"""
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
        entities = re.findall(r'\b[A-Z][a-záéíóúñ]+\b', query)
        importance += len(entities) * 0.05
        
        # Més important si és tècnic
        technical = {'teorema', 'funció', 'equació', 'derivada', 'integral',
                    'geometria', 'simetria', 'primer', 'nombre'}
        if any(term in query.lower() for term in technical):
            importance += 0.2
        
        # Context addicional
        if context:
            if context.get('user_reaction') == 'positive':
                importance += 0.2
            elif context.get('user_reaction') == 'negative':
                importance -= 0.1
            
            if context.get('topic_confidence', 0) > 0.8:
                importance += 0.1
        
        return max(0.1, min(1.0, importance))
    
    def add_memory(self, query: str, response: str, 
                  topic: str = None, context: Dict = None, 
                  importance: float = None, importancia: float = None) -> str:
        """
        Afegeix un record a la memòria a llarg termini
        
        Args:
            query: Consulta original
            response: Resposta del sistema
            topic: Tema associat (opcional)
            context: Context addicional (opcional)
            importance: Importància del record (0-1) en anglès
            importancia: Importància del record (0-1) en català/castellà
        
        Returns:
            ID del record o None si no és prou important
        """
        # Determinar quina importància utilitzar (prioritat: importance > importancia > calculada)
        if importance is not None:
            final_importance = importance
        elif importancia is not None:
            final_importance = importancia
        else:
            final_importance = self._compute_importance(query, response, context)
        
        # Només guardar si és prou important
        if final_importance < self.importance_threshold:
            return None
        
        # Crear ID únic
        timestamp = datetime.now()
        mem_id = hashlib.md5(
            f"{query}_{response}_{timestamp.isoformat()}".encode()
        ).hexdigest()[:16]
        
        memory = {
            'id': mem_id,
            'query': query,
            'response': response,
            'topic': topic or 'general',
            'importance': final_importance,
            'date': timestamp.isoformat(),
            'context': context or {},
            'access_count': 0,
            'last_accessed': None,
            'consolidated': False
        }
        
        self.memories.append(memory)
        
        # Actualitzar índex
        self.memory_index['by_topic'][memory['topic']].append(mem_id)
        
        keywords = self._extract_keywords(query + ' ' + response)
        for kw in keywords:
            self.memory_index['by_keyword'][kw].append(mem_id)
        
        date_key = timestamp.strftime('%Y-%m-%d')
        self.memory_index['by_date'][date_key].append(mem_id)
        
        imp_level = int(final_importance * 10)
        self.memory_index['by_importance'][imp_level].append(mem_id)
        
        # Guardar cada 10 records
        if len(self.memories) % 10 == 0:
            self._save()
        
        return mem_id
    
    def recall(self, query: str, top_k: int = 3, 
              min_importance: float = 0.0) -> List[Dict]:
        """
        Recupera records rellevants per una consulta
        
        Args:
            query: Consulta
            top_k: Nombre màxim de records
            min_importance: Importància mínima
        
        Returns:
            Llista de records ordenats per rellevància
        """
        keywords = self._extract_keywords(query)
        
        if not keywords:
            return []
        
        # Puntuació de records
        scores = defaultdict(float)
        
        for kw in keywords:
            if kw in self.memory_index['by_keyword']:
                for mem_id in self.memory_index['by_keyword'][kw]:
                    # Puntuació base per coincidència
                    scores[mem_id] += 1.0
        
        if not scores:
            return []
        
        # Recuperar records complets
        results = []
        memory_dict = {m['id']: m for m in self.memories}
        
        for mem_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k*2]:
            if mem_id in memory_dict:
                mem = memory_dict[mem_id].copy()
                
                # Calcular rellevància final
                relevance = score / len(keywords)  # Normalitzar
                relevance *= mem['importance']  # Pes per importància
                
                # Decaïment temporal
                mem_date = datetime.fromisoformat(mem['date'])
                days_old = (datetime.now() - mem_date).days
                time_decay = max(0.5, 1.0 - (days_old * self.decay_rate))
                relevance *= time_decay
                
                if relevance >= min_importance:
                    mem['relevance'] = relevance
                    results.append(mem)
                    
                    # Actualitzar estadístiques
                    self.access_stats[mem_id]['count'] += 1
                    self.access_stats[mem_id]['last_access'] = datetime.now().isoformat()
                    self.access_stats[mem_id]['avg_relevance'] = (
                        self.access_stats[mem_id]['avg_relevance'] * 0.9 + relevance * 0.1
                    )
        
        # Ordenar per rellevància
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Actualitzar access count dels seleccionats
        for mem in results[:top_k]:
            for m in self.memories:
                if m['id'] == mem['id']:
                    m['access_count'] = m.get('access_count', 0) + 1
                    m['last_accessed'] = datetime.now().isoformat()
                    break
        
        return results[:top_k]
    
    def recall_by_topic(self, topic: str, top_k: int = 3) -> List[Dict]:
        """Recupera records per tema"""
        if topic not in self.memory_index['by_topic']:
            return []
        
        mem_ids = self.memory_index['by_topic'][topic][-top_k:]
        
        results = []
        memory_dict = {m['id']: m for m in self.memories}
        
        for mem_id in mem_ids:
            if mem_id in memory_dict:
                mem = memory_dict[mem_id].copy()
                mem['relevance'] = 0.8  # Rellevància base per tema
                results.append(mem)
        
        return results
    
    def recall_by_date(self, days_ago: int, top_k: int = 10) -> List[Dict]:
        """Recupera records d'uns quants dies enrere"""
        target_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        if target_date not in self.memory_index['by_date']:
            return []
        
        mem_ids = self.memory_index['by_date'][target_date][-top_k:]
        
        results = []
        memory_dict = {m['id']: m for m in self.memories}
        
        for mem_id in mem_ids:
            if mem_id in memory_dict:
                results.append(memory_dict[mem_id])
        
        return results
    
    def consolidate(self):
        """Consolida records importants i elimina els irrellevants"""
        print(f"     🔄 Consolidating long-term memory...")
        
        now = datetime.now()
        to_keep = []
        
        for mem in self.memories:
            mem_date = datetime.fromisoformat(mem['date'])
            days_old = (now - mem_date).days
            
            # Decidir si mantenir
            keep = False
            
            # Records molt importants sempre es mantenen
            if mem['importance'] > 0.9:
                keep = True
                mem['consolidated'] = True
            
            # Records importants i accessats recentment
            elif mem['importance'] > 0.7:
                stats = self.access_stats.get(mem['id'], {})
                if stats.get('count', 0) > 3 or days_old < 30:
                    keep = True
                    mem['consolidated'] = True
            
            # Records amb accessos freqüents
            else:
                stats = self.access_stats.get(mem['id'], {})
                if stats.get('count', 0) > 10:
                    keep = True
                    mem['consolidated'] = True
                elif days_old < 7:  # Records recents
                    keep = True
            
            if keep:
                to_keep.append(mem)
        
        removed = len(self.memories) - len(to_keep)
        self.memories = to_keep
        
        # Reconstruir índex
        self._rebuild_index()
        self._save()
        
        print(f"     ✅ Consolidation complete: {removed} memories removed")
    
    def get_memory_stats(self) -> Dict:
        """Retorna estadístiques de memòria"""
        return {
            'total_memories': len(self.memories),
            'by_importance': {
                'high': len([m for m in self.memories if m['importance'] > 0.8]),
                'medium': len([m for m in self.memories if 0.5 < m['importance'] <= 0.8]),
                'low': len([m for m in self.memories if m['importance'] <= 0.5])
            },
            'by_topic': {k: len(v) for k, v in self.memory_index['by_topic'].items()},
            'consolidated': len([m for m in self.memories if m.get('consolidated', False)]),
            'avg_importance': np.mean([m['importance'] for m in self.memories]) if self.memories else 0
        }