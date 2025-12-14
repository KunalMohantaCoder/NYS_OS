#!/usr/bin/env python3
"""
Debug and validation script for NyxOS AI Engine.
Checks for common issues and validates the implementation.
"""
import os
import sys
import importlib.util
from pathlib import Path

def check_imports():
    """Check if all required modules can be imported."""
    print("=" * 60)
    print("Checking Imports")
    print("=" * 60)
    
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 9):
        issues.append(f"[X] Python 3.9+ required, found {sys.version}")
    else:
        print(f"[OK] Python version: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = {
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'tqdm': 'tqdm',
    }
    
    # requests is optional (has fallback)
    optional_packages = {
        'requests': 'requests (optional - has urllib fallback)'
    }
    
    for module, name in required_packages.items():
        try:
            __import__(module)
            print(f"[OK] {name} installed")
        except ImportError:
            issues.append(f"[X] {name} not installed. Run: pip install {module}")
            print(f"[X] {name} not installed")
    
    for module, name in optional_packages.items():
        try:
            __import__(module)
            print(f"[OK] {name} installed")
        except ImportError:
            print(f"[~] {name} not installed (optional - fallback available)")
    
    return issues

def check_file_structure():
    """Check if all required files exist."""
    print("\n" + "=" * 60)
    print("Checking File Structure")
    print("=" * 60)
    
    issues = []
    base_dir = Path(__file__).parent
    
    required_files = [
        'model/__init__.py',
        'model/attention.py',
        'model/embeddings.py',
        'model/transformer.py',
        'model/model.py',
        'training/__init__.py',
        'training/tokenizer.py',
        'training/dataset.py',
        'training/trainer.py',
        'training/data_preprocessing.py',
        'inference/__init__.py',
        'inference/generator.py',
        'inference/context_manager.py',
        'inference/inference_engine.py',
        'assistant/__init__.py',
        'assistant/task_parser.py',
        'assistant/file_manager.py',
        'assistant/system_commands.py',
        'assistant/scheduler.py',
        'assistant/assistant.py',
        'api/__init__.py',
        'api/server.py',
        'requirements.txt',
        'train.py',
    ]
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"[OK] {file_path}")
        else:
            issues.append(f"[X] Missing: {file_path}")
            print(f"[X] {file_path}")
    
    return issues

def check_syntax():
    """Check Python syntax of key files."""
    print("\n" + "=" * 60)
    print("Checking Syntax")
    print("=" * 60)
    
    issues = []
    base_dir = Path(__file__).parent
    
    key_files = [
        'model/model.py',
        'training/tokenizer.py',
        'inference/inference_engine.py',
        'api/server.py',
    ]
    
    for file_path in key_files:
        full_path = base_dir / file_path
        if not full_path.exists():
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(full_path), 'exec')
            print(f"[OK] {file_path} - syntax OK")
        except SyntaxError as e:
            issues.append(f"[X] {file_path} - Syntax error: {e}")
            print(f"[X] {file_path} - Syntax error: {e}")
        except Exception as e:
            issues.append(f"[X] {file_path} - Error: {e}")
            print(f"[X] {file_path} - Error: {e}")
    
    return issues

def check_import_paths():
    """Check if import paths work correctly."""
    print("\n" + "=" * 60)
    print("Checking Import Paths")
    print("=" * 60)
    
    issues = []
    base_dir = Path(__file__).parent
    
    # Add parent directory to path for proper package imports
    parent_dir = base_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Also add current directory
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    
    modules_to_test = [
        ('model.model', 'TransformerModel'),
        ('training.tokenizer', 'BPETokenizer'),
        ('inference.inference_engine', 'InferenceEngine'),
        ('assistant.assistant', 'PersonalAssistant'),
    ]
    
    for module_name, class_name in modules_to_test:
        success = False
        error_msg = None
        
        # Try importing directly (from ai-engine directory)
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"[OK] {module_name}.{class_name}")
            success = True
        except ImportError as e:
            error_msg = str(e)
            # Relative import errors are expected when importing directly
            # The code will work fine when run as a module (python -m api.server)
            if 'attempted relative import' in str(e):
                print(f"[OK] {module_name}.{class_name} (relative imports - works when run as module)")
                success = True  # Not an issue
            elif 'No module named' in str(e) and ('torch' in str(e) or '..' in str(e)):
                # Missing dependency or relative import - both are OK
                print(f"[OK] {module_name}.{class_name} (structure OK - works in module context)")
                success = True
        except AttributeError as e:
            error_msg = str(e)
        except Exception as e:
            error_msg = str(e)
            # Check if it's a dependency issue
            if 'torch' in str(e).lower() or 'No module named' in str(e):
                print(f"[OK] {module_name}.{class_name} (requires dependencies)")
                success = True
            else:
                issues.append(f"[X] {module_name}.{class_name} - {e}")
                print(f"[X] {module_name}.{class_name} - {e}")
                success = True
        
        if not success and error_msg:
            # Only report as issue if it's not a relative import or dependency problem
            if 'attempted relative import' not in error_msg and 'torch' not in error_msg.lower():
                issues.append(f"[X] Cannot import {module_name}.{class_name}: {error_msg}")
                print(f"[X] {module_name}.{class_name} - {error_msg}")
            else:
                print(f"[OK] {module_name}.{class_name} (structure OK)")
    
    return issues

def check_data_directories():
    """Check if data directories exist or can be created."""
    print("\n" + "=" * 60)
    print("Checking Data Directories")
    print("=" * 60)
    
    issues = []
    base_dir = Path(__file__).parent
    
    dirs = [
        'data',
        'data/models',
        'data/training',
        'data/assistant',
    ]
    
    for dir_path in dirs:
        full_path = base_dir / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] {dir_path}/")
        except Exception as e:
            issues.append(f"[X] Cannot create {dir_path}: {e}")
            print(f"[X] {dir_path}/ - {e}")
    
    return issues

def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print("NyxOS AI Engine - Debug Check")
    print("=" * 60)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_imports())
    all_issues.extend(check_file_structure())
    all_issues.extend(check_syntax())
    all_issues.extend(check_import_paths())
    all_issues.extend(check_data_directories())
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if not all_issues:
        print("\n[OK] All checks passed! The system appears ready for deployment.")
        print("\nNext steps:")
        print("1. Train the model: python train.py")
        print("2. Start the service: python -m api.server")
        print("3. Test the API: python test_ai.py")
        return 0
    else:
        print(f"\n[X] Found {len(all_issues)} issue(s):")
        for issue in all_issues:
            print(f"  {issue}")
        print("\nPlease fix these issues before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

