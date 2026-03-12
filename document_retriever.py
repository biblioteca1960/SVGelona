"""
core/document_retriever.py
Retrieves information from PDF documents with improved relevance filtering
VERSIÓ COMPLETA I CORREGIDA
"""

import os
import re
from typing import Dict, List, Optional
import PyPDF2

class DocumentRetriever:
    """
    Searches and retrieves information from PDF documents
    Now with relevance filtering to avoid irrelevant matches
    """
    
    # Palabras que identifican cada PDF (para evitar falsos positivos)
    PDF_TOPICS = {
        'I.3. Annex2 Spin-Correlation-Derivation_(QSVG)': {
            'keywords': ['spin', 'qsvg', 'correlación', 'partícula', 'quark', 'rhics', 'hadron', 'fase geométrica'],
            'topic': 'física de partículas y QSVG',
            'skip_for_general': True
        },
        '01_Main_Proof_Riemann_Hypothesis': {
            'keywords': ['riemann', 'zeta', 'ceros', 'zeros', 'hipótesis', 'hypothesis', 'primos', 'primes'],
            'topic': 'hipótesis de Riemann',
            'skip_for_general': True
        },
        '600_cell': {
            'keywords': ['600-cell', 'polychoron', 'geometry', 'geometría', 'vertices', 'edges'],
            'topic': 'geometría del 600-cell',
            'skip_for_general': False
        },
        'angular_defect': {
            'keywords': ['defecto angular', 'angular defect', '6.8°', '6.8 grados'],
            'topic': 'defecto angular',
            'skip_for_general': False
        },
        'symmetries_gamma': {
            'keywords': ['simetrías', 'symmetries', 'gamma function', 'función gamma', 'Γ_R'],
            'topic': 'simetrías de la función gamma',
            'skip_for_general': False
        }
    }
    
    def __init__(self, documents_path: str = "documents"):
        """
        Inicialitza el recuperador de documents
        
        Args:
            documents_path: Ruta a la carpeta de documents PDF
        """
        self.documents_path = documents_path  # 🔥 CORREGIT: guardar com a atribut
        self.documents = {}
        self.index = {}
        self.document_summaries = {}
        self.document_topics = {}  # Mapejar documents als seus temes
        
        print(f"   📚 Initializing DocumentRetriever from '{documents_path}'")
        self._load_documents()
    
    def _load_documents(self):
        """Load all PDF documents from the folder"""
        if not os.path.exists(self.documents_path):
            print(f"   ⚠️ Documents folder '{self.documents_path}' not found, creating...")
            os.makedirs(self.documents_path, exist_ok=True)
            print(f"   ℹ️ Please add your PDF files to '{self.documents_path}'")
            return
        
        pdf_files = [f for f in os.listdir(self.documents_path) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"   ⚠️ No PDF files found in '{self.documents_path}'")
            return
        
        print(f"   📊 Found {len(pdf_files)} PDF files")
        
        for filename in pdf_files:
            filepath = os.path.join(self.documents_path, filename)
            try:
                print(f"   📄 Loading {filename}...")
                content = self._extract_text_from_pdf(filepath)
                
                if not content or len(content) < 100:
                    print(f"   ⚠️ {filename} has little or no extractable text")
                    continue
                
                # Identificar el tema del PDF
                doc_topic = self._identify_pdf_topic(filename, content)
                
                # Store document
                doc_name = filename.replace('.pdf', '')
                self.documents[doc_name] = {
                    'filename': filename,
                    'content': content,
                    'title': self._extract_title(content, doc_name),
                    'path': filepath,
                    'size': len(content),
                    'topic': doc_topic,
                    'skip_for_general': self._should_skip_for_general(filename)
                }
                
                # Create document summary
                self.document_summaries[doc_name] = self._create_summary(content)
                
                # Index keywords (solo palabras relevantes)
                self._index_document(doc_name, content)
                print(f"   ✅ Loaded {filename} ({len(content)} chars) - Tema: {doc_topic}")
                
            except Exception as e:
                print(f"   ⚠️ Error loading {filename}: {e}")
        
        print(f"   ✅ Loaded {len(self.documents)} PDF documents")
    
    def _identify_pdf_topic(self, filename: str, content: str) -> str:
        """Identify the topic of a PDF based on filename and content"""
        # Check by filename first
        for pdf_name, info in self.PDF_TOPICS.items():
            if pdf_name.lower() in filename.lower():
                return info['topic']
        
        # Check content for keywords
        content_lower = content.lower()
        for pdf_name, info in self.PDF_TOPICS.items():
            for keyword in info['keywords']:
                if keyword.lower() in content_lower:
                    return info['topic']
        
        return "general"
    
    def _should_skip_for_general(self, filename: str) -> bool:
        """Check if this PDF should be skipped for general questions"""
        for pdf_name, info in self.PDF_TOPICS.items():
            if pdf_name.lower() in filename.lower() and info.get('skip_for_general', False):
                return True
        return False
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                print(f"      📖 Reading {len(reader.pages)} pages...")
                
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"   ⚠️ PyPDF2 error: {e}")
        
        return text
    
    def _extract_title(self, content: str, default: str) -> str:
        """Extract title from document content"""
        lines = content.split('\n')
        for line in lines[:20]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('http'):
                # Remove page numbers
                line = re.sub(r'[0-9]+$', '', line)
                return line.strip()
        return default.replace('_', ' ').title()
    
    def _create_summary(self, content: str, max_sentences: int = 3) -> str:
        """Create a summary of the document"""
        sentences = re.split(r'(?<=[.!?])\s+', content[:3000])
        important_sentences = []
        
        for sentence in sentences[:15]:
            sentence = sentence.strip()
            if len(sentence) > 50 and not sentence.startswith('['):
                important_sentences.append(sentence)
            if len(important_sentences) >= max_sentences:
                break
        
        return ' '.join(important_sentences)
    
    def _index_document(self, doc_name: str, content: str):
        """Create keyword index for the document"""
        # Extraer palabras significativas (5+ letras)
        words = re.findall(r'\b[a-zA-Z]{5,}\b', content.lower())
        
        # Palabras a ignorar (comunes en español/catalán)
        stop_words = {
            'aquest', 'aquesta', 'això', 'sobre', 'entre', 'durant', 'després',
            'abans', 'sempre', 'mai', 'quan', 'on', 'com', 'però', 'sino',
            'porque', 'porqué', 'donde', 'como', 'cuando', 'siempre', 'nunca',
            'this', 'that', 'these', 'those', 'with', 'from', 'have', 'will',
            'sobre', 'entre', 'durante', 'después', 'antes', 'para', 'por',
            'pero', 'mas', 'sin', 'con', 'han', 'has', 'hay', 'era', 'fue'
        }
        
        for word in set(words):
            if word not in stop_words and len(word) > 3:
                if word not in self.index:
                    self.index[word] = []
                if doc_name not in self.index[word]:
                    self.index[word].append(doc_name)
    
    def is_general_query(self, query: str) -> bool:
        """Check if query is about general/common topics"""
        q = query.lower()
        
        # Temas generales que deberían ir a Wikipedia
        general_topics = [
            'montaña', 'montaña', 'mountain',
            'caballo', 'horse', 'caball',
            'gato', 'cat',
            'perro', 'dog',
            'pez', 'fish',
            'trucha', 'trout',
            'salmón', 'salmon',
            'árbol', 'tree',
            'flor', 'flower',
            'río', 'river',
            'mar', 'sea',
            'océano', 'ocean',
            'cama', 'bed',
            'mesa', 'table',
            'silla', 'chair'
        ]
        
        return any(topic in q for topic in general_topics)
    
    def search(self, query: str, max_results: int = 2) -> List[Dict]:
        """
        Search documents for relevant information
        Now with filtering to avoid irrelevant matches
        """
        q = query.lower()
        words = re.findall(r'\b[a-zA-Z]{4,}\b', q)
        
        if not words:
            return []
        
        # Check if this is a general query
        is_general = self.is_general_query(q)
        
        # Score documents
        scores = {}
        for word in words:
            if word in self.index:
                for doc_name in self.index[word]:
                    # Skip specialized PDFs for general queries
                    if is_general and self.documents.get(doc_name, {}).get('skip_for_general', False):
                        continue
                    scores[doc_name] = scores.get(doc_name, 0) + 1
        
        # Boost score if document topic matches query
        for doc_name, doc in self.documents.items():
            # Skip specialized PDFs for general queries
            if is_general and doc.get('skip_for_general', False):
                continue
                
            # Check if document topic appears in query
            topic = doc.get('topic', '').lower()
            if topic and any(word in topic for word in words):
                scores[doc_name] = scores.get(doc_name, 0) + 5
        
        # Sort by relevance
        relevant_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_name, score in relevant_docs[:max_results]:
            if doc_name in self.documents:
                doc = self.documents[doc_name]
                
                # Extract relevant paragraph
                excerpt = self._extract_relevant_paragraph(doc['content'], words)
                
                if excerpt:  # Only include if we found relevant content
                    results.append({
                        'title': doc['title'],
                        'filename': doc['filename'],
                        'excerpt': excerpt,
                        'relevance': score,
                        'topic': doc.get('topic', 'general'),
                        'source': 'pdf'
                    })
        
        return results
    
    def _extract_relevant_paragraph(self, content: str, keywords: List[str]) -> Optional[str]:
        """Extract the most relevant paragraph based on keywords"""
        paragraphs = re.split(r'\n\s*\n', content)
        
        best_paragraph = None
        best_score = -1
        
        for para in paragraphs:
            if len(para) < 100 or len(para) > 2000:
                continue
            
            para_lower = para.lower()
            score = sum(para_lower.count(keyword) for keyword in keywords)
            
            # Boost if paragraph contains multiple keywords together
            for i, kw1 in enumerate(keywords):
                for kw2 in keywords[i+1:]:
                    if kw1 in para_lower and kw2 in para_lower:
                        score += 2
            
            if score > best_score:
                best_score = score
                best_paragraph = para
        
        if best_paragraph and best_score > 2:  # Minimum relevance threshold
            # Clean up
            best_paragraph = re.sub(r'\s+', ' ', best_paragraph)
            best_paragraph = re.sub(r'\[[0-9]+\]', '', best_paragraph)
            best_paragraph = best_paragraph.strip()
            
            if len(best_paragraph) > 800:
                best_paragraph = best_paragraph[:800] + "..."
            
            return best_paragraph
        
        return None  # No relevant paragraph found
    
    def get_info(self, query: str) -> Optional[str]:
        """
        Main method to get information from documents
        Returns None if no relevant information found
        """
        # Check if this is a general query
        if self.is_general_query(query):
            return None  # Let Wikipedia handle it
        
        # Search for relevant documents
        results = self.search(query)
        
        if results:
            best = results[0]
            return f"📖 **{best['title']}** (PDF: {best['filename']}):\n\n{best['excerpt']}"
        
        return None
    
    def list_documents(self) -> List[str]:
        """List all available documents with topics"""
        docs = []
        for doc_name, doc in self.documents.items():
            topic = doc.get('topic', 'general')
            summary = self.document_summaries.get(doc_name, '')[:80] + '...' if self.document_summaries.get(doc_name) else ''
            docs.append(f"📄 {doc['title']} - Tema: {topic}\n   {summary}")
        return docs
    
    def get_stats(self) -> Dict:
        """Get statistics about loaded documents"""
        return {
            'total_documents': len(self.documents),
            'by_topic': {},
            'total_pages': sum(len(doc.get('content', '')) // 2000 for doc in self.documents.values())  # Aproximació
        }