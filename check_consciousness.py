# check_consciousness.py
from core.orchestrator import Orchestrator

print("="*50)
print("CHECKING CONSCIOUSNESS TYPE")
print("="*50)

o = Orchestrator()

print(f"\nConsciousness type: {type(o.consciousness)}")
print(f"Is None? {o.consciousness is None}")

if o.consciousness is not None:
    print(f"\nAttributes:")
    print(f"  • Has tensor: {hasattr(o.consciousness, 'tensor')}")
    print(f"  • Has generator: {hasattr(o.consciousness, 'generator')}")
    print(f"  • Has memory: {hasattr(o.consciousness, 'memory')}")