"""
core/wikipedia_api.py
Module to query Wikipedia and get updated information

ENHANCED VERSION with:
- Better search with fallback strategies
- Multi-language support
- Improved error handling
- Smart topic extraction
- Response caching
- 🔥 Location-aware search (adds "city" context)
"""

import requests
import re
import time
from typing import Dict, List, Optional, Any
from urllib.parse import quote

class WikipediaAPI:
    """
    Client to query the Wikipedia API
    ENHANCED with better search and error handling
    """
    
    def __init__(self, lang: str = 'es'):
        self.lang = lang
        self.base_url = f"https://{lang}.wikipedia.org/api/rest_v1"
        self.search_url = f"https://{lang}.wikipedia.org/w/api.php"
        self.cache = {}
        self.search_cache = {}  # Separate cache for search results
        self.timeout = 15  # Increased timeout
        self.max_retries = 3
        self.user_agent = 'SVGelona/3.0 (Icosahedral Consciousness; mailto:luis@svgelona.org)'
        
        # 🔥 Paraules a evitar en resultats
        self.generic_terms = ['wally', 'waldo', 'dónde está wally', 'where is wally']
        
        print(f"   ✅ WikipediaAPI initialized (language: {lang})")
        print(f"      🔍 Search enabled | Cache: enabled | Timeout: {self.timeout}s")
    
    def _make_request(self, params: Dict, retry_count: int = 0) -> Optional[Dict]:
        """Makes a request to the API with retries and exponential backoff"""
        if retry_count >= self.max_retries:
            print(f"      ⚠️ Max retries reached for {params.get('titles', params.get('srsearch', 'unknown'))}")
            return None
        
        try:
            # Add common parameters
            params['format'] = 'json'
            params['utf8'] = 1
            
            response = requests.get(
                self.search_url, 
                params=params, 
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Too Many Requests
                wait_time = (2 ** retry_count)  # Exponential backoff
                print(f"      ⚠️ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                return self._make_request(params, retry_count + 1)
            else:
                print(f"      ⚠️ HTTP Error {response.status_code} for {params.get('titles', params.get('srsearch', 'unknown'))}")
                
        except requests.exceptions.Timeout:
            print(f"      ⚠️ Timeout for {params.get('titles', params.get('srsearch', 'unknown'))}")
        except requests.exceptions.ConnectionError:
            print(f"      ⚠️ Connection error")
        except Exception as e:
            print(f"      ⚠️ Request error: {e}")
        
        # Retry with backoff
        time.sleep(1 * (retry_count + 1))
        return self._make_request(params, retry_count + 1)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better search"""
        # Remove punctuation and extra spaces
        query = re.sub(r'[¿?¡!.,;:]', ' ', query)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remove common question words
        question_words = [
            'qué es', 'que es', 'what is', 'who is', 'quién es', 'qui és',
            'explica', 'explain', 'define', 'definición', 'definició',
            'significa', 'meaning', 'historia de', 'history of',
            'biografia de', 'biography of', 'teoria de', 'theory of',
            'dónde está', 'where is', 'on és', 'cómo funciona', 'how does'
        ]
        
        query_lower = query.lower()
        for word in question_words:
            if query_lower.startswith(word):
                query = query[len(word):].strip()
                break
        
        return query
    
    # 🔥 Funció per detectar si és una consulta de ubicació
    def _is_location_query(self, query: str) -> bool:
        """Detects if the query is asking for a location"""
        location_patterns = [
            r'dónde está', r'where is', r'on és', r'en donde', r'ubicación de'
        ]
        query_lower = query.lower()
        for pattern in location_patterns:
            if re.search(pattern, query_lower):
                return True
        return False
    
    # 🔥 Funció per extreure nom de ciutat
    def _extract_city_name(self, query: str) -> Optional[str]:
        """Extracts city name from location query"""
        patterns = [
            r'(?:dónde está|where is|on és|en donde)\s+([a-záéíóúñ\s]+)',
            r'ubicación de\s+([a-záéíóúñ\s]+)'
        ]
        query_lower = query.lower()
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1).strip()
        return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Searches for articles on Wikipedia related to the query
        Now with better normalization and fallback strategies
        """
        if not query or len(query) < 2:
            return []
        
        # 🔥 Detectar si és ubicació
        is_location = self._is_location_query(query)
        city_name = self._extract_city_name(query) if is_location else None
        
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        # 🔥 Per ubicacions, intentar amb "city" si és massa genèric
        search_queries = [normalized_query]
        if is_location and city_name and len(city_name.split()) == 1:
            # Afegir versió amb "city" per a ciutats poc conegudes
            search_queries.append(f"{city_name} city")
            print(f"      🔍 Also trying location-enhanced: '{city_name} city'")
        
        all_results = []
        
        for search_query in search_queries:
            # Check cache
            cache_key = f"search:{self.lang}:{search_query}"
            if cache_key in self.search_cache:
                cache_time, results = self.search_cache[cache_key]
                # Cache for 1 hour
                if time.time() - cache_time < 3600:
                    all_results.extend(results)
                    continue
            
            print(f"      🔍 Searching Wikipedia for: '{search_query}'")
            
            # Try exact search
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': limit,
                'srprop': 'snippet|titlesnippet|categorysnippet'
            }
            
            data = self._make_request(params)
            results = []
            
            if data and data.get('query', {}).get('search'):
                search_results = data['query']['search']
                
                for r in search_results:
                    # 🔥 Filtrar resultats genèrics
                    title_lower = r.get('title', '').lower()
                    if any(term in title_lower for term in self.generic_terms):
                        print(f"      ⚠️ Filtered generic result: {r.get('title')}")
                        continue
                    
                    results.append({
                        'title': r.get('title'),
                        'pageid': r.get('pageid'),
                        'snippet': self._clean_html(r.get('snippet', '')),
                        'wordcount': r.get('wordcount', 0),
                        'relevance': 1.0 if search_query == normalized_query else 0.8
                    })
                
                if results:
                    print(f"      ✅ Found {len(results)} results")
                    # Cache results
                    self.search_cache[cache_key] = (time.time(), results)
                    all_results.extend(results)
        
        # Si no hi ha resultats, intentar amb paraules individuals
        if not all_results:
            words = normalized_query.split()
            for word in words:
                if len(word) > 3:
                    print(f"      🔍 Trying alternative search for: '{word}'")
                    params['srsearch'] = word
                    data = self._make_request(params)
                    if data and data.get('query', {}).get('search'):
                        for r in data['query']['search'][:2]:  # Limit to 2 per word
                            # 🔥 Filtrar genèrics
                            title_lower = r.get('title', '').lower()
                            if any(term in title_lower for term in self.generic_terms):
                                continue
                            # Avoid duplicates
                            if not any(res['title'] == r.get('title') for res in all_results):
                                all_results.append({
                                    'title': r.get('title'),
                                    'pageid': r.get('pageid'),
                                    'snippet': self._clean_html(r.get('snippet', '')),
                                    'wordcount': r.get('wordcount', 0),
                                    'relevance': 0.7  # Lower relevance for partial matches
                                })
        
        # Clean cache (keep last 100)
        if len(self.search_cache) > 100:
            # Remove oldest entries
            sorted_cache = sorted(self.search_cache.items(), key=lambda x: x[1][0])
            for old_key, _ in sorted_cache[:-50]:
                del self.search_cache[old_key]
        
        return all_results
    
    def get_article(self, title: str) -> Optional[Dict]:
        """
        Gets the complete content of an article
        Now with better error handling and redirect following
        """
        if not title:
            return None
        
        # 🔥 Comprovar si és un títol genèric
        if any(term in title.lower() for term in self.generic_terms):
            print(f"      ⚠️ Skipping generic article: {title}")
            return None
        
        # Check cache
        cache_key = f"article:{self.lang}:{title}"
        if cache_key in self.cache:
            cache_time, article = self.cache[cache_key]
            # Cache for 24 hours
            if time.time() - cache_time < 86400:
                return article
        
        print(f"      📖 Fetching article: '{title}'")
        
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'extracts|info|pageimages',
            'exintro': False,
            'explaintext': True,
            'inprop': 'url|displaytitle',
            'pithumbsize': 300
        }
        
        data = self._make_request(params)
        if data:
            pages = data.get('query', {}).get('pages', {})
            
            for page_id, page_data in pages.items():
                if page_id != '-1':  # Valid page
                    article = {
                        'title': page_data.get('title'),
                        'display_title': page_data.get('displaytitle', page_data.get('title')),
                        'extract': page_data.get('extract', ''),
                        'pageid': page_data.get('pageid'),
                        'url': f"https://{self.lang}.wikipedia.org/wiki/{quote(page_data.get('title', '').replace(' ', '_'))}",
                        'length': len(page_data.get('extract', '')),
                        'thumbnail': page_data.get('thumbnail', {}).get('source') if 'thumbnail' in page_data else None
                    }
                    
                    # Cache article
                    self.cache[cache_key] = (time.time(), article)
                    return article
        
        return None
    
    def get_summary(self, query: str, sentences: int = 3, auto_lang: bool = True) -> Optional[Dict]:
        """
        Gets a summary of a topic
        Now with auto language detection and better fallback
        
        Args:
            query: Search query
            sentences: Number of sentences for summary
            auto_lang: Try to detect and switch language if no results
            
        Returns:
            Dict with title, summary, url, and source language
        """
        if not query or len(query) < 2:
            return None
        
        # 🔥 Detectar si és ubicació
        is_location = self._is_location_query(query)
        city_name = self._extract_city_name(query) if is_location else None
        
        # Normalize query
        normalized_query = self._normalize_query(query)
        
        # 🔥 Per ubicacions, provar diferents variants
        search_queries = [normalized_query]
        if is_location and city_name:
            search_queries.append(city_name)
            if len(city_name.split()) == 1:
                search_queries.append(f"{city_name} city")
        
        for search_query in search_queries:
            # Search for articles
            results = self.search(search_query, limit=3)
            
            # If no results and auto_lang is True, try English
            if not results and auto_lang and self.lang != 'en':
                print(f"      🔄 No results in {self.lang}, trying English...")
                original_lang = self.lang
                self.lang = 'en'
                self.search_url = f"https://en.wikipedia.org/w/api.php"
                results = self.search(search_query, limit=3)
                self.lang = original_lang
                self.search_url = f"https://{original_lang}.wikipedia.org/w/api.php"
            
            if results:
                # Get the best result (highest relevance or wordcount)
                best_result = max(results, key=lambda x: (x.get('relevance', 0), x.get('wordcount', 0)))
                
                # Get the article
                article = self.get_article(best_result['title'])
                
                if article and article.get('extract'):
                    # Extract summary
                    extract = article['extract']
                    
                    # Clean extract (remove references, etc.)
                    extract = re.sub(r'\[\d+\]', '', extract)  # Remove reference numbers
                    extract = re.sub(r'\s+', ' ', extract).strip()
                    
                    # Split into sentences
                    sentences_list = re.split(r'(?<=[.!?])\s+', extract)
                    
                    if len(sentences_list) <= sentences:
                        summary = extract
                    else:
                        summary = ' '.join(sentences_list[:sentences]) + '...'
                    
                    return {
                        'title': article['title'],
                        'display_title': article.get('display_title', article['title']),
                        'summary': summary,
                        'full_extract': extract[:500] + '...' if len(extract) > 500 else extract,
                        'url': article['url'],
                        'length': article['length'],
                        'source_lang': self.lang,
                        'thumbnail': article.get('thumbnail')
                    }
        
        return None
    
    def get_summary_simple(self, query: str) -> str:
        """
        Simplified method to get just the summary text
        Perfect for quick responses
        """
        summary = self.get_summary(query, sentences=2)
        if summary:
            return f"🌐 **{summary['display_title']}**\n\n{summary['summary']}"
        
        # If no exact summary, try search results
        results = self.search(query, limit=3)
        if results:
            response = f"🔍 He trobat aquests resultats relacionats:\n\n"
            for i, r in enumerate(results[:3], 1):
                response += f"{i}. **{r['title']}**\n"
                if r.get('snippet'):
                    # Clean snippet
                    snippet = self._clean_html(r['snippet'])
                    snippet = re.sub(r'\s+', ' ', snippet).strip()
                    response += f"   {snippet[:150]}...\n"
                response += "\n"
            return response
        
        return f"❌ No he trobat informació sobre '{query}'."
    
    def query_topic(self, topic: str) -> str:
        """
        Legacy method for backward compatibility
        """
        return self.get_summary_simple(topic)
    
    def get_random_article(self) -> Optional[Dict]:
        """Get a random Wikipedia article"""
        params = {
            'action': 'query',
            'list': 'random',
            'rnlimit': 1,
            'rnnamespace': 0  # Main namespace only
        }
        
        data = self._make_request(params)
        if data and data.get('query', {}).get('random'):
            random_title = data['query']['random'][0]['title']
            return self.get_summary(random_title, sentences=2)
        
        return None
    
    def get_wikipedia_languages(self) -> List[str]:
        """Get list of available Wikipedia languages"""
        # Most common languages
        return ['ca', 'es', 'en', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ar']
    
    def set_language(self, lang: str):
        """Change Wikipedia language"""
        if lang != self.lang:
            self.lang = lang
            self.search_url = f"https://{lang}.wikipedia.org/w/api.php"
            print(f"      🔄 Wikipedia language changed to: {lang}")
            # Clear caches when changing language
            self.cache.clear()
            self.search_cache.clear()
    
    def _clean_html(self, text: str) -> str:
        """Cleans HTML tags from snippets"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        html_entities = {
            '&quot;': '"',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&nbsp;': ' ',
            '&#39;': "'",
            '&apos;': "'",
            '&hellip;': '...',
            '&mdash;': '—',
            '&ndash;': '–'
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'article_cache_size': len(self.cache),
            'search_cache_size': len(self.search_cache),
            'total_cache_entries': len(self.cache) + len(self.search_cache),
            'language': self.lang
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self.cache.clear()
        self.search_cache.clear()
        print("      🧹 Wikipedia cache cleared")