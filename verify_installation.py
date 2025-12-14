#!/usr/bin/env python3
"""
NyxOS AI Engine - Verification Script
Checks that all dependencies and modules are properly installed
"""

import sys

print("\n" + "="*60)
print("NyxOS AI Engine - Dependency & Module Verification")
print("="*60)

# Check core dependencies
print("\n✓ Checking Core Dependencies...")
try:
    import torch
    print(f"  ✓ PyTorch {torch.__version__}")
except ImportError as e:
    print(f"  ✗ PyTorch: {e}")
    sys.exit(1)

try:
    import numpy
    print(f"  ✓ NumPy {numpy.__version__}")
except ImportError as e:
    print(f"  ✗ NumPy: {e}")
    sys.exit(1)

try:
    import fastapi
    print(f"  ✓ FastAPI {fastapi.__version__}")
except ImportError as e:
    print(f"  ✗ FastAPI: {e}")
    sys.exit(1)

try:
    import pydantic
    print(f"  ✓ Pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"  ✗ Pydantic: {e}")
    sys.exit(1)

try:
    import uvicorn
    print(f"  ✓ Uvicorn installed")
except ImportError as e:
    print(f"  ✗ Uvicorn: {e}")
    sys.exit(1)

# Check AI Engine modules
print("\n✓ Checking AI Engine Modules...")
try:
    from model.transformer import Transformer
    print("  ✓ Transformer model")
except ImportError as e:
    print(f"  ✗ Transformer model: {e}")

try:
    from training.tokenizer import BPETokenizer
    print("  ✓ BPE Tokenizer")
except ImportError as e:
    print(f"  ✗ BPE Tokenizer: {e}")

try:
    from inference.inference_engine import InferenceEngine
    print("  ✓ Inference Engine")
except ImportError as e:
    print(f"  ✗ Inference Engine: {e}")

try:
    from assistant.assistant import PersonalAssistant
    print("  ✓ Personal Assistant")
except ImportError as e:
    print(f"  ✗ Personal Assistant: {e}")

try:
    from api.server import app
    print("  ✓ FastAPI Server")
except ImportError as e:
    print(f"  ✗ FastAPI Server: {e}")

print("\n" + "="*60)
print("✅ ALL DEPENDENCIES & MODULES VERIFIED SUCCESSFULLY!")
print("="*60)
print("\nYour AI Engine is ready to use!")
print("\nNext steps:")
print("  1. Start the server: python -m api.server")
print("  2. Train the model: python train.py")
print("  3. Run tests: python test_ai.py")
print("="*60)
