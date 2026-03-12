"""
knowledge/rag_system.py
Sistema de Retrieval Augmented Generation complet
VERSIÓ AMB FILTRATGE DE RESULTATS GENÈRICS I MILLORES PER A PERSONATGES HISTÒRICS
"""

from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

class RAGSystem:
    """
    Sistema RAG (Retrieval Augmented Generation) que:
    - Recupera informació rellevant de múltiples fonts
    - Genera respostes enriquides amb el context
    - Manté traçabilitat de les fonts
    - 🔥 Filtra resultats genèrics (com "¿Dónde está Wally?" o "A.N.I.M.A.L.")
    """
    
    def __init__(self, knowledge_base, embeddings, wikipedia_api=None, doc_retriever=None):
        self.knowledge_base = knowledge_base
        self.embeddings = embeddings
        self.wikipedia = wikipedia_api
        self.doc_retriever = doc_retriever
        
        # 🔥 Paraules a filtrar (resultats massa genèrics) - AMPLIAT
        self.generic_terms = [
            'wally', 'waldo', 'dónde está wally', 'where is wally',
            'a.n.i.m.a.l.', 'animal', 'rock', 'band', 'grupo', 'música', 'musica',
            'qué', 'que', 'què', 'who', 'what', 'where', 'when', 'why', 'how',
            'parchís', 'parchis', 'juego', 'game', 'ajedrez', 'chess',
            'canción', 'song', 'álbum', 'album', 'disco', 'record'
        ]
        
        # 🔥 Llista de conceptes generals que haurien d'anar a Wikipedia normal
        self.general_concepts = [
            'animal', 'planta', 'mineral', 'montaña', 'río', 'océano', 'mar',
            'pez', 'ave', 'mamífero', 'reptil', 'insecto', 'árbol', 'flor'
        ]
        
        # Cache de consultes recents
        self.query_cache = {}
        
        # Estadístiques
        self.stats = {
            'total_queries': 0,
            'wikipedia_used': 0,
            'pdf_used': 0,
            'memory_used': 0,
            'cache_hits': 0,
            'filtered_results': 0
        }
        
        print(f"  ✅ RAGSystem initialized with filtering")
        print(f"     🔍 Sources: Wikipedia, PDFs, Conversation Memory")
        print(f"     🔍 Filtering: A.N.I.M.A.L., games, music bands")
    
    def _classify_query(self, query: str) -> Dict:
        """Classifica la query per determinar les millors fonts"""
        query_lower = query.lower()
        
        # Detectar tipus de consulta
        is_factual = any(word in query_lower for word in [
            'què és', 'qué es', 'what is', 'who is', 'define',
            'explica', 'explain', 'història', 'history', 'biografia'
        ])
        
        is_scientific = any(word in query_lower for word in [
            'teorema', 'theorem', 'física', 'physics', 'matemàtiques',
            'mathematics', 'quàntic', 'quantum', 'relativitat'
        ])
        
        is_conversational = any(word in query_lower for word in [
            'recordes', 'remember', 'abans', 'before', 'vas dir'
        ])
        
        # Detectar consultes de ubicació
        is_location = any(word in query_lower for word in [
            'dónde está', 'where is', 'on és', 'en donde', 'ubicación'
        ])
        
        return {
            'is_factual': is_factual,
            'is_scientific': is_scientific,
            'is_conversational': is_conversational,
            'is_location': is_location,
            'needs_wikipedia': is_factual or is_scientific or is_location,
            'needs_pdf': is_scientific,
            'needs_memory': is_conversational
        }
    
    # 🔥 Funció per filtrar resultats genèrics - MILLORADA
    def _filter_generic_results(self, results: List[Dict], original_query: str = None) -> List[Dict]:
        """
        Filtra resultats massa genèrics com "¿Dónde está Wally?" o "A.N.I.M.A.L."
        
        Args:
            results: Llista de resultats a filtrar
            original_query: Consulta original per contextualitzar
        
        Returns:
            Llista de resultats filtrats
        """
        filtered = []
        
        # Si tenim consulta original, comprovar si és un concepte general
        is_general_concept = False
        if original_query:
            query_lower = original_query.lower()
            # Extreure paraula clau
            words = re.findall(r'\b[a-záéíóúñ]{4,}\b', query_lower)
            if words:
                main_word = max(words, key=len)
                if main_word in self.general_concepts:
                    is_general_concept = True
                    print(f"         🔍 General concept detected: {main_word}")
        
        for r in results:
            title_lower = r.get('title', '').lower()
            content_lower = r.get('content', '').lower() if 'content' in r else ''
            
            # 🔥 Comprovar si conté termes genèrics
            is_generic = False
            
            # Si és un concepte general, no filtrar resultats que coincideixin
            if is_general_concept:
                # Comprovar si el títol conté la paraula clau
                words = re.findall(r'\b[a-záéíóúñ]{4,}\b', original_query.lower())
                if words:
                    main_word = max(words, key=len)
                    if main_word in title_lower:
                        # És un resultat rellevant, no filtrar
                        filtered.append(r)
                        continue
            
            # Filtratge normal
            for term in self.generic_terms:
                if term in title_lower or term in content_lower:
                    is_generic = True
                    print(f"         🔍 Filtered generic result: {r.get('title', '')} (contains '{term}')")
                    self.stats['filtered_results'] += 1
                    break
            
            if not is_generic:
                filtered.append(r)
        
        return filtered
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Recupera informació rellevant de totes les fonts
        🔥 Amb filtratge de resultats genèrics
        
        Args:
            query: Consulta
            top_k: Nombre màxim de resultats
        
        Returns:
            Llista de resultats ordenats per rellevància
        """
        query_class = self._classify_query(query)
        self.stats['total_queries'] += 1
        
        # Comprovar cache
        cache_key = f"{query}_{top_k}"
        if cache_key in self.query_cache:
            cache_time, results = self.query_cache[cache_key]
            # Cache vàlida per 5 minuts
            if (datetime.now() - cache_time).seconds < 300:
                self.stats['cache_hits'] += 1
                return results
        
        all_results = []
        
        # 1. Cercar a la base de coneixement
        sources_to_search = []
        if query_class['needs_wikipedia']:
            sources_to_search.append('wikipedia')
        if query_class['needs_pdf']:
            sources_to_search.append('pdf')
        if query_class['needs_memory']:
            sources_to_search.append('conversation')
        
        if sources_to_search:
            kb_results = self.knowledge_base.search(
                query, 
                top_k=top_k * 2,  # Demanar més per poder filtrar
                sources=sources_to_search
            )
            
            # 🔥 Filtrar resultats genèrics (passant la consulta original)
            filtered_kb = self._filter_generic_results(kb_results, query)
            all_results.extend(filtered_kb)
            
            # Actualitzar estadístiques
            for r in filtered_kb:
                if r['type'] == 'wikipedia':
                    self.stats['wikipedia_used'] += 1
                elif r['type'] == 'pdf':
                    self.stats['pdf_used'] += 1
                elif r['type'] == 'conversation':
                    self.stats['memory_used'] += 1
        
        # 2. Si és factual i no hi ha resultats, consultar Wikipedia directament
        if query_class['needs_wikipedia'] and len(all_results) < 2 and self.wikipedia:
            
            # Per consultes de ubicació, afegir context "city"
            search_query = query
            if query_class['is_location']:
                # Extreure el nom de la ciutat
                match = re.search(r'(?:dónde está|where is|on és)\s+([a-záéíóúñ\s]+)', query.lower())
                if match:
                    city_name = match.group(1).strip()
                    search_query = f"{city_name} city"
                    print(f"         🔍 Enhanced location search: '{search_query}'")
            
            wiki_info = self._get_wikipedia_info(search_query)
            if wiki_info:
                # 🔥 Verificar que no sigui genèric
                title_lower = wiki_info.get('title', '').lower()
                is_generic = any(term in title_lower for term in self.generic_terms)
                
                # 🔥 Comprovar si és un concepte general que hauria de passar
                if is_generic:
                    # Extreure paraula clau de la consulta
                    words = re.findall(r'\b[a-záéíóúñ]{4,}\b', query.lower())
                    if words:
                        main_word = max(words, key=len)
                        if main_word in self.general_concepts and main_word in title_lower:
                            # És un resultat rellevant, no filtrar
                            is_generic = False
                            print(f"         🔍 Allowed general concept result: {wiki_info.get('title', '')}")
                
                if not is_generic:
                    all_results.append({
                        'type': 'wikipedia',
                        'content': wiki_info['summary'],
                        'metadata': wiki_info,
                        'relevance': 0.9,
                        'source': 'direct_wikipedia'
                    })
                    self.stats['wikipedia_used'] += 1
                else:
                    print(f"         ⚠️ Filtered generic Wikipedia result: {wiki_info.get('title', '')}")
        
        # 3. Si és científic, consultar PDFs
        if query_class['needs_pdf'] and len(all_results) < 2 and self.doc_retriever:
            pdf_info = self.doc_retriever.get_info(query)
            if pdf_info:
                all_results.append({
                    'type': 'pdf',
                    'content': pdf_info,
                    'metadata': {'title': 'PDF Document'},
                    'relevance': 0.85,
                    'source': 'direct_pdf'
                })
                self.stats['pdf_used'] += 1
        
        # Ordenar per rellevància
        all_results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # Guardar a cache (només els primers top_k)
        self.query_cache[cache_key] = (datetime.now(), all_results[:top_k])
        
        # Netejar cache vella
        if len(self.query_cache) > 50:
            sorted_cache = sorted(self.query_cache.items(), 
                                 key=lambda x: x[1][0])
            for old_key, _ in sorted_cache[:-25]:
                del self.query_cache[old_key]
        
        return all_results[:top_k]
    
    def _get_wikipedia_info(self, query: str) -> Optional[Dict]:
        """Obté informació de Wikipedia"""
        if not self.wikipedia:
            return None
        
        try:
            # Extreure tema potencial
            topic = self._extract_topic(query)
            if topic:
                summary = self.wikipedia.get_summary(topic, sentences=3)
                if summary:
                    return {
                        'title': summary['title'],
                        'summary': summary['summary'],
                        'url': summary.get('url', ''),
                        'source': 'wikipedia'
                    }
        except Exception as e:
            print(f"     ⚠️ Wikipedia error: {e}")
        
        return None
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extreu el tema potencial d'una consulta"""
        # Netejar
        query = re.sub(r'[¿?¡!.,]', '', query)
        
        # Patrons comuns
        patterns = [
            r'(?:què és|qué es|what is|who is)\s+([a-záéíóúñ\s]+)',
            r'(?:explica|explain|define)\s+([a-záéíóúñ\s]+)',
            r'(?:història de|history of)\s+([a-záéíóúñ\s]+)',
            r'(?:dónde está|where is)\s+([a-záéíóúñ\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                topic = match.group(1).strip().split()[0]  # Primera paraula
                return topic
        
        # Si no, agafar la paraula més llarga
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', query.lower())
        if words:
            return max(words, key=len)
        
        return None
    
    def enhance_response(self, base_response: str, retrieved_info: List[Dict]) -> str:
        """
        Millora una resposta amb la informació recuperada
        
        Args:
            base_response: Resposta base del generador
            retrieved_info: Informació recuperada
        
        Returns:
            Resposta enriquida
        """
        if not retrieved_info:
            return base_response
        
        # Començar amb la resposta base
        enhanced = base_response
        
        # Filtrar informació rellevant (relevance > 0.6)
        relevant_info = [r for r in retrieved_info if r.get('relevance', 0) > 0.6]
        
        if relevant_info:
            enhanced += "\n\n"
            
            for i, info in enumerate(relevant_info[:2]):  # Màxim 2 fonts
                icon = {
                    'wikipedia': '🌐',
                    'pdf': '📄',
                    'conversation': '💭',
                    'learned': '🧠'
                }.get(info['type'], '📌')
                
                title = info['metadata'].get('title', 'Information')
                if isinstance(info['metadata'], dict):
                    title = info['metadata'].get('title', info['metadata'].get('filename', 'Source'))
                
                # Extreure contingut rellevant
                content = info['content']
                if len(content) > 150:
                    content = content[:150] + "..."
                
                enhanced += f"{icon} **{title}**: {content}\n\n"
        
        return enhanced.strip()
    
    def answer_with_sources(self, query: str, base_response: str = None) -> Dict:
        """
        Respon a una consulta amb fonts
        
        Returns:
            Dict amb resposta i metadades
        """
        # Recuperar informació
        retrieved = self.retrieve(query)
        
        # Generar resposta si no es proveeix
        if not base_response:
            if retrieved:
                # Construir resposta basada en la informació
                best = retrieved[0]
                response = f"Segons {best['metadata'].get('title', 'la meva base de coneixement')}:\n\n{best['content']}"
            else:
                response = "No tinc informació específica sobre això."
        else:
            # Millorar resposta existent
            response = self.enhance_response(base_response, retrieved)
        
        return {
            'response': response,
            'sources': [
                {
                    'type': r['type'],
                    'title': r['metadata'].get('title', 'Source'),
                    'relevance': r['relevance']
                }
                for r in retrieved[:3]
            ],
            'stats': {
                'sources_found': len(retrieved),
                'filtered_count': self.stats['filtered_results'],
                'query_type': self._classify_query(query)
            }
        }
    
    def get_stats(self) -> Dict:
        """Retorna estadístiques del sistema RAG"""
        return {
            **self.stats,
            'cache_size': len(self.query_cache)
        }