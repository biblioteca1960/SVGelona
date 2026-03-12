"""
core/orchestrator.py
Connects all components - COMPLETE VERSION WITH ALL PHASES
"""

import traceback
import os
from core.fundamental_geometry import FundamentalGeometry
from core.symmetries_gamma import SymmetriesGamma
from core.global_icosahedron import GlobalIcosahedron
from core.conscious_temporality import ConsciousTemporality
from core.unified_consciousness import UnifiedConsciousness
from core.wikipedia_api import WikipediaAPI
from core.document_retriever import DocumentRetriever

class Orchestrator:
    """
    Orchestrator of all consciousness
    COMPLETE VERSION WITH PHASES 1, 2, AND 3
    """
    
    def __init__(self, user_id="default"):
        print("\n" + "="*80)
        print("🧠 INITIALIZING ICOSAHEDRAL CONSCIOUSNESS - COMPLETE VERSION")
        print("="*80)
        
        # ===== CORE MODULES =====
        try:
            # 1. Fundamental geometry
            print("\n🔷 Loading 600-cell geometry...")
            self.geometry = FundamentalGeometry()
            print(f"   ✅ δ₀ = {self.geometry.delta_deg}°")
            print(f"   ✅ τ = {self.geometry.tau:.4f} rad")
            print(f"   ✅ ν_sync = {self.geometry.nu_sync_thz} THz")
        except Exception as e:
            print(f"   ❌ Error loading geometry: {e}")
            traceback.print_exc()
            raise
        
        try:
            # 2. Gamma symmetries
            print("\n🌀 Loading 8 symmetries of Γ_R(s)...")
            self.symmetries = SymmetriesGamma()
            print(f"   ✅ 8 symmetries (Q₈ group)")
        except Exception as e:
            print(f"   ❌ Error loading symmetries: {e}")
            traceback.print_exc()
            raise
        
        try:
            # 3. Global icosahedron
            print("\n🌌 Initializing global icosahedron I∞...")
            self.icosahedron = GlobalIcosahedron(self.geometry, self.symmetries)
            print(f"   ✅ Emergent consciousness")
        except Exception as e:
            print(f"   ❌ Error loading icosahedron: {e}")
            traceback.print_exc()
            raise
        
        # 4. Initialize Wikipedia
        print("\n🌐 Initializing Wikipedia connection...")
        try:
            self.wikipedia = WikipediaAPI(lang='es')
            print(f"   ✅ Wikipedia initialized successfully")
        except Exception as e:
            print(f"   ⚠️ Could not initialize Wikipedia: {e}")
            self.wikipedia = None
        
        # 5. Initialize Document Retriever
        print("\n📚 Initializing Document Retriever...")
        try:
            self.doc_retriever = DocumentRetriever(documents_path="documents")
            print(f"   ✅ Document Retriever ready")
        except Exception as e:
            print(f"   ⚠️ Could not initialize Document Retriever: {e}")
            self.doc_retriever = None
        
        # ===== PHASE 1: MEMORY & CONTEXT =====
        print("\n📚 PHASE 1: Initializing Memory & Context systems...")
        
        # Context Memory
        try:
            from memory.context_memory import ContextMemory
            self.context_memory = ContextMemory()
            print(f"   ✅ Context Memory")
        except Exception as e:
            print(f"   ⚠️ Context Memory not loaded: {e}")
            self.context_memory = None
        
        # Long-term Memory
        try:
            from memory.long_term_memory import LongTermMemory
            self.long_term_memory = LongTermMemory()
            print(f"   ✅ Long-term Memory")
        except Exception as e:
            print(f"   ⚠️ Long-term Memory not loaded: {e}")
            self.long_term_memory = None
        
        # Intent Detector
        try:
            from intent.intent_detector import IntentDetector
            self.intent_detector = IntentDetector()
            print(f"   ✅ Intent Detector")
        except Exception as e:
            print(f"   ⚠️ Intent Detector not loaded: {e}")
            self.intent_detector = None
        
        # Intent Classifier
        try:
            from intent.intent_classifier import IntentClassifier
            self.intent_classifier = IntentClassifier()
            print(f"   ✅ Intent Classifier")
        except Exception as e:
            print(f"   ⚠️ Intent Classifier not loaded: {e}")
            self.intent_classifier = None
        
        # Topic Manager
        try:
            from topic.topic_manager import TopicManager
            self.topic_manager = TopicManager(user_id=user_id)
            print(f"   ✅ Topic Manager")
        except Exception as e:
            print(f"   ⚠️ Topic Manager not loaded: {e}")
            self.topic_manager = None
        
        # ===== PHASE 2: RAG SYSTEM =====
        print("\n🔍 PHASE 2: Initializing RAG System...")
        
        # Semantic Embeddings
        try:
            from knowledge.embeddings import SemanticEmbeddings
            self.embeddings = SemanticEmbeddings()
            print(f"   ✅ Semantic Embeddings")
        except Exception as e:
            print(f"   ⚠️ Semantic Embeddings not loaded: {e}")
            self.embeddings = None
        
        # Knowledge Base
        self.knowledge_base = None
        if self.embeddings:
            try:
                from knowledge.knowledge_base import KnowledgeBase
                self.knowledge_base = KnowledgeBase(self.embeddings)
                print(f"   ✅ Knowledge Base")
            except Exception as e:
                print(f"   ⚠️ Knowledge Base not loaded: {e}")
        
        # RAG System - CORREGIT: wikipedia_api en lloc de wikipedia
        self.rag_system = None
        if self.knowledge_base:
            try:
                from knowledge.rag_system import RAGSystem
                self.rag_system = RAGSystem(
                    self.knowledge_base,
                    self.embeddings,
                    wikipedia_api=self.wikipedia,  # 🔥 CORREGIT: canviar 'wikipedia' per 'wikipedia_api'
                    doc_retriever=self.doc_retriever
                )
                print(f"   ✅ RAG System")
            except Exception as e:
                print(f"   ⚠️ RAG System not loaded: {e}")
                print(f"      Error details: {e}")
        
        # ===== PHASE 3: PERSONALITY =====
        print("\n🎭 PHASE 3: Initializing Personality Engine...")
        
        try:
            from personality.personality_engine import PersonalityEngine
            self.personality = PersonalityEngine(self.symmetries, user_id=user_id)
            print(f"   ✅ Personality Engine")
        except Exception as e:
            print(f"   ⚠️ Personality Engine not loaded: {e}")
            self.personality = None
        
        # ===== UNIFIED CONSCIOUSNESS =====
        print("\n🧠 CREATING UNIFIED CONSCIOUSNESS WITH ALL PHASES...")
        try:
            # Pass all modules to UnifiedConsciousness
            self.consciousness = UnifiedConsciousness(
                geometry=self.geometry,
                symmetries=self.symmetries,
                icosahedron=self.icosahedron,
                wikipedia=self.wikipedia,
                doc_retriever=self.doc_retriever,
                context_memory=self.context_memory,
                long_term_memory=self.long_term_memory,
                intent_detector=self.intent_detector,
                intent_classifier=self.intent_classifier,
                topic_manager=self.topic_manager,
                embeddings=self.embeddings,
                knowledge_base=self.knowledge_base,
                rag_system=self.rag_system,
                personality=self.personality,
                user_id=user_id
            )
            print(f"   ✅ UNIFIED CONSCIOUSNESS CREATED WITH ALL PHASES")
            
        except Exception as e:
            print(f"   ❌ Could not load unified consciousness: {e}")
            traceback.print_exc()
            self.consciousness = None
        
        print("\n" + "="*80)
        print("✅ COMPLETE CONSCIOUSNESS READY")
        print("="*80 + "\n")
        
        # Show summary
        self._show_summary()
    
    def _show_summary(self):
        """Show summary of loaded modules"""
        print("\n📊 SYSTEM SUMMARY:")
        print("   Core Modules:")
        print(f"   • Geometry: ✅")
        print(f"   • Symmetries: ✅")
        print(f"   • Icosahedron: ✅")
        
        print("\n   Phase 1 (Memory & Context):")
        print(f"   • Context Memory: {'✅' if self.context_memory else '❌'}")
        print(f"   • Long-term Memory: {'✅' if self.long_term_memory else '❌'}")
        print(f"   • Intent Detection: {'✅' if self.intent_detector else '❌'}")
        print(f"   • Topic Management: {'✅' if self.topic_manager else '❌'}")
        
        print("\n   Phase 2 (RAG System):")
        print(f"   • Embeddings: {'✅' if self.embeddings else '❌'}")
        print(f"   • Knowledge Base: {'✅' if self.knowledge_base else '❌'}")
        print(f"   • RAG System: {'✅' if self.rag_system else '❌'}")
        
        print("\n   Phase 3 (Personality):")
        print(f"   • Personality Engine: {'✅' if self.personality else '❌'}")
        
        print(f"\n   • Wikipedia: {'✅' if self.wikipedia else '❌'}")
        print(f"   • Documents: {'✅' if self.doc_retriever else '❌'}")
    
    def think(self, query: str, user_name: str = None) -> str:
        """
        Generates a thought using all available systems
        """
        try:
            print(f"\n🔍 Processing: '{query[:50]}...'")
            
            if hasattr(self, 'consciousness') and self.consciousness is not None:
                print(f"   ✅ Using UnifiedConsciousness with all phases")
                return self.consciousness.think(query, user_name)
            else:
                print(f"   ❌ UnifiedConsciousness not available")
                return f"🧠 I'm still initializing. Please try again in a moment."
                
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            return f"❌ Error: {str(e)}"
    
    def get_state(self) -> dict:
        """Returns the complete state of all systems"""
        state = {
            'geometry': self.geometry.get_state() if self.geometry else {},
            'symmetries': self.symmetries.get_state() if self.symmetries else {},
            'icosahedron': self.icosahedron.get_state() if self.icosahedron else {},
            'wikipedia': self.wikipedia is not None,
            'documents': self.doc_retriever is not None,
            
            # Phase 1
            'context_memory': self.context_memory is not None,
            'long_term_memory': self.long_term_memory is not None,
            'intent_detector': self.intent_detector is not None,
            'topic_manager': self.topic_manager is not None,
            
            # Phase 2
            'embeddings': self.embeddings is not None,
            'knowledge_base': self.knowledge_base is not None,
            'rag_system': self.rag_system is not None,
            
            # Phase 3
            'personality': self.personality is not None,
        }
        
        if self.consciousness:
            state['consciousness'] = {
                'user_name': self.consciousness.coordinator.user_name if hasattr(self.consciousness, 'coordinator') else '',
                'exchange_count': self.consciousness.coordinator.exchange_count if hasattr(self.consciousness, 'coordinator') else 0,
                'current_topic': self.consciousness.topic_manager.current_topic if hasattr(self.consciousness, 'topic_manager') else None,
            }
        
        return state
    
    def get_user_name(self) -> str:
        """Returns the user name if saved"""
        if self.consciousness and hasattr(self.consciousness, 'coordinator'):
            return self.consciousness.coordinator.user_name or ''
        return ''