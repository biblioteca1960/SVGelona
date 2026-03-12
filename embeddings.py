"""
knowledge/embeddings.py
Sistema d'embeddings semàntics per recuperació intel·ligent
"""

import numpy as np
import pickle
import os
import hashlib
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime

class SemanticEmbeddings:
    """
    Sistema d'embeddings semàntics per:
    - Convertir text a vectors semàntics
    - Calcular similitud entre textos
    - Cachejar embeddings per eficiència
    - Suport multi-idioma
    """
    
    def __init__(self, model_name="paraphrase-multilingual-MiniLM-L12-v2", cache_path="memories/embeddings"):
        """
        Inicialitza el sistema d'embeddings
        
        Args:
            model_name: Model multilingüe (suporta català, castellà, anglès)
            cache_path: Directori per cachejar embeddings
        """
        self.model_name = model_name
        self.cache_path = cache_path
        os.makedirs(cache_path, exist_ok=True)
        
        # Carregar model (descarrega automàticament si no existeix)
        print(f"     📥 Loading embeddings model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            print(f"     ✅ Model loaded successfully")
        except Exception as e:
            print(f"     ⚠️ Error loading model: {e}")
            print(f"     🔧 Falling back to simpler model...")
            # Model de reserva més lleuger
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cache d'embeddings (memòria + disc)
        self.embedding_cache = {}  # {text_hash: embedding_vector}
        self.cache_file = os.path.join(cache_path, "embedding_cache.pkl")
        self._load_cache()
        
        # Estadístiques
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_embeddings': len(self.embedding_cache)
        }
        
        print(f"     💾 Embedding cache: {len(self.embedding_cache)} items")
    
    def _load_cache(self):
        """Carrega la cache d'embeddings de disc"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                print(f"     📖 Loaded {len(self.embedding_cache)} cached embeddings")
            except Exception as e:
                print(f"     ⚠️ Could not load embedding cache: {e}")
                self.embedding_cache = {}
    
    def _save_cache(self):
        """Guarda la cache d'embeddings a disc"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
        except Exception as e:
            print(f"     ⚠️ Could not save embedding cache: {e}")
    
    def _hash_text(self, text: str) -> str:
        """Crea un hash únic per un text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _chunk_text(self, text: str, max_chars: int = 500) -> List[str]:
        """
        Divideix text llarg en fragments més petits
        """
        if len(text) <= max_chars:
            return [text]
        
        # Dividir per frases
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) <= max_chars:
                current_chunk.append(sentence)
                current_length += len(sentence)
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = len(sentence)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def get_embedding(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Obté l'embedding per un text (amb cache)
        """
        if not text or len(text.strip()) < 5:
            return np.zeros(384)  # Dimensió per defecte
        
        text_hash = self._hash_text(text)
        
        # Comprovar cache
        if use_cache and text_hash in self.embedding_cache:
            self.stats['cache_hits'] += 1
            return self.embedding_cache[text_hash]
        
        self.stats['cache_misses'] += 1
        
        # Generar embedding
        try:
            embedding = self.model.encode(text, normalize_embeddings=True)
            
            # Guardar a cache
            if use_cache:
                self.embedding_cache[text_hash] = embedding
                # Guardar cada 100 embeddings nous
                if len(self.embedding_cache) % 100 == 0:
                    self._save_cache()
            
            return embedding
            
        except Exception as e:
            print(f"     ⚠️ Error generating embedding: {e}")
            return np.zeros(384)
    
    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Obté embeddings per múltiples textos (més eficient)
        """
        results = []
        texts_to_encode = []
        text_indices = []
        
        for i, text in enumerate(texts):
            text_hash = self._hash_text(text)
            if text_hash in self.embedding_cache:
                results.append(self.embedding_cache[text_hash])
                self.stats['cache_hits'] += 1
            else:
                results.append(None)
                texts_to_encode.append(text)
                text_indices.append(i)
        
        if texts_to_encode:
            try:
                new_embeddings = self.model.encode(texts_to_encode, normalize_embeddings=True)
                
                for idx, emb in zip(text_indices, new_embeddings):
                    results[idx] = emb
                    text_hash = self._hash_text(texts[idx])
                    self.embedding_cache[text_hash] = emb
                    self.stats['cache_misses'] += 1
                
                # Guardar cache si hi ha canvis
                if texts_to_encode:
                    self._save_cache()
                    
            except Exception as e:
                print(f"     ⚠️ Error generating batch embeddings: {e}")
                for idx in text_indices:
                    results[idx] = np.zeros(384)
        
        self.stats['total_embeddings'] = len(self.embedding_cache)
        return results
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud semàntica entre dos textos
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        # Similaritat cosinus
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        return float(similarity)
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Troba els candidats més similars semànticament a la query
        """
        if not candidates:
            return []
        
        # Obtenir embedding de la query
        query_emb = self.get_embedding(query)
        
        # Obtenir embeddings dels candidats (batch)
        candidate_embs = self.get_embeddings_batch(candidates)
        
        # Calcular similituds
        similarities = []
        for i, cand_emb in enumerate(candidate_embs):
            if cand_emb is not None:
                sim = cosine_similarity([query_emb], [cand_emb])[0][0]
                similarities.append((candidates[i], float(sim)))
        
        # Ordenar per similitud
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_cache_stats(self) -> Dict:
        """Retorna estadístiques de la cache"""
        hit_rate = self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) \
                  if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0 else 0
        
        return {
            'cache_size': len(self.embedding_cache),
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate': hit_rate,
            'model': self.model_name
        }