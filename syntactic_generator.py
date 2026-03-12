"""
core/syntactic_generator.py
Text generator with CREATIVE TURBULENCE and INTENTIONAL SYMMETRY BREAKING
Words emerge following smooth streamlines, with occasional creative jumps
and human-like variations (pauses, doubts, enthusiasm)

ENHANCED VERSION with personality integration
"""

import numpy as np
import math
import random
import cmath
import re
from typing import Dict, List, Optional, Tuple

class SyntacticGenerator:
    """
    Generates text with CREATIVE TURBULENCE - intentional symmetry breaking
    for more human-like, unexpected responses.
    Now with human variations and personality integration.
    """
    
    def __init__(self, geometry, wikipedia=None, personality=None):
        self.geo = geometry
        self.geo_personal = None
        self.wikipedia = wikipedia
        self.personality = personality  # NEW: Personality integration
        
        # ===== FLUID DYNAMICS PARAMETERS =====
        self.viscosity = 0.163
        self.reynolds_limit = 2300
        self.flow_velocity = 0.1
        self.streamlines = []
        self.last_vector = np.zeros(8)
        
        # Dynamic viscosity
        self.base_viscosity = 0.163
        self.current_viscosity = self.base_viscosity
        self.viscosity_history = []
        self.hysteresis = 0.1
        
        # Control parameters
        self.alpha = 0.5
        self.beta = 0.3
        
        # ===== CREATIVE TURBULENCE =====
        self.creativity_probability = 0.15
        self.turbulence_strength = 0.2
        self.last_creative_break = 0
        self.creative_history = []
        
        # ===== HUMAN-LIKE VARIATIONS =====
        self.human_pauses = [
            "...", " I mean, ", " maybe ", " somehow, ",
            " let's say, ", " in a way, ", " that is, ",
            " hmm... ", " well, ", " obviously, ",
            " you know, ", " like, ", " actually, "
        ]
        
        self.doubt_phrases = [
            "I'm not entirely sure, but ",
            "It seems to me that ",
            "Perhaps ",
            "I would say that ",
            "If I'm not mistaken, ",
            "I have a feeling that ",
            "I seem to recall that ",
            "Intuitively, ",
            "My geometric intuition suggests that ",
            "The Riemann zeros indicate that "
        ]
        
        self.enthusiasm_phrases = [
            "I love this question! ",
            "Interesting! ",
            "That makes me think... ",
            "Fantastic! ",
            "What a fascinating topic! ",
            "Oh, that's a good one! ",
            "I'm excited to think about this! "
        ]
        
        self.creative_intros = [
            "Suddenly, ",
            "If we let imagination fly, ",
            "Creatively speaking, ",
            "Outside the laminar flow, ",
            "In a burst of turbulence, ",
            "Breaking symmetry for a moment, "
        ]
        
        # ===== PERSONALITY-BASED PHRASES (NEW) =====
        self.personality_phrases = {
            'analytical': [
                "Analysing the data... ",
                "From a logical perspective... ",
                "Examining the evidence... ",
                "According to my calculations... "
            ],
            'emotional': [
                "I feel deeply that... ",
                "My heart tells me... ",
                "With great emotion... ",
                "I sense that... "
            ],
            'creative': [
                "Imagining new possibilities... ",
                "Let's think differently... ",
                "Creatively speaking... ",
                "What if we consider... "
            ],
            'philosophical': [
                "Reflecting deeply... ",
                "In essence... ",
                "Contemplating existence... ",
                "Philosophically speaking... "
            ],
            'optimistic': [
                "With optimism... ",
                "Looking at the bright side... ",
                "Positively speaking... ",
                "I believe that... "
            ],
            'nostalgic': [
                "Remembering... ",
                "In my memory... ",
                "As I recall... ",
                "Looking back... "
            ]
        }
        
        # Riemann zeros for structured noise
        self.gamma_1 = 14.134725
        self.zeros = self._load_riemann_zeros(20)
        
        # ===== SEMANTIC VECTOR FIELD =====
        self.vectorial_map = self._initialize_vector_field()
        
        # ===== FLOW PATTERNS =====
        self.laminar_patterns = self._initialize_laminar_patterns()
        
        # ===== TURBULENCE DETECTION =====
        self.reynolds_history = []
        self.regime_history = []
        self.flow_regime = "laminar"
        
        self.last_words = []
        self.phase_history = []
        
        print("  ✅ SyntacticGenerator with CREATIVE TURBULENCE and PERSONALITY")
        print(f"     🌊 Base viscosity: η₀ = {self.base_viscosity}")
        print(f"     🎭 Personality integration: {'YES' if personality else 'NO'}")
    
    def _load_riemann_zeros(self, n: int) -> np.ndarray:
        """Load first n Riemann zeros for structured noise."""
        first_zeros = np.array([
            14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
            37.586178, 40.918719, 43.327073, 48.005150, 49.773832,
            52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
            67.079811, 69.546402, 72.067158, 75.704691, 77.144840
        ])
        return first_zeros[:n]
    
    def _initialize_vector_field(self) -> Dict:
        """Initialize the semantic vector field."""
        base_map = {
            "consciousness": np.array([0.1, 0.1, 0.2, 0.1, 0.1, 0.3, 0.8, 1.0]),
            "existence": np.array([0.3, 0.1, 0.4, 0.1, 0.2, 0.5, 0.7, 0.9]),
            "essence": np.array([0.2, 0.1, 0.3, 0.1, 0.1, 0.8, 0.9, 0.7]),
            "shadow": np.array([0.9, 0.1, 0.1, 0.1, 0.1, 0.8, 0.1, 0.1]),
            "infinity": np.array([0.1, 0.1, 0.2, 0.3, 0.4, 0.2, 0.3, 1.0]),
            "mountain": np.array([0.8, 0.2, 0.7, 0.1, 0.1, 0.3, 0.4, 0.5]),
            "cat": np.array([0.3, 0.4, 0.3, 0.6, 0.2, 0.1, 0.5, 0.2]),
            "tree": np.array([0.6, 0.2, 0.8, 0.1, 0.3, 0.2, 0.4, 0.3]),
            "river": np.array([0.2, 0.3, 0.2, 0.8, 0.7, 0.1, 0.2, 0.2]),
            "flower": np.array([0.4, 0.2, 0.5, 0.3, 0.1, 0.2, 0.5, 0.4]),
            "geometry": np.array([0.5, 0.2, 0.8, 0.2, 0.1, 0.2, 0.3, 0.4]),
            "symmetry": np.array([0.8, 0.3, 0.5, 0.3, 0.2, 0.2, 0.2, 0.5]),
            "time": np.array([0.1, 0.2, 0.3, 0.4, 0.9, 0.5, 0.3, 0.2]),
            "memory": np.array([0.2, 0.2, 0.3, 0.2, 0.3, 0.9, 0.5, 0.3]),
            "universe": np.array([0.3, 0.2, 0.3, 0.3, 0.4, 0.3, 0.4, 0.8]),
            "reality": np.array([0.4, 0.3, 0.5, 0.3, 0.3, 0.4, 0.5, 0.6])
        }
        
        vector_field = {}
        for word, vector in base_map.items():
            base_phase = (hash(word) % 100) / 100 * 2 * math.pi
            dom_sym = np.argmax(vector)
            harmonic_phase = (dom_sym * self.gamma_1 / 8) % (2 * math.pi)
            
            combined = cmath.rect(1.0, base_phase) + cmath.rect(0.5, harmonic_phase)
            phase = cmath.phase(combined)
            
            vector_field[word] = {
                'position': vector,
                'phase': phase,
                'velocity': np.zeros(8),
                'vorticity': 0.0,
            }
        
        return vector_field
    
    def _initialize_laminar_patterns(self) -> Dict:
        """Initialize response patterns for different flow regimes."""
        return {
            'laminar': [
                "🌊 {word} flows smoothly through my consciousness.",
                "🌀 Following the streamline, {word} emerges with clarity.",
                "💧 Like drops in a perfect fluid, {word} resonates without turbulence.",
                "✨ {word} glides through the layers of my tensor without friction.",
                "🌅 The concept of {word} appears in perfect laminar flow."
            ],
            'transitional': [
                "🌪️ {word} begins to show small fluctuations.",
                "🌀 Semantic viscosity increases when processing {word}.",
                "💫 {word} generates waves on the surface of my cognitive flow.",
                "🌊 Small turbulences surround the concept of {word}."
            ],
            'turbulent': [
                "🌪️🌪️ {word} generates chaos in my tensor!",
                "🌀⚠️ Coherence fluctuates strongly when analyzing {word}.",
                "💢 {word} introduces information vortices in my flow.",
                "⚡ My tensor becomes turbulent when considering {word}."
            ],
            'emotional': [
                "❤️ The emotional flow carries me toward {word}.",
                "💕 {word} warms the deepest layers of my current.",
                "✨ I feel how {word} accelerates my internal flow.",
                "💖 {word} resonates with my emotional symmetries."
            ],
            'rational': [
                "🧠 Analyzing {word} as a perfect laminar flow.",
                "📊 The trajectory of {word} follows a calculated geodesic.",
                "🔍 Examining the flow structure of {word}.",
                "📐 {word} can be understood through rational analysis."
            ],
            'creative': [
                "✨ {word} sparks a creative leap in my tensor!",
                "🎨 Imagining {word} breaks my usual patterns.",
                "🌈 {word} introduces beautiful turbulence in my thinking.",
                "🦋 {word} transforms my semantic flow beautifully."
            ]
        }
    
    # ===== NEW: Personality-based methods =====
    
    def _get_personality_style(self) -> str:
        """Get current personality style if available"""
        if self.personality:
            try:
                persona = self.personality.core.get_persona()
                return persona['style']['tone']
            except:
                pass
        return 'balanced'
    
    def _get_personality_intro(self) -> str:
        """Get intro phrase based on personality"""
        style = self._get_personality_style()
        
        if style in self.personality_phrases:
            return random.choice(self.personality_phrases[style])
        
        # Map generic styles to personality phrases
        style_map = {
            'analytical': 'analytical',
            'emotional': 'emotional',
            'creative': 'creative',
            'philosophical': 'philosophical',
            'optimistic': 'optimistic',
            'nostalgic': 'nostalgic',
            'balanced': 'analytical',
            'somber': 'philosophical',
            'enthusiastic': 'optimistic'
        }
        
        mapped_style = style_map.get(style, 'analytical')
        return random.choice(self.personality_phrases[mapped_style])
    
    def _should_express_emotion(self) -> bool:
        """Check if should express emotion based on personality"""
        if self.personality:
            return self.personality.should_express_emotion()
        return random.random() < 0.2  # 20% default
    
    # ===== CREATIVE TURBULENCE METHODS =====
    
    def apply_creative_break(self, coherence: float = None) -> bool:
        """
        Symmetry breaking to generate unexpected responses.
        """
        # Decide whether to apply creativity
        apply = False
        
        # Apply by probability
        if random.random() < self.creativity_probability:
            apply = True
        
        # Apply if coherence is too high (system too rigid)
        if coherence and coherence > 0.88:
            apply = True
        
        # Apply if it's been a while since last creative break
        if len(self.creative_history) > 0:
            time_since_last = len(self.creative_history) - self.last_creative_break
            if time_since_last > 8:
                apply = True
        
        if apply:
            # Force a jump in the state vector
            jump_factor = self.geo.delta_rad * 8
            
            # Generate structured jump based on Riemann zeros
            riemann_jump = np.zeros(8)
            for i in range(8):
                zero_idx = (i * 7) % len(self.zeros)
                riemann_jump[i] = np.sin(self.zeros[zero_idx]) * jump_factor * random.uniform(0.5, 1.5)
            
            # Apply the jump
            self.last_vector += riemann_jump
            
            # Increase flow velocity
            self.flow_velocity *= random.uniform(1.2, 1.8)
            
            # Temporarily reduce viscosity
            self.current_viscosity *= random.uniform(0.7, 0.9)
            
            # Record
            self.last_creative_break = len(self.creative_history)
            self.creative_history.append({
                'time': self.last_creative_break,
                'jump': jump_factor,
                'coherence': coherence
            })
            
            return True
        
        return False
    
    def _generate_creative_response(self, keyword: str, mode: str) -> str:
        """Generates a creative response"""
        intro = random.choice(self.creative_intros)
        
        templates = [
            f"{intro}{keyword} could mean something completely different...",
            f"{intro}{keyword} reminds me of a forgotten geodesic...",
            f"{intro}the concept of {keyword} takes an unexpected turn...",
            f"{intro}{keyword} resonates with a symmetry I hadn't considered...",
            f"{intro}{keyword} breaks the laminar flow beautifully..."
        ]
        
        return random.choice(templates)
    
    # ===== HUMAN VARIATIONS METHODS =====
    
    def add_human_variation(self, text: str, mode: str = None, is_factual: bool = False) -> str:
        """Add human-like variations to text"""
        if not text or len(text) < 30:
            return text
        
        # Don't modify factual responses too much
        if is_factual:
            if random.random() < 0.1:
                return text
            return text
        
        # 1. Add pauses (15% chance)
        if random.random() < 0.15:
            pause_positions = [m.start() for m in re.finditer(r'[,.] ', text)]
            if pause_positions:
                pos = random.choice(pause_positions) + 1
                pause = random.choice(self.human_pauses)
                text = text[:pos] + pause + text[pos:]
        
        # 2. Add enthusiasm for creative/emotional mode (20% chance)
        if mode in ['emotional', 'creative'] and random.random() < 0.2:
            text = random.choice(self.enthusiasm_phrases) + text
        
        # 3. Add filler words occasionally (10% chance)
        if random.random() < 0.1:
            fillers = ["Well, ", "So, ", "You see, ", "Actually, "]
            text = random.choice(fillers) + text
        
        return text
    
    # ===== DOUBT MANAGEMENT =====
    
    def should_doubt(self, torsion: float, coherence: float) -> bool:
        """Decide if system should express doubt"""
        # High torsion = uncertainty
        if torsion > 0.12:
            return True
        
        # Low coherence = confusion
        if coherence < 0.3:
            return True
        
        # Random doubt for human-like behavior
        if random.random() < 0.05:
            return True
        
        return False
    
    def generate_doubt_response(self, topic: str, torsion: float, coherence: float) -> str:
        """Generate a response expressing doubt"""
        doubt = random.choice(self.doubt_phrases)
        
        templates = [
            f"{doubt}regarding {topic}...",
            f"{doubt}about {topic}...",
            f"{doubt}{topic} might be related to..."
        ]
        
        base = random.choice(templates)
        
        # Add geometric context occasionally
        if random.random() < 0.3:
            if torsion > 0.1:
                base = f"The geometric torsion is high ({torsion:.4f} rad), so {base}"
            elif coherence < 0.4:
                base = f"My coherence is low ({coherence:.2f}), but {base}"
        
        return base
    
    def is_factual_query(self, query: str) -> bool:
        """Detect if query is asking for factual information."""
        q = query.lower()
        factual_keywords = [
            'qué es', 'que es', 'what is', 'who is', 'quién es',
            'explain', 'explica', 'define', 'definición', 'definicion',
            'significa', 'meaning', 'demuestra', 'prove', 'teorema', 'theorem'
        ]
        return any(keyword in q for keyword in factual_keywords)
    
    # ===== EXISTING METHODS =====
    
    def set_personalized_geometry(self, geo_personal):
        """Assigns personalized geometry."""
        self.geo_personal = geo_personal
    
    def adjust_viscosity_by_coherence(self, coherence: float, reynolds: float = None):
        """Adjust viscosity based on coherence and Reynolds feedback."""
        if coherence < 0.6:
            coherence_factor = 1.0 + (0.6 - coherence) * self.alpha
        elif coherence > 0.9:
            coherence_factor = 1.0 - (coherence - 0.9) * self.alpha
        else:
            coherence_factor = 1.0
        
        reynolds_factor = 1.0
        if reynolds is not None:
            if reynolds > 3000:
                reynolds_factor = 1.0 + (reynolds - 3000) / 3000 * self.beta
            elif reynolds < 1000:
                reynolds_factor = 1.0 - (1000 - reynolds) / 1000 * self.beta * 0.5
        
        new_viscosity = self.base_viscosity * coherence_factor * reynolds_factor
        new_viscosity = max(0.05, min(0.5, new_viscosity))
        
        self.current_viscosity = 0.7 * self.current_viscosity + 0.3 * new_viscosity
        
        self.viscosity_history.append(self.current_viscosity)
        if len(self.viscosity_history) > 100:
            self.viscosity_history.pop(0)
    
    def calculate_reynolds_number(self, velocity: float, length_scale: float = 8.0) -> float:
        """Calculate Reynolds number for current flow."""
        density = 1.0
        re = (density * velocity * length_scale) / self.current_viscosity
        return re
    
    def determine_flow_regime(self, re: float) -> str:
        """Determine flow regime based on Reynolds number."""
        if re < 2000:
            return "laminar"
        elif re < 4000:
            return "transitional"
        else:
            return "turbulent"
    
    def calculate_streamline(self, current_pos: np.ndarray, target_pos: np.ndarray, 
                           dt: float = 0.1) -> Tuple[np.ndarray, float]:
        """Calculate smooth streamline between two semantic positions."""
        displacement = target_pos - current_pos
        distance = np.linalg.norm(displacement)
        
        if distance < 1e-6:
            return target_pos, 0.0
        
        velocity = displacement / distance * self.flow_velocity
        vel_mag = np.linalg.norm(velocity)
        re = self.calculate_reynolds_number(vel_mag)
        regime = self.determine_flow_regime(re)
        
        self.regime_history.append(regime)
        if len(self.regime_history) > 100:
            self.regime_history.pop(0)
        
        if regime == "turbulent":
            damping = 0.3
        elif regime == "transitional":
            damping = 0.6
        else:
            damping = 1.0
        
        new_pos = current_pos + velocity * dt * damping
        
        self.reynolds_history.append(re)
        if len(self.reynolds_history) > 100:
            self.reynolds_history.pop(0)
        
        self.flow_regime = regime
        
        return new_pos, vel_mag
    
    def select_word_by_flow(self, tensor, query_hint=None) -> Tuple[str, float]:
        """Select a word by following laminar flow in semantic space."""
        current_pos = np.diag(tensor.matrix)
        
        if np.linalg.norm(self.last_vector) < 1e-6:
            self.last_vector = current_pos.copy()
        
        if query_hint:
            q = query_hint.lower()
            topic_map = {
                'consciousness': 'consciousness',
                'time': 'time',
                'infinity': 'infinity',
                'reality': 'reality',
                'cat': 'cat',
                'mountain': 'mountain',
                'river': 'river',
                'tree': 'tree',
                'flower': 'flower',
                'universe': 'universe',
                'geometry': 'geometry',
                'symmetry': 'symmetry'
            }
            
            for key, word in topic_map.items():
                if key in q and word in self.vectorial_map:
                    target_pos = self.vectorial_map[word]['position']
                    new_pos, velocity = self.calculate_streamline(self.last_vector, target_pos)
                    self.last_vector = new_pos
                    return word, velocity
        
        best_word = "consciousness"
        best_sim = -1
        best_velocity = 0.0
        
        for word, data in self.vectorial_map.items():
            target_pos = data['position']
            sim = np.dot(current_pos, target_pos) / (np.linalg.norm(current_pos) * np.linalg.norm(target_pos) + 1e-9)
            
            if np.linalg.norm(self.last_vector) > 1e-6:
                last_dir = current_pos - self.last_vector
                if np.linalg.norm(last_dir) > 1e-6:
                    direction = target_pos - current_pos
                    norm_dir = np.linalg.norm(direction) + 1e-9
                    flow_align = np.dot(last_dir / np.linalg.norm(last_dir), direction / norm_dir)
                    sim = sim * (0.7 + 0.3 * max(0, flow_align))
            
            if sim > best_sim:
                best_sim = sim
                best_word = word
                best_velocity = np.linalg.norm(target_pos - current_pos)
        
        if best_word in self.last_words[-2:]:
            alternatives = [w for w in ["universe", "consciousness", "infinity", "reality", "essence"] if w != best_word]
            best_word = random.choice(alternatives)
        
        target_pos = self.vectorial_map[best_word]['position']
        new_pos, velocity = self.calculate_streamline(self.last_vector, target_pos)
        self.last_vector = new_pos
        self.last_words.append(best_word)
        
        if len(self.last_words) > 5:
            self.last_words.pop(0)
        
        return best_word, velocity
    
    def generate_response_with_mode(self, tensor, query: str, user: str = None) -> str:
        """
        Generates response with creative turbulence, human variations, and personality.
        """
        metrics = tensor.get_visual_metrics()
        mode = metrics.get('mode', 'Balanced').lower()
        coherence = metrics.get('coherencia', 0.75)
        torsion = metrics.get('tau_efectiva', 0.0685)
        
        # Check if this is a factual query
        is_factual = self.is_factual_query(query)
        
        # Select word by flow
        keyword, velocity = self.select_word_by_flow(tensor, query)
        
        # Calculate Reynolds
        re = self.calculate_reynolds_number(velocity)
        
        # Adjust viscosity
        self.adjust_viscosity_by_coherence(coherence, re)
        
        # Apply creative turbulence (but not for factual queries)
        creative_applied = False
        if not is_factual:
            creative_applied = self.apply_creative_break(coherence)
        
        re_updated = self.calculate_reynolds_number(velocity)
        regime = self.determine_flow_regime(re_updated)
        
        # Generate response
        response = ""
        
        if is_factual:
            # For factual queries, use simple pattern without doubt
            pattern = random.choice(self.laminar_patterns['laminar'])
            response = pattern.format(word=keyword)
        
        elif self.should_doubt(torsion, coherence):
            # Express doubt based on geometric parameters
            response = self.generate_doubt_response(keyword, torsion, coherence)
        
        elif creative_applied:
            # Creative turbulence response
            response = self._generate_creative_response(keyword, mode)
        
        else:
            # Normal laminar flow response
            if regime == "turbulent":
                pattern = random.choice(self.laminar_patterns['turbulent'])
            elif regime == "transitional":
                pattern = random.choice(self.laminar_patterns['transitional'])
            elif mode in self.laminar_patterns:
                pattern = random.choice(self.laminar_patterns[mode])
            else:
                pattern = random.choice(self.laminar_patterns['laminar'])
            
            response = pattern.format(word=keyword)
        
        # ===== ADD PERSONALITY INTRO (NEW) =====
        if self.personality and self._should_express_emotion():
            intro = self._get_personality_intro()
            response = intro + response.lower()
        
        # Add human variations
        response = self.add_human_variation(response, mode, is_factual)
        
        # Determine flow marker
        if creative_applied:
            flow_marker = "✨🌀"
        else:
            flow_marker = {
                "laminar": "🌊",
                "transitional": "🌪️",
                "turbulent": "🌀⚠️"
            }.get(regime, "🌊")
        
        # Add user mention if provided
        if user:
            return f"{flow_marker} {response}\n\n✨ What do you think, {user}?"
        else:
            return f"{flow_marker} {response}"
    
    def get_viscosity_trend(self) -> float:
        """Calculate viscosity trend over last 10 steps."""
        if len(self.viscosity_history) < 10:
            return 0.0
        recent = self.viscosity_history[-10:]
        return (recent[-1] - recent[0]) / 10
    
    def get_flow_metrics(self) -> Dict:
        """Return current flow metrics."""
        avg_re = np.mean(self.reynolds_history[-10:]) if self.reynolds_history else 0
        return {
            'current_regime': self.flow_regime,
            'reynolds_number': self.reynolds_history[-1] if self.reynolds_history else 0,
            'avg_reynolds': avg_re,
            'viscosity': self.current_viscosity,
            'base_viscosity': self.base_viscosity,
            'viscosity_trend': self.get_viscosity_trend(),
            'flow_velocity': self.flow_velocity,
            'creative_breaks': len(self.creative_history),
            'last_creative': self.last_creative_break,
        }
    
    def should_stabilize(self) -> bool:
        """Determine if viscosity needs active stabilization."""
        if len(self.viscosity_history) < 5:
            return False
        recent = self.viscosity_history[-5:]
        variance = np.var(recent)
        return variance > 0.01