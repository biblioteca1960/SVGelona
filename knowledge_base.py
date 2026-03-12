"""
knowledge/knowledge_base.py
Base de coneixement unificada amb múltiples fonts
"""

import json
import os
import pickle
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from collections import defaultdict

class KnowledgeBase:
    """
    Base de coneixement unificada que integra:
    - Wikipedia
    - PDFs locals
    - Memòria de converses
    - Coneixement après
    
    Amb indexació semàntica i recuperació intel·ligent
    """
    
    def __init__(self, embeddings, storage_path="memories/knowledge"):
        self.embeddings = embeddings
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Índex per tipus de font
        self.documents = {
            'wikipedia': [],      # Articles de Wikipedia
            'pdf': [],           # Documents PDF
            'conversation': [],  # Intercanvis importants
            'learned': []        # Coneixement après
        }
        
        # Índex semàntic (embeddings per document)
        self.semantic_index = defaultdict(list)  # {doc_id: embedding}
        
        # Metadades
        self.metadata = {}  # {doc_id: metadata}
        
        # Cache de recuperació
        self.retrieval_cache = {}  # {query_hash: results}
        
        # Carregar dades persistents
        self._load()
        
        print(f"  ✅ KnowledgeBase initialized")
        print(f"     📚 Wikipedia: {len(self.documents['wikipedia'])} articles")
        print(f"     📄 PDFs: {len(self.documents['pdf'])} documents")
        print(f"     💬 Conversations: {len(self.documents['conversation'])} items")
        print(f"     🧠 Learned: {len(self.documents['learned'])} items")
    
    def _get_doc_file(self, doc_type: str) -> str:
        """Retorna el camí del fitxer per un tipus de document"""
        return os.path.join(self.storage_path, f"{doc_type}_docs.pkl")
    
    def _get_metadata_file(self) -> str:
        """Retorna el camí del fitxer de metadades"""
        return os.path.join(self.storage_path, "metadata.pkl")
    
    def _load(self):
        """Carrega dades persistents"""
        # Carregar documents per tipus
        for doc_type in self.documents:
            doc_file = self._get_doc_file(doc_type)
            if os.path.exists(doc_file):
                try:
                    with open(doc_file, 'rb') as f:
                        self.documents[doc_type] = pickle.load(f)
                except Exception as e:
                    print(f"     ⚠️ Could not load {doc_type} documents: {e}")
        
        # Carregar metadades
        meta_file = self._get_metadata_file()
        if os.path.exists(meta_file):
            try:
                with open(meta_file, 'rb') as f:
                    self.metadata = pickle.load(f)
            except Exception as e:
                print(f"     ⚠️ Could not load metadata: {e}")
        
        # Reconstruir índex semàntic
        self._rebuild_semantic_index()
    
    def _save(self, doc_type: str = None):
        """Guarda dades persistents"""
        if doc_type:
            # Guardar només un tipus
            doc_file = self._get_doc_file(doc_type)
            try:
                with open(doc_file, 'wb') as f:
                    pickle.dump(self.documents[doc_type], f)
            except Exception as e:
                print(f"     ⚠️ Could not save {doc_type} documents: {e}")
        else:
            # Guardar tots
            for dt in self.documents:
                doc_file = self._get_doc_file(dt)
                try:
                    with open(doc_file, 'wb') as f:
                        pickle.dump(self.documents[dt], f)
                except Exception as e:
                    print(f"     ⚠️ Could not save {dt} documents: {e}")
        
        # Guardar metadades
        meta_file = self._get_metadata_file()
        try:
            with open(meta_file, 'wb') as f:
                pickle.dump(self.metadata, f)
        except Exception as e:
            print(f"     ⚠️ Could not save metadata: {e}")
    
    def _rebuild_semantic_index(self):
        """Reconstrueix l'índex semàntic"""
        self.semantic_index.clear()
        
        for doc_type, docs in self.documents.items():
            for i, doc in enumerate(docs):
                doc_id = f"{doc_type}_{i}"
                
                # Generar embedding pel document
                text = self._get_doc_text(doc)
                if text:
                    embedding = self.embeddings.get_embedding(text)
                    self.semantic_index[doc_id] = embedding
                    
                    # Guardar metadades
                    if doc_id not in self.metadata:
                        self.metadata[doc_id] = {
                            'type': doc_type,
                            'index': i,
                            'added': datetime.now().isoformat(),
                            'access_count': 0
                        }
    
    def _get_doc_text(self, doc: Any) -> str:
        """Extreu text d'un document segons el seu tipus"""
        if isinstance(doc, dict):
            # Wikipedia o PDF
            if 'summary' in doc:
                return doc['summary']
            elif 'extract' in doc:
                return doc['extract']
            elif 'content' in doc:
                return doc['content']
            elif 'excerpt' in doc:
                return doc['excerpt']
        elif isinstance(doc, str):
            return doc
        
        # Si és un intercanvi de conversa
        if hasattr(doc, 'get'):
            return doc.get('query', '') + ' ' + doc.get('response', '')
        
        return str(doc)
    
    def _compute_doc_id(self, doc_type: str, content: str) -> str:
        """Crea un ID únic per un document"""
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        return f"{doc_type}_{content_hash}"
    
    def add_wikipedia_article(self, title: str, summary: str, url: str = None):
        """Afegeix un article de Wikipedia"""
        doc = {
            'type': 'wikipedia',
            'title': title,
            'summary': summary,
            'url': url,
            'added': datetime.now().isoformat()
        }
        
        # Evitar duplicats
        for existing in self.documents['wikipedia']:
            if existing.get('title') == title:
                return
        
        self.documents['wikipedia'].append(doc)
        
        # Actualitzar índex
        doc_id = self._compute_doc_id('wikipedia', summary)
        embedding = self.embeddings.get_embedding(summary)
        self.semantic_index[doc_id] = embedding
        self.metadata[doc_id] = {
            'type': 'wikipedia',
            'title': title,
            'added': datetime.now().isoformat(),
            'access_count': 0
        }
        
        self._save('wikipedia')
    
    def add_pdf_document(self, title: str, content: str, filename: str, topic: str = None):
        """Afegeix un document PDF"""
        # Dividir en fragments si és molt llarg
        chunks = self.embeddings._chunk_text(content, max_chars=1000)
        
        for i, chunk in enumerate(chunks):
            doc = {
                'type': 'pdf',
                'title': f"{title} (part {i+1})",
                'filename': filename,
                'content': chunk,
                'topic': topic,
                'added': datetime.now().isoformat()
            }
            
            self.documents['pdf'].append(doc)
            
            doc_id = self._compute_doc_id('pdf', chunk)
            embedding = self.embeddings.get_embedding(chunk)
            self.semantic_index[doc_id] = embedding
            self.metadata[doc_id] = {
                'type': 'pdf',
                'title': title,
                'topic': topic,
                'added': datetime.now().isoformat(),
                'access_count': 0
            }
        
        self._save('pdf')
    
    def add_conversation_memory(self, exchange: Dict):
        """Afegeix un intercanvi important a la base de coneixement"""
        if exchange.get('importance', 0) >= 0.8:  # Només memòries molt importants
            doc = {
                'type': 'conversation',
                'query': exchange.get('query', ''),
                'response': exchange.get('response', ''),
                'topic': exchange.get('topic'),
                'user': exchange.get('user'),
                'timestamp': exchange.get('timestamp'),
                'importance': exchange.get('importance')
            }
            
            self.documents['conversation'].append(doc)
            
            text = doc['query'] + ' ' + doc['response']
            doc_id = self._compute_doc_id('conversation', text)
            embedding = self.embeddings.get_embedding(text)
            self.semantic_index[doc_id] = embedding
            self.metadata[doc_id] = {
                'type': 'conversation',
                'topic': doc['topic'],
                'added': datetime.now().isoformat(),
                'access_count': 0
            }
            
            self._save('conversation')
    
    def search(self, query: str, top_k: int = 5, 
               sources: List[str] = None) -> List[Dict]:
        """
        Cerca semàntica a la base de coneixement
        
        Args:
            query: Consulta
            top_k: Nombre de resultats
            sources: Tipus de fonts a cercar (None = totes)
        
        Returns:
            Llista de resultats amb rellevància
        """
        if not self.semantic_index:
            return []
        
        # Comprovar cache
        cache_key = hashlib.md5(f"{query}_{top_k}_{sources}".encode()).hexdigest()
        if cache_key in self.retrieval_cache:
            cache_time, results = self.retrieval_cache[cache_key]
            # Cache vàlida per 1 hora
            if (datetime.now() - cache_time).seconds < 3600:
                return results
        
        # Obtenir embedding de la query
        query_emb = self.embeddings.get_embedding(query)
        
        # Calcular similitud amb tots els documents
        similarities = []
        
        for doc_id, doc_emb in self.semantic_index.items():
            # Comprovar font si s'especifica
            if sources and self.metadata[doc_id]['type'] not in sources:
                continue
            
            sim = cosine_similarity([query_emb], [doc_emb])[0][0]
            similarities.append((doc_id, float(sim)))
        
        # Ordenar per similitud
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Recuperar documents
        results = []
        for doc_id, sim in similarities[:top_k]:
            meta = self.metadata[doc_id]
            doc_type = meta['type']
            doc_idx = meta['index'] if 'index' in meta else 0
            
            # Localitzar el document
            if doc_idx < len(self.documents[doc_type]):
                doc = self.documents[doc_type][doc_idx]
                
                # Actualitzar access count
                meta['access_count'] = meta.get('access_count', 0) + 1
                meta['last_accessed'] = datetime.now().isoformat()
                
                results.append({
                    'id': doc_id,
                    'type': doc_type,
                    'content': self._get_doc_text(doc),
                    'metadata': doc if isinstance(doc, dict) else {'text': doc},
                    'relevance': sim,
                    'source_info': meta
                })
        
        # Guardar a cache
        self.retrieval_cache[cache_key] = (datetime.now(), results)
        
        # Netejar cache vella (>100 entrades)
        if len(self.retrieval_cache) > 100:
            # Eliminar les més antigues
            sorted_cache = sorted(self.retrieval_cache.items(), 
                                 key=lambda x: x[1][0])
            for old_key, _ in sorted_cache[:-50]:
                del self.retrieval_cache[old_key]
        
        return results
    
    def get_knowledge_summary(self, query: str) -> Optional[str]:
        """
        Obté un resum del coneixement rellevant per la query
        """
        results = self.search(query, top_k=3)
        
        if not results:
            return None
        
        summary = "📚 **Coneixement rellevant:**\n\n"
        
        for i, result in enumerate(results, 1):
            icon = {
                'wikipedia': '🌐',
                'pdf': '📄',
                'conversation': '💭',
                'learned': '🧠'
            }.get(result['type'], '📌')
            
            title = result['metadata'].get('title', 'Informació')
            content = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            
            summary += f"{icon} **{title}** (rellevància: {result['relevance']:.2f})\n"
            summary += f"   {content}\n\n"
        
        return summary
    
    def get_stats(self) -> Dict:
        """Retorna estadístiques de la base de coneixement"""
        return {
            'total_documents': sum(len(docs) for docs in self.documents.values()),
            'by_type': {k: len(v) for k, v in self.documents.items()},
            'semantic_index_size': len(self.semantic_index),
            'cache_size': len(self.retrieval_cache)
        }