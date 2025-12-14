# Fix for urllib3/six Module Error

## Issue
When running `test_ai.py` on Python 3.14, you may encounter:
```
ModuleNotFoundError: No module named 'urllib3.packages.six.moves'
```

This is a compatibility issue between older urllib3 versions and Python 3.14.

## Solution

### Option 1: Upgrade urllib3 (Recommended)

```bash
pip install --upgrade "urllib3>=2.0.0"
```

Or use the provided script:
```bash
fix_dependencies.bat
```

### Option 2: Use Built-in urllib (Already Implemented)

The `test_ai.py` script has been updated to automatically fall back to Python's built-in `urllib` if `requests` is not available or has issues.

### Option 3: Reinstall requests

```bash
pip uninstall requests urllib3
pip install requests urllib3
```

## Verification

After fixing, test with:
```bash
python test_ai.py
```

The script will work with either `requests` or built-in `urllib`.

## Note

Python 3.14 is very new, and some packages may have compatibility issues. The test script now handles this gracefully by falling back to standard library modules.

