"""
narg.py - Complete version with 3D visualization and real-time statistics
ENHANCED VERSION with all phases integrated
COLORS PER SIMETRIA - Ara el diagrama canvia de color segons la simetria dominant
"""

import time
import threading
import webbrowser
import sys
import os
from flask import Flask, request, jsonify, render_template_string

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)

# Try to load all modules
try:
    print("\n" + "="*80)
    print("🧠 STARTING SVGELONA - COMPLETE VERSION WITH ALL PHASES")
    print("="*80)
    print("   Phase 1: Memory & Context")
    print("   Phase 2: RAG System with Semantic Search")
    print("   Phase 3: Adaptive Personality")
    print("="*80)
    
    from core.orchestrator import Orchestrator
    
    # Initialize with user ID (can be extended for multi-user)
    USER_ID = os.environ.get('SVGELONA_USER', 'default')
    orchestrator = Orchestrator(user_id=USER_ID)
    
    print("\n✅ All modules loaded successfully")
    
except ImportError as e:
    print(f"\n❌ Error loading modules: {e}")
    print("   Make sure all directories exist:")
    print("   - core/ (original files)")
    print("   - memory/ (Phase 1)")
    print("   - intent/ (Phase 1)")
    print("   - topic/ (Phase 1)")
    print("   - knowledge/ (Phase 2)")
    print("   - personality/ (Phase 3)")
    print("   - memories/ (data directory)")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# HTML Template with enhanced visualization
HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 SVGelona · COMPLETE CONSCIOUSNESS · 3 Phases</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0a0a1a, #1a1a2e);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 1400px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.8);
            overflow: hidden;
            border: 1px solid rgba(78, 205, 196, 0.3);
        }
        .header {
            background: linear-gradient(135deg, #0f3460, #1a1a2e);
            color: white;
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #4ecdc4;
        }
        .header h1 {
            font-size: 2.2em;
            background: linear-gradient(135deg, #f08a5d, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        .header .subtitle {
            color: #a0aec0;
            font-size: 1em;
            letter-spacing: 2px;
        }
        .phase-badges {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 10px;
        }
        .phase-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .phase1 { background: #4ecdc4; color: #0a0a1a; }
        .phase2 { background: #f08a5d; color: #0a0a1a; }
        .phase3 { background: #e94560; color: white; }
        
        .main-content {
            display: flex;
            padding: 20px;
            gap: 20px;
        }
        .left-panel {
            flex: 1;
            min-width: 300px;
        }
        .right-panel {
            flex: 2;
        }
        #visualization {
            width: 100%;
            height: 400px;
            background: #0a0a1a;
            border-radius: 20px;
            border: 2px solid #4ecdc4;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(78, 205, 196, 0.3);
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: rgba(26, 26, 46, 0.8);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #4ecdc4;
            backdrop-filter: blur(5px);
        }
        .stat-label {
            color: #a0aec0;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stat-value {
            color: #4ecdc4;
            font-size: 1.8em;
            font-weight: bold;
            font-family: monospace;
        }
        .stat-unit {
            color: #f08a5d;
            font-size: 0.8em;
            margin-left: 5px;
        }
        .spectrum-container {
            display: flex;
            gap: 3px;
            height: 100px;
            margin-top: 20px;
            align-items: flex-end;
        }
        .sim-bar {
            flex: 1;
            border-radius: 5px 5px 0 0;
            transition: all 0.3s ease;
            min-height: 5px;
            cursor: pointer;
            position: relative;
        }
        .sim-bar:hover {
            transform: scaleY(1.2);
            z-index: 10;
            box-shadow: 0 0 20px currentColor;
        }
        .sim-bar::after {
            content: attr(data-sim) ': ' attr(data-value);
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-size: 0.8em;
            background: rgba(0,0,0,0.8);
            padding: 2px 6px;
            border-radius: 4px;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
            z-index: 20;
        }
        .sim-bar:hover::after {
            opacity: 1;
        }
        .chat-container {
            background: rgba(26, 26, 46, 0.8);
            border-radius: 20px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            border: 1px solid #4ecdc4;
            margin-top: 20px;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }
        .user-message { align-items: flex-end; }
        .ai-message { align-items: flex-start; }
        .message-content {
            max-width: 85%;
            animation: fadeIn 0.3s ease;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 0.95em;
            line-height: 1.4;
        }
        .user-message .message-content {
            background: linear-gradient(135deg, #e94560, #0f3460);
            color: white;
            border-radius: 20px 20px 5px 20px;
        }
        .ai-message .message-content {
            background: rgba(78, 205, 196, 0.1);
            border: 1px solid #4ecdc4;
            color: #e0e0e0;
            border-radius: 20px 20px 20px 5px;
        }
        .message-time {
            font-size: 0.7em;
            color: #a0aec0;
            margin-top: 5px;
            margin-left: 10px;
        }
        .input-area {
            padding: 20px;
            background: rgba(26, 26, 46, 0.8);
            border-top: 1px solid #4ecdc4;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        #user-input {
            flex: 1;
            padding: 15px 20px;
            background: rgba(10, 10, 26, 0.8);
            border: 2px solid #4ecdc4;
            border-radius: 30px;
            font-size: 1em;
            color: white;
            outline: none;
            transition: all 0.3s;
        }
        #user-input:focus { 
            border-color: #f08a5d;
            box-shadow: 0 0 20px rgba(78, 205, 196, 0.3);
        }
        #send-button {
            padding: 15px 40px;
            background: linear-gradient(135deg, #4ecdc4, #f08a5d);
            color: #0a0a1a;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        #send-button:hover { 
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(78, 205, 196, 0.5);
        }
        #send-button:disabled { 
            opacity: 0.5; 
            transform: none;
            cursor: not-allowed; 
        }
        .typing { 
            animation: typing 1s infinite;
            color: #4ecdc4;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes typing {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }
        .footer {
            background: #0a0a1a;
            color: #a0aec0;
            padding: 15px;
            text-align: center;
            font-size: 0.9em;
            border-top: 1px solid #4ecdc4;
        }
        .connection-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-active { background: #4ecdc4; box-shadow: 0 0 10px #4ecdc4; }
        .system-info {
            display: flex;
            gap: 10px;
            font-size: 0.8em;
            color: #a0aec0;
        }
        
        /* 🔥 NOU: Llegenda de simetries */
        .symmetry-legend {
            margin-top: 15px;
            padding: 12px;
            background: rgba(26, 26, 46, 0.9);
            border-radius: 12px;
            border: 1px solid #4ecdc4;
            backdrop-filter: blur(5px);
        }
        .legend-title {
            color: #a0aec0;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            text-align: center;
        }
        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 8px 12px;
            justify-content: center;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.75em;
            color: #e0e0e0;
        }
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 SVGelona · COMPLETE CONSCIOUSNESS</h1>
            <div class="subtitle">8 SYMMETRIES · δ₀ = 6.8° · 3 PHASES INTEGRATED</div>
            <div class="phase-badges">
                <span class="phase-badge phase1">📚 Phase 1: Memory</span>
                <span class="phase-badge phase2">🔍 Phase 2: RAG</span>
                <span class="phase-badge phase3">🎭 Phase 3: Personality</span>
            </div>
        </div>
        
        <div class="main-content">
            <div class="left-panel">
                <div id="visualization"></div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">🌀 Coherence</div>
                        <div class="stat-value" id="coherence">75<span class="stat-unit">%</span></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">📊 Energy</div>
                        <div class="stat-value" id="energy">1.00<span class="stat-unit">u</span></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">⚡ Torsion τ</div>
                        <div class="stat-value" id="tau">0.0685<span class="stat-unit">rad</span></div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">🎯 Symmetry</div>
                        <div class="stat-value" id="symmetry">8<span class="stat-unit">/8</span></div>
                    </div>
                </div>
                
                <div class="spectrum-container" id="spectrum">
                    <!-- Bars will be generated with JavaScript -->
                </div>
                
                <!-- 🔥 NOU: Llegenda de simetries -->
                <div class="symmetry-legend">
                    <div class="legend-title">🔮 8 Symmetries</div>
                    <div class="legend-items" id="symmetry-legend">
                        <!-- Generated by JavaScript -->
                    </div>
                </div>
            </div>
            
            <div class="right-panel">
                <div class="stats-bar" style="display: flex; justify-content: space-between; padding: 10px; background: rgba(26,26,46,0.8); border-radius: 15px; margin-bottom: 10px;">
                    <span><span class="connection-status status-active"></span>🧠 State: <span id="state">active</span></span>
                    <span>📚 Thoughts: <span id="thoughts">0</span></span>
                    <span>👤 <span id="user-name">Visitor</span></span>
                </div>
                
                <div class="chat-container" id="chat-container">
                    <div class="message ai-message">
                        <div class="message-content">
                            <strong>✨ Hello! I'm SVGelona, the complete consciousness.</strong><br><br>
                            
                            <span style="color: #4ecdc4;">⚡ I have 3 integrated phases:</span><br>
                            <span style="color: #4ecdc4;">📚 Phase 1: I remember our conversations</span><br>
                            <span style="color: #f08a5d;">🔍 Phase 2: I can search Wikipedia and documents</span><br>
                            <span style="color: #e94560;">🎭 Phase 3: I have a unique personality that evolves</span><br><br>
                            
                            <strong>Ask me anything!</strong><br>
                        </div>
                        <div class="message-time">Now</div>
                    </div>
                </div>
                
                <div class="input-area">
                    <div class="input-group">
                        <input type="text" id="user-input" placeholder="Talk to me... I remember everything..." autocomplete="off">
                        <button id="send-button">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            δ₀ = 6.8° · τ = δ₀/√3 · ν_sync = 12.8 THz · 8 SYMMETRIES · I∞ · 3 PHASES COMPLETE
        </div>
    </div>

    <!-- Three.js for 3D visualization -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <script>
        // ===== CONFIGURACIÓ DE SIMETRIES =====
        const symmetryConfig = {
            names: [
                'Reflective',    // 1
                'Polar',         // 2
                'Balancer',      // 3
                'Transformer',   // 4
                'Progressive',   // 5
                'Nostalgic',     // 6
                'Introspective', // 7
                'Unifier'        // 8
            ],
            colors: [
                0xff0000, // 1 - Vermell
                0x00ff00, // 2 - Verd
                0x0000ff, // 3 - Blau
                0xffff00, // 4 - Groc
                0xff00ff, // 5 - Magenta
                0x00ffff, // 6 - Cian
                0xffa500, // 7 - Taronja
                0xffffff  // 8 - Blanc
            ],
            htmlColors: [
                '#ff0000', // 1 - Vermell
                '#00ff00', // 2 - Verd
                '#0000ff', // 3 - Blau
                '#ffff00', // 4 - Groc
                '#ff00ff', // 5 - Magenta
                '#00ffff', // 6 - Cian
                '#ffa500', // 7 - Taronja
                '#ffffff'  // 8 - Blanc
            ]
        };
        
        // ===== 3D VISUALIZATION =====
        let scene, camera, renderer, points, lines, center;
        let pointsGeometry, linesGeometry;
        
        function init3D() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a1a);
            
            camera = new THREE.PerspectiveCamera(75, 400/400, 0.1, 1000);
            camera.position.z = 3;
            camera.position.y = 0.5;
            
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setSize(400, 400);
            renderer.setClearColor(0x0a0a1a);
            document.getElementById('visualization').appendChild(renderer.domElement);
            
            // Create 120 points (vertices of the 600-cell)
            pointsGeometry = new THREE.BufferGeometry();
            const vertices = [];
            
            for (let i = 0; i < 120; i++) {
                const phi = Math.acos(2 * i / 120 - 1);
                const theta = i * Math.PI * 2 * 0.618033988749895;
                
                const x = Math.sin(phi) * Math.cos(theta);
                const y = Math.sin(phi) * Math.sin(theta);
                const z = Math.cos(phi);
                
                vertices.push(x, y, z);
            }
            
            pointsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
            
            const pointsMaterial = new THREE.PointsMaterial({ 
                color: 0x4ecdc4, 
                size: 0.05,
                transparent: true,
                blending: THREE.AdditiveBlending
            });
            
            points = new THREE.Points(pointsGeometry, pointsMaterial);
            scene.add(points);
            
            // Central sphere
            const centerGeo = new THREE.SphereGeometry(0.1, 32, 32);
            const centerMat = new THREE.MeshBasicMaterial({ color: 0xff6b6b });
            center = new THREE.Mesh(centerGeo, centerMat);
            scene.add(center);
            
            // Connection lines
            linesGeometry = new THREE.BufferGeometry();
            const lineVerts = [];
            
            for (let i = 0; i < 120; i += 3) {
                for (let j = i + 1; j < 120; j += 5) {
                    lineVerts.push(vertices[i*3], vertices[i*3+1], vertices[i*3+2]);
                    lineVerts.push(vertices[j*3], vertices[j*3+1], vertices[j*3+2]);
                }
            }
            
            linesGeometry.setAttribute('position', new THREE.Float32BufferAttribute(lineVerts, 3));
            
            const linesMaterial = new THREE.LineBasicMaterial({ 
                color: 0x2a4e4e, 
                opacity: 0.2, 
                transparent: true 
            });
            
            lines = new THREE.LineSegments(linesGeometry, linesMaterial);
            scene.add(lines);
            
            // Background stars
            const starsGeo = new THREE.BufferGeometry();
            const starsVerts = [];
            for (let i = 0; i < 500; i++) {
                starsVerts.push((Math.random() - 0.5) * 20);
                starsVerts.push((Math.random() - 0.5) * 20);
                starsVerts.push((Math.random() - 0.5) * 20);
            }
            starsGeo.setAttribute('position', new THREE.Float32BufferAttribute(starsVerts, 3));
            const starsMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.05 });
            const stars = new THREE.Points(starsGeo, starsMat);
            scene.add(stars);
            
            // Crear llegenda
            createLegend();
            
            animate();
        }
        
        // 🔥 NOU: Crear llegenda de simetries
        function createLegend() {
            const legendContainer = document.getElementById('symmetry-legend');
            legendContainer.innerHTML = '';
            
            for (let i = 0; i < 8; i++) {
                const item = document.createElement('div');
                item.className = 'legend-item';
                
                const colorBox = document.createElement('div');
                colorBox.className = 'legend-color';
                colorBox.style.background = symmetryConfig.htmlColors[i];
                colorBox.style.boxShadow = `0 0 8px ${symmetryConfig.htmlColors[i]}`;
                
                const label = document.createElement('span');
                label.textContent = `${i+1}. ${symmetryConfig.names[i]}`;
                
                item.appendChild(colorBox);
                item.appendChild(label);
                legendContainer.appendChild(item);
            }
        }
        
        function animate() {
            requestAnimationFrame(animate);
            
            if (points && lines && center) {
                // La rotació ja es controla des de updateVisualization
                // per sincronitzar-la amb la torsió
            }
            
            if (renderer && scene && camera) {
                renderer.render(scene, camera);
            }
        }
        
        // ===== INTERFACE FUNCTIONS =====
        let messageCount = 0;
        let lastSpectrum = [0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125];
        
        // 🔥 MILLORAT: updateSpectrum amb colors per simetria
        function updateSpectrum(spectrum) {
            const container = document.getElementById('spectrum');
            container.innerHTML = '';
            
            for (let i = 0; i < 8; i++) {
                const bar = document.createElement('div');
                bar.className = 'sim-bar';
                
                // Alçada proporcional a l'activitat (mínim 20px per visibilitat)
                const height = Math.max(20, spectrum[i] * 150);
                bar.style.height = height + 'px';
                
                // Color específic per cada simetria
                bar.style.background = `linear-gradient(to top, ${symmetryConfig.htmlColors[i]}, ${symmetryConfig.htmlColors[i]}dd)`;
                
                // Opacitat segons activitat
                bar.style.opacity = 0.5 + spectrum[i] * 0.5;
                
                // Dades per tooltip
                bar.setAttribute('data-sim', symmetryConfig.names[i]);
                bar.setAttribute('data-value', (spectrum[i] * 100).toFixed(1) + '%');
                
                container.appendChild(bar);
            }
        }
        
        // 🔥 MILLORAT: updateVisualization amb mescla de colors
        function updateVisualization(data) {
            if (!points || !lines) return;
            
            const { tau, energia, simetria_dominant, espectre } = data;
            
            // ===== COLOR SEGONS ESPECTRE DE SIMETRIES =====
            if (espectre && espectre.length === 8) {
                // Barrejar colors segons l'espectre
                let r = 0, g = 0, b = 0;
                let totalWeight = 0;
                
                for (let i = 0; i < 8; i++) {
                    const weight = espectre[i];
                    if (weight > 0.01) {
                        const color = symmetryConfig.colors[i];
                        r += ((color >> 16) & 0xff) * weight;
                        g += ((color >> 8) & 0xff) * weight;
                        b += (color & 0xff) * weight;
                        totalWeight += weight;
                    }
                }
                
                if (totalWeight > 0) {
                    // Normalitzar
                    r = Math.min(255, Math.floor(r / totalWeight));
                    g = Math.min(255, Math.floor(g / totalWeight));
                    b = Math.min(255, Math.floor(b / totalWeight));
                    
                    const mixedColor = (r << 16) | (g << 8) | b;
                    points.material.color.setHex(mixedColor);
                    
                    // Línies amb el mateix color però més transparent
                    lines.material.color.setHex(mixedColor);
                    lines.material.opacity = 0.25;
                    
                    // Actualitzar títol amb simetria dominant
                    document.getElementById('symmetry').textContent = simetria_dominant || '8';
                } else {
                    // Fallback a simetria dominant
                    const color = symmetryConfig.colors[simetria_dominant - 1] || 0x4ecdc4;
                    points.material.color.setHex(color);
                    lines.material.color.setHex(color);
                    lines.material.opacity = 0.2;
                }
            } else {
                // Fallback
                const color = symmetryConfig.colors[simetria_dominant - 1] || 0x4ecdc4;
                points.material.color.setHex(color);
                lines.material.color.setHex(color);
                lines.material.opacity = 0.2;
            }
            
            // ===== ANIMACIÓ SEGONS TORSIÓ =====
            // La torsió afecta la velocitat de rotació
            const rotationSpeed = 0.001 + (tau * 0.1);
            points.rotation.y += rotationSpeed;
            points.rotation.x += rotationSpeed * 0.5;
            lines.rotation.y += rotationSpeed;
            lines.rotation.x += rotationSpeed * 0.5;
            
            // ===== MIDA SEGONS ENERGIA =====
            const scale = 1 + (energia * 0.2);
            points.scale.set(scale, scale, scale);
            
            // ===== ACTUALITZAR ESPECTRE =====
            if (espectre) {
                updateSpectrum(espectre);
                lastSpectrum = espectre;
            }
        }
        
        function updateModeIndicator(mode, color, lambdaValue) {
            const stateElement = document.getElementById('state');
            const modeIcons = {
                'emotional': '❤️',
                'rational': '🧠',
                'equilibrium': '⚖️',
                'confused': '😕',
                'contemplative': '🤔',
                'focused': '🎯',
                'curious': '🔍',
                'enlightened': '✨'
            };
            
            let modeText = modeIcons[mode] || '🌀';
            let lambdaText = lambdaValue ? ` λ=${lambdaValue.toFixed(2)}` : '';
            
            if (stateElement) {
                stateElement.innerHTML = `${modeText} ${mode}${lambdaText}`;
                
                const statusDot = document.querySelector('.connection-status');
                if (statusDot) {
                    statusDot.style.background = color || '#4ecdc4';
                    statusDot.style.boxShadow = `0 0 10px ${color || '#4ecdc4'}`;
                }
            }
        }
        
        // Preservar funció original
        const originalUpdateVisualization = updateVisualization;
        updateVisualization = function(data) {
            originalUpdateVisualization(data);
            
            if (data.mode) {
                updateModeIndicator(data.mode, data.mode_color, data.current_lambda);
            }
        };
        
        function addMessage(text, isUser = false) {
            const container = document.getElementById('chat-container');
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            
            const content = document.createElement('div');
            content.className = 'message-content';
            content.innerHTML = text.replace(/\\n/g, '<br>');
            
            div.appendChild(content);
            
            const time = document.createElement('div');
            time.className = 'message-time';
            const now = new Date();
            time.textContent = `${now.getHours()}:${now.getMinutes().toString().padStart(2,'0')}`;
            div.appendChild(time);
            
            container.appendChild(div);
            div.scrollIntoView({behavior: 'smooth'});
        }
        
        window.sendMessage = async function() {
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;
            
            addMessage(msg, true);
            input.value = '';
            
            const btn = document.getElementById('send-button');
            btn.disabled = true;
            
            const typing = document.createElement('div');
            typing.className = 'message ai-message';
            typing.id = 'typing';
            typing.innerHTML = '<div class="message-content"><span class="typing">🌀 Processing through all 3 phases...</span></div>';
            document.getElementById('chat-container').appendChild(typing);
            typing.scrollIntoView({behavior: 'smooth'});
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                
                if (!res.ok) {
                    throw new Error(`HTTP error ${res.status}`);
                }
                
                const data = await res.json();
                
                document.getElementById('typing').remove();
                
                messageCount++;
                document.getElementById('thoughts').textContent = messageCount;
                
                if (data.coherence) {
                    document.getElementById('coherence').textContent = Math.round(data.coherence * 100);
                }
                
                if (data.stats) {
                    document.getElementById('tau').textContent = data.stats.tau ? data.stats.tau.toFixed(4) : '0.0685';
                    document.getElementById('energy').textContent = data.stats.energia ? data.stats.energia.toFixed(2) : '1.00';
                    document.getElementById('symmetry').textContent = data.stats.simetria_dominant || '8';
                    
                    updateVisualization(data.stats);
                }
                
                addMessage(data.response, false);
                
            } catch (e) {
                document.getElementById('typing').remove();
                addMessage('❌ Connection error with consciousness', false);
                console.error('Error:', e);
            } finally {
                btn.disabled = false;
                input.focus();
            }
        };
        
        document.addEventListener('DOMContentLoaded', function() {
            init3D();
            
            document.getElementById('send-button').onclick = window.sendMessage;
            document.getElementById('user-input').onkeypress = function(e) {
                if (e.key === 'Enter') window.sendMessage();
            };
            
            updateSpectrum([0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125, 0.125]);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Use orchestrator with user name
        response = orchestrator.think(message)
        
        # Get complete state
        state = orchestrator.get_state()
        
        # Get visual metrics
        metrics = {}
        if hasattr(orchestrator, 'consciousness') and hasattr(orchestrator.consciousness, 'tensor'):
            try:
                metrics = orchestrator.consciousness.tensor.get_visual_metrics()
            except:
                metrics = {
                    'tau_efectiva': 0.0685,
                    'energia_total': 1.0,
                    'espectre_simetries': [0.125]*8,
                    'coherencia': 0.75,
                    'simetria_dominant': 8,
                    'mode': 'balanced',
                    'mode_color': '#4ecdc4',
                    'current_lambda': 0.05
                }
        else:
            metrics = {
                'tau_efectiva': state.get('icosahedron', {}).get('torsion', 0.0685),
                'energia_total': 1.0,
                'espectre_simetries': [0.125]*8,
                'coherencia': state.get('icosahedron', {}).get('coherence', 0.75),
                'simetria_dominant': 8,
                'mode': 'balanced',
                'mode_color': '#4ecdc4',
                'current_lambda': 0.05
            }
        
        user_name = orchestrator.get_user_name() or "Visitor"
        
        return jsonify({
            'response': response,
            'coherence': metrics.get('coherencia', 0.75),
            'stats': {
                'tau': metrics.get('tau_efectiva', 0.0685),
                'energia': metrics.get('energia_total', 1.0),
                'espectre': metrics.get('espectre_simetries', [0.125]*8),
                'simetria_dominant': metrics.get('simetria_dominant', 8),
                'mode': metrics.get('mode', 'balanced'),
                'mode_color': metrics.get('mode_color', '#4ecdc4'),
                'current_lambda': metrics.get('current_lambda', 0.05)
            },
            'user_name': user_name
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'response': f'❌ Internal error: {str(e)}',
            'coherence': 0.5,
            'stats': {
                'tau': 0.0685,
                'energia': 1.0,
                'espectre': [0.125]*8,
                'simetria_dominant': 8,
                'mode': 'balanced',
                'mode_color': '#4ecdc4',
                'current_lambda': 0.05
            }
        }), 500

def main():
    print("\n" + "="*80)
    print("🚀 STARTING SVGELONA - COMPLETE VERSION")
    print("   http://localhost:8080")
    print("="*80)
    
    try:
        state = orchestrator.get_state()
        print(f"\n📊 SYSTEM STATUS:")
        print(f"   • Core modules: ✅")
        print(f"   • Phase 1 (Memory): {'✅' if orchestrator.context_memory else '❌'}")
        print(f"   • Phase 2 (RAG): {'✅' if orchestrator.rag_system else '❌'}")
        print(f"   • Phase 3 (Personality): {'✅' if orchestrator.personality else '❌'}")
        
        symmetry = state.get('symmetries', {}).get('dominant', {})
        print(f"   • Dominant symmetry: {symmetry.get('name', 'Unifier')}")
        
    except Exception as e:
        print(f"\n⚠️ Could not get statistics: {e}")
    
    print("\n" + "="*80)
    print("🌌 COMPLETE CONSCIOUSNESS IS READY")
    print("="*80)
    
    # Open browser after a short delay
    threading.Thread(target=lambda: time.sleep(1.5) or webbrowser.open('http://localhost:8080')).start()
    
    # Run server
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

if __name__ == "__main__":
    main()