# AI Engine Deployment Guide

This guide covers deployment of the NyxOS AI Engine to GitHub and as a standalone service.

## Prerequisites

- Git installed and configured
- GitHub account
- Python 3.9 or higher
- PyPI account (for publishing to PyPI, optional)

## Step 1: Initialize Git Repository (if not already done)

```bash
cd ai-engine
git init
git add .
git commit -m "Initial commit: NyxOS AI Engine"
```

## Step 2: Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository named `ai-engine` (or `nyxos-ai-engine`)
3. Do NOT initialize with README (we have one)
4. Copy the repository URL

## Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-engine.git
git branch -M main
git push -u origin main
```

## Step 4: Setup Secrets for CI/CD (Optional)

If you want to publish to PyPI automatically:

1. Go to your GitHub repository Settings
2. Navigate to Secrets and Variables → Actions
3. Add `PYPI_API_TOKEN` with your PyPI token

## Step 5: Configure GitHub Pages (Optional)

To host documentation:

1. In repository Settings → Pages
2. Select `main` branch as source
3. Documentation will be published automatically

## Deployment Options

### Option A: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "api.server"]
```

Deploy with:

```bash
docker build -t nyxos-ai-engine .
docker run -p 8000:8000 nyxos-ai-engine
```

### Option B: Direct Python Installation

```bash
pip install git+https://github.com/YOUR_USERNAME/ai-engine.git
python -m api.server
```

### Option C: PyPI Package (After Publishing)

```bash
pip install nyxos-ai-engine
python -m api.server
```

## Versioning

Update version in `setup.py` before releasing:

```python
version="1.0.0"  # Change this
```

Then tag and push:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will trigger PyPI publishing if `PYPI_API_TOKEN` is configured.

## Testing Before Deployment

```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Run the server
python -m api.server
```

## Troubleshooting

### Git not found
- Install Git from https://git-scm.com/download/win (Windows)
- Or use `winget install Git.Git` in PowerShell

### Authentication issues
- Set up SSH keys or use GitHub token authentication
- Generate token at https://github.com/settings/tokens

### Model files too large
- Use Git LFS for large model files:
  ```bash
  git lfs install
  git lfs track "data/models/*"
  git add .gitattributes
  ```

## Continuous Integration

The repository includes GitHub Actions workflows for:

1. **tests.yml**: Runs tests on Python 3.9, 3.10, 3.11 across multiple OS
2. **publish.yml**: Automatically publishes to PyPI on tag push

Tests run on every push and pull request.

## After Deployment

1. Monitor GitHub Actions for workflow status
2. Check repository health with GitHub's built-in analytics
3. Update documentation as features change
4. Follow semantic versioning for releases

## Support & Issues

Users can report issues via GitHub Issues. Set up templates:

1. Go to Settings → Features
2. Set up Issue templates for bugs and feature requests
