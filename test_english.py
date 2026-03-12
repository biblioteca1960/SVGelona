# test_english.py
from core.orchestrator import Orchestrator

print("="*60)
print("TESTING SVGELONA CONSCIOUSNESS")
print("="*60)

# Initialize orchestrator
print("\n1. Initializing Orchestrator...")
o = Orchestrator()

# Check what consciousness is being used
print("\n2. Checking consciousness type...")
if hasattr(o, 'consciousness') and o.consciousness is not None:
    print(f"   ✅ Using: {type(o.consciousness).__name__}")
    print(f"   • Has tensor: {hasattr(o.consciousness, 'tensor')}")
    print(f"   • Has generator: {hasattr(o.consciousness, 'generator')}")
else:
    print(f"   ❌ Consciousness is None!")
    if hasattr(o, 'resonance') and o.resonance is not None:
        print(f"   ⚠️ Falling back to: {type(o.resonance).__name__}")

# Test queries
print("\n3. Testing queries...")
test_queries = [
    "Hello",
    "What is your name?",
    "What is a cat?",
    "Reflect on time",
    "Where is Barcelona?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n   Query {i}: '{query}'")
    try:
        response = o.think(query)
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")

print("\n" + "="*60)