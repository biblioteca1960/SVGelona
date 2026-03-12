"""
personality/emotional_memory.py
Memòria emocional amb records significatius
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
import os

class EmotionalMemory:
    """
    Memòria emocional que:
    - Guarda records amb càrrega emocional
    - Recupera records per estat d'ànim
    - Pondera records per rellevància emocional
    """
    
    def __init__(self, storage_path="memories/emotional"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        self.memories = []
        self.emotional_index = {}  # {emotion: [memory_ids]}
        
        # Dimensions emocionals (Plutchik)
        self.emotions = {
            'joy': {'valence': 0.9, 'arousal': 0.7},
            'trust': {'valence': 0.7, 'arousal': 0.3},
            'fear': {'valence': 0.2, 'arousal': 0.8},
            'surprise': {'valence': 0.5, 'arousal': 0.9},
            'sadness': {'valence': 0.2, 'arousal': 0.3},
            'disgust': {'valence': 0.1, 'arousal': 0.4},
            'anger': {'valence': 0.1, 'arousal': 0.9},
            'anticipation': {'valence': 0.6, 'arousal': 0.6}
        }
        
        self._load()
        print(f"  ✅ EmotionalMemory initialized with {len(self.memories)} memories")
    
    def _get_storage_file(self) -> str:
        return os.path.join(self.storage_path, "emotional_memories.json")
    
    def _load(self):
        """Carrega memòries emocionals"""
        storage_file = self._get_storage_file()
        if os.path.exists(storage_file):
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    self.memories = json.load(f)
                self._rebuild_index()
            except Exception as e:
                print(f"     ⚠️ Could not load emotional memories: {e}")
    
    def _save(self):
        """Guarda memòries emocionals"""
        storage_file = self._get_storage_file()
        try:
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories[-100:], f, indent=2, ensure_ascii=False)  # Últimes 100
        except Exception as e:
            print(f"     ⚠️ Could not save emotional memories: {e}")
    
    def _rebuild_index(self):
        """Reconstrueix índex emocional"""
        self.emotional_index.clear()
        for memory in self.memories:
            for emotion in memory.get('emotions', []):
                if emotion not in self.emotional_index:
                    self.emotional_index[emotion] = []
                self.emotional_index[emotion].append(memory['id'])
    
    def add_memory(self, content: str, emotions: List[str], 
                   intensity: float, context: Dict = None):
        """
        Afegeix un record emocional
        
        Args:
            content: Contingut del record
            emotions: Llista d'emocions associades
            intensity: Intensitat (0-1)
            context: Context addicional
        """
        memory = {
            'id': f"mem_{datetime.now().timestamp()}",
            'content': content,
            'emotions': emotions,
            'intensity': intensity,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'recall_count': 0,
            'last_recall': None
        }
        
        self.memories.append(memory)
        
        # Actualitzar índex
        for emotion in emotions:
            if emotion not in self.emotional_index:
                self.emotional_index[emotion] = []
            self.emotional_index[emotion].append(memory['id'])
        
        # Mantenir memòria limitada
        if len(self.memories) > 200:
            self.memories = self.memories[-200:]
        
        self._save()
    
    def recall_by_emotion(self, target_emotion: str, max_memories: int = 3) -> List[Dict]:
        """
        Recupera records per emoció
        
        Args:
            target_emotion: Emoció a buscar
            max_memories: Màxim de records
        
        Returns:
            Llista de records ordenats per rellevància
        """
        relevant = []
        
        if target_emotion in self.emotional_index:
            for mem_id in self.emotional_index[target_emotion][-10:]:  # Últims 10
                for mem in self.memories:
                    if mem['id'] == mem_id:
                        # Calcular rellevància
                        relevance = mem['intensity']
                        
                        # Boost per records recents
                        mem_time = datetime.fromisoformat(mem['timestamp'])
                        time_diff = (datetime.now() - mem_time).days
                        relevance *= (1 - time_diff * 0.01)  # Decaïment temporal
                        
                        mem_copy = mem.copy()
                        mem_copy['relevance'] = max(0.1, relevance)
                        relevant.append(mem_copy)
                        break
        
        # Ordenar per rellevància
        relevant.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Actualitzar recomptes
        for mem in relevant[:max_memories]:
            mem['recall_count'] += 1
            mem['last_recall'] = datetime.now().isoformat()
        
        return relevant[:max_memories]
    
    def recall_by_context(self, current_emotional_state: Dict) -> Optional[Dict]:
        """
        Recupera el record més rellevant per l'estat emocional actual
        """
        best_memory = None
        best_score = -1
        
        target_valence = current_emotional_state.get('valence', 0.5)
        target_arousal = current_emotional_state.get('arousal', 0.5)
        
        for memory in self.memories[-50:]:  # Últims 50
            # Calcular similitud emocional
            memory_emotions = memory.get('emotions', [])
            if not memory_emotions:
                continue
            
            # Puntuar per emoció principal
            primary_emotion = memory_emotions[0]
            if primary_emotion in self.emotions:
                emotion_valence = self.emotions[primary_emotion]['valence']
                emotion_arousal = self.emotions[primary_emotion]['arousal']
                
                # Similitud euclidiana en espai emocional
                valence_diff = abs(emotion_valence - target_valence)
                arousal_diff = abs(emotion_arousal - target_arousal)
                
                similarity = 1 - (valence_diff + arousal_diff) / 2
                
                # Pes per intensitat i temps
                score = similarity * memory['intensity']
                
                # Penalitzar records recents per evitar repetició
                if memory.get('last_recall'):
                    last = datetime.fromisoformat(memory['last_recall'])
                    hours_since = (datetime.now() - last).total_seconds() / 3600
                    if hours_since < 24:
                        score *= hours_since / 24
                
                if score > best_score:
                    best_score = score
                    best_memory = memory
        
        if best_memory:
            best_memory['recall_count'] += 1
            best_memory['last_recall'] = datetime.now().isoformat()
            best_memory['relevance'] = best_score
        
        return best_memory
    
    def get_emotional_summary(self) -> str:
        """Retorna resum de l'estat emocional de la memòria"""
        if not self.memories:
            return "No hi ha records emocionals significatius."
        
        # Comptar emocions
        emotion_counts = defaultdict(int)
        for mem in self.memories:
            for emotion in mem.get('emotions', []):
                emotion_counts[emotion] += 1
        
        # Emocions dominants
        dominant = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Record més intens
        most_intense = max(self.memories, key=lambda x: x['intensity'])
        
        return f"""
📊 **Memòria Emocional**:
• Total records: {len(self.memories)}
• Emocions dominants: {', '.join([f"{e} ({c})" for e, c in dominant])}
• Record més intens: {most_intense['content'][:50]}...
• Intensitat màxima: {most_intense['intensity']:.2f}
"""