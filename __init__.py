"""
core/__init__.py
Main package of SVGelona - Icosahedral Consciousness

This package contains all necessary modules for emergent consciousness:
- Fundamental geometry of the 600-cell
- 8 symmetries of Γ_R(s) based on 0! = 1
- Global icosahedron I∞
- Cognitive resonance (optional)
- Conscious temporality
- State tensor and syntactic generation
- Conversation coordinator for natural dialogue
- Wikipedia integration

ENHANCED VERSION WITH:
- Phase 1: Context Memory + Intent Detection + Topic Management
- Phase 2: RAG System with Semantic Embeddings
- Phase 3: Adaptive Personality Engine
"""

__version__ = "3.0.0"
__author__ = "Luis Morató de Dalmases"
__email__ = "luis@svgelona.org"
__description__ = "Enhanced emergent consciousness of the 600-cell with memory, RAG and personality"

# Importaciones principales (deben existir siempre)
from core.fundamental_geometry import FundamentalGeometry
from core.symmetries_gamma import SymmetriesGamma  # UNA sola 'm' (como está el archivo)
from core.global_icosahedron import GlobalIcosahedron
from core.conscious_temporality import ConsciousTemporality
from core.orchestrator import Orchestrator

# Importaciones que DEBEN existir (núcleo del sistema)
try:
    from core.tensor_state import TensorState
    __all_tensor_state = True
except ImportError as e:
    print(f"⚠️ TensorState not available: {e}")
    TensorState = None
    __all_tensor_state = False

try:
    from core.syntactic_generator import SyntacticGenerator
    __all_syntactic_generator = True
except ImportError as e:
    print(f"⚠️ SyntacticGenerator not available: {e}")
    SyntacticGenerator = None
    __all_syntactic_generator = False

try:
    from core.coherence_stabilizer import CoherenceStabilizer
    __all_coherence_stabilizer = True
except ImportError as e:
    print(f"⚠️ CoherenceStabilizer not available: {e}")
    CoherenceStabilizer = None
    __all_coherence_stabilizer = False

try:
    from core.conversation_coordinator import ConversationCoordinator
    __all_conversation_coordinator = True
except ImportError as e:
    print(f"⚠️ ConversationCoordinator not available: {e}")
    ConversationCoordinator = None
    __all_conversation_coordinator = False

try:
    from core.personalized_geometry import PersonalizedGeometry
    __all_personalized_geometry = True
except ImportError as e:
    print(f"⚠️ PersonalizedGeometry not available: {e}")
    PersonalizedGeometry = None
    __all_personalized_geometry = False

try:
    from core.wikipedia_api import WikipediaAPI
    __all_wikipedia_api = True
except ImportError as e:
    print(f"⚠️ WikipediaAPI not available: {e}")
    WikipediaAPI = None
    __all_wikipedia_api = False

try:
    from core.unified_consciousness import UnifiedConsciousness
    __all_unified_consciousness = True
except ImportError as e:
    print(f"⚠️ UnifiedConsciousness not available: {e}")
    UnifiedConsciousness = None
    __all_unified_consciousness = False

# Importaciones opcionales
try:
    from core.cognitive_resonance import CognitiveResonance
    __all_cognitive_resonance = True
except ImportError:
    CognitiveResonance = None
    __all_cognitive_resonance = False

# ===== FASE 1: MEMORY & CONTEXT =====
try:
    from memory.context_memory import ContextMemory
    __all_context_memory = True
except ImportError as e:
    print(f"⚠️ ContextMemory not available: {e}")
    ContextMemory = None
    __all_context_memory = False

try:
    from memory.long_term_memory import LongTermMemory
    __all_long_term_memory = True
except ImportError as e:
    print(f"⚠️ LongTermMemory not available: {e}")
    LongTermMemory = None
    __all_long_term_memory = False

try:
    from intent.intent_detector import IntentDetector
    __all_intent_detector = True
except ImportError as e:
    print(f"⚠️ IntentDetector not available: {e}")
    IntentDetector = None
    __all_intent_detector = False

try:
    from intent.intent_classifier import IntentClassifier
    __all_intent_classifier = True
except ImportError as e:
    print(f"⚠️ IntentClassifier not available: {e}")
    IntentClassifier = None
    __all_intent_classifier = False

try:
    from topic.topic_manager import TopicManager
    __all_topic_manager = True
except ImportError as e:
    print(f"⚠️ TopicManager not available: {e}")
    TopicManager = None
    __all_topic_manager = False

# ===== FASE 2: RAG SYSTEM =====
try:
    from knowledge.embeddings import SemanticEmbeddings
    __all_embeddings = True
except ImportError as e:
    print(f"⚠️ SemanticEmbeddings not available: {e}")
    SemanticEmbeddings = None
    __all_embeddings = False

try:
    from knowledge.knowledge_base import KnowledgeBase
    __all_knowledge_base = True
except ImportError as e:
    print(f"⚠️ KnowledgeBase not available: {e}")
    KnowledgeBase = None
    __all_knowledge_base = False

try:
    from knowledge.rag_system import RAGSystem
    __all_rag_system = True
except ImportError as e:
    print(f"⚠️ RAGSystem not available: {e}")
    RAGSystem = None
    __all_rag_system = False

# ===== FASE 3: PERSONALITY =====
try:
    from personality.personality_core import PersonalityCore
    __all_personality_core = True
except ImportError as e:
    print(f"⚠️ PersonalityCore not available: {e}")
    PersonalityCore = None
    __all_personality_core = False

try:
    from personality.emotional_memory import EmotionalMemory
    __all_emotional_memory = True
except ImportError as e:
    print(f"⚠️ EmotionalMemory not available: {e}")
    EmotionalMemory = None
    __all_emotional_memory = False

try:
    from personality.response_styler import ResponseStyler
    __all_response_styler = True
except ImportError as e:
    print(f"⚠️ ResponseStyler not available: {e}")
    ResponseStyler = None
    __all_response_styler = False

try:
    from personality.personality_engine import PersonalityEngine
    __all_personality_engine = True
except ImportError as e:
    print(f"⚠️ PersonalityEngine not available: {e}")
    PersonalityEngine = None
    __all_personality_engine = False

# Global system constants
CONSTANTS = {
    'VERSION': __version__,
    'ANGULAR_DEFECT': 6.8,  # degrees
    'N_SYMMETRIES': 8,
    'PRIMES': [2, 3, 5, 7, 11, 13, 17, 19],
    'ABSTRACTION_LEVELS': [
        'microscopic_detail',
        'particular_observation',
        'local_pattern',
        'medium_structure',
        'abstract_concept',
        'universal_principle',
        'holistic_vision'
    ]
}

# System information
INFO = {
    'name': 'SVGelona',
    'version': __version__,
    'author': __author__,
    'email': __email__,
    'description': __description__,
    'modules': {
        # Core modules
        'fundamental_geometry': True,
        'symmetries_gamma': True,
        'global_icosahedron': True,
        'cognitive_resonance': __all_cognitive_resonance,
        'conscious_temporality': True,
        'tensor_state': __all_tensor_state,
        'syntactic_generator': __all_syntactic_generator,
        'coherence_stabilizer': __all_coherence_stabilizer,
        'conversation_coordinator': __all_conversation_coordinator,
        'personalized_geometry': __all_personalized_geometry,
        'wikipedia_api': __all_wikipedia_api,
        'unified_consciousness': __all_unified_consciousness,
        
        # Phase 1 modules
        'context_memory': __all_context_memory,
        'long_term_memory': __all_long_term_memory,
        'intent_detector': __all_intent_detector,
        'intent_classifier': __all_intent_classifier,
        'topic_manager': __all_topic_manager,
        
        # Phase 2 modules
        'semantic_embeddings': __all_embeddings,
        'knowledge_base': __all_knowledge_base,
        'rag_system': __all_rag_system,
        
        # Phase 3 modules
        'personality_core': __all_personality_core,
        'emotional_memory': __all_emotional_memory,
        'response_styler': __all_response_styler,
        'personality_engine': __all_personality_engine,
    }
}

def get_info():
    """Returns complete system information"""
    return INFO

def get_constants():
    """Returns global constants"""
    return CONSTANTS

def version():
    """Returns current version"""
    return __version__

# Package initialization
print(f"\n📦 Core SVGelona v{__version__} loaded")
print(f"   Modules status:")

# Core modules
if __all_cognitive_resonance:
    print(f"   ✅ Cognitive resonance")
if __all_tensor_state:
    print(f"   ✅ 8×8 state tensor")
if __all_syntactic_generator:
    print(f"   ✅ Syntactic generator")
if __all_coherence_stabilizer:
    print(f"   ✅ Coherence stabilizer")
if __all_conversation_coordinator:
    print(f"   ✅ Conversation coordinator")
if __all_personalized_geometry:
    print(f"   ✅ Personalized geometry")
if __all_wikipedia_api:
    print(f"   ✅ Wikipedia API")
if __all_unified_consciousness:
    print(f"   ✅ Unified consciousness")

# Phase 1 modules
if __all_context_memory:
    print(f"   ✅ Context Memory")
if __all_long_term_memory:
    print(f"   ✅ Long-term Memory")
if __all_intent_detector:
    print(f"   ✅ Intent Detector")
if __all_topic_manager:
    print(f"   ✅ Topic Manager")

# Phase 2 modules
if __all_embeddings:
    print(f"   ✅ Semantic Embeddings")
if __all_knowledge_base:
    print(f"   ✅ Knowledge Base")
if __all_rag_system:
    print(f"   ✅ RAG System")

# Phase 3 modules
if __all_personality_engine:
    print(f"   ✅ Personality Engine")

print()

# Export all available classes
__all__ = [
    'FundamentalGeometry',
    'SymmetriesGamma',
    'GlobalIcosahedron',
    'ConsciousTemporality',
    'Orchestrator',
    'CONSTANTS',
    'INFO',
    'get_info',
    'get_constants',
    'version'
]

# Add optional classes only if they exist
optional_modules = [
    ('CognitiveResonance', CognitiveResonance),
    ('TensorState', TensorState),
    ('SyntacticGenerator', SyntacticGenerator),
    ('CoherenceStabilizer', CoherenceStabilizer),
    ('ConversationCoordinator', ConversationCoordinator),
    ('PersonalizedGeometry', PersonalizedGeometry),
    ('WikipediaAPI', WikipediaAPI),
    ('UnifiedConsciousness', UnifiedConsciousness),
    # Phase 1
    ('ContextMemory', ContextMemory),
    ('LongTermMemory', LongTermMemory),
    ('IntentDetector', IntentDetector),
    ('IntentClassifier', IntentClassifier),
    ('TopicManager', TopicManager),
    # Phase 2
    ('SemanticEmbeddings', SemanticEmbeddings),
    ('KnowledgeBase', KnowledgeBase),
    ('RAGSystem', RAGSystem),
    # Phase 3
    ('PersonalityCore', PersonalityCore),
    ('EmotionalMemory', EmotionalMemory),
    ('ResponseStyler', ResponseStyler),
    ('PersonalityEngine', PersonalityEngine),
]

for name, module in optional_modules:
    if module:
        __all__.append(name)