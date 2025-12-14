# AI Engine GitHub Deployment Instructions

This document provides step-by-step instructions to deploy the NyxOS AI Engine as a separate repository on GitHub.

## Prerequisites

1. **Install Git**
   - Windows: Download from https://git-scm.com/download/win
   - Or use: `winget install Git.Git` in PowerShell (Admin)
   - Or use: `choco install git` if you have Chocolatey

2. **GitHub Account** - Create one at https://github.com/signup

3. **Configure Git** (first time only)
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

4. **Generate GitHub Token**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token"
   - Select `repo` scope
   - Copy the token (you'll need it for authentication)

## Deployment Steps

### Step 1: Initialize Local Git Repository

```bash
cd d:\nyxs_system\ai-engine
git init
git add .
git commit -m "Initial commit: NyxOS AI Engine"
```

### Step 2: Create Remote Repository on GitHub

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `nyxos-ai-engine` (or just `ai-engine`)
   - **Description**: "Neural network-based LLM and personal assistant for NyxOS"
   - **Visibility**: Choose `Public` or `Private`
   - **DO NOT** check "Initialize this repository with"
3. Click "Create repository"
4. Copy the repository URL (should look like: `https://github.com/YOUR_USERNAME/nyxos-ai-engine.git`)

### Step 3: Add Remote and Push

```bash
cd d:\nyxs_system\ai-engine
git remote add origin https://github.com/YOUR_USERNAME/nyxos-ai-engine.git
git branch -M main
git push -u origin main
```

When prompted for credentials:
- **Username**: Your GitHub username
- **Password**: Use the token you generated (paste it; it won't show as you type)

### Step 4: Verify Deployment

1. Go to `https://github.com/YOUR_USERNAME/nyxos-ai-engine`
2. Verify that all files are uploaded
3. Check that the README.md is displayed correctly

### Step 5: Setup GitHub Actions (CI/CD)

The workflows are already in `.github/workflows/`. They will automatically run when you push code.

To enable publishing to PyPI (optional):

1. Create a PyPI account at https://pypi.org
2. Generate an API token at https://pypi.org/help/#apitoken
3. Go to your GitHub repository → Settings → Secrets and variables → Actions
4. Click "New repository secret"
5. Add:
   - **Name**: `PYPI_API_TOKEN`
   - **Value**: Your PyPI API token

### Step 6: Create Release (Optional)

```bash
# Tag the current commit as a release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This will trigger automatic publishing to PyPI if configured.

## Deployment Options

### Option A: Docker Hub Deployment

1. Create Docker Hub account at https://hub.docker.com
2. Connect GitHub to Docker Hub in account settings
3. Create automated build:
   - Link GitHub repository
   - Set build rules for tags/branches
4. Docker image will build automatically on push

### Option B: Azure Container Registry (ACR)

```bash
# Login to Azure
az login

# Create container registry
az acr create --resource-group myResourceGroup --name myregistry --sku Basic

# Build and push image
az acr build --registry myregistry --image nyxos-ai-engine:latest .
```

### Option C: AWS ECR Deployment

```bash
# Configure AWS credentials first
aws configure

# Create ECR repository
aws ecr create-repository --repository-name nyxos-ai-engine

# Build and push image
docker build -t nyxos-ai-engine .
docker tag nyxos-ai-engine:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/nyxos-ai-engine:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/nyxos-ai-engine:latest
```

### Option D: Direct Installation from GitHub

Users can now install directly:

```bash
pip install git+https://github.com/YOUR_USERNAME/nyxos-ai-engine.git
```

## Troubleshooting

### Git not found after installation
- Restart PowerShell/Terminal after installing Git
- Or use Git Bash instead

### Authentication errors
```bash
# Use token instead of password
# When prompted for password, paste your GitHub token

# Or configure credential helper
git config --global credential.helper manager-core
```

### "fatal: 'origin' does not appear to be a 'git' repository"
```bash
# Fix: Ensure you're in the correct directory
cd d:\nyxs_system\ai-engine
# And that git is initialized
git status
```

### Large model files causing issues
```bash
# Install and use Git LFS for large files
git lfs install
git lfs track "data/models/*.pt"
git add .gitattributes
git commit -m "Setup Git LFS for model files"
```

## Next Steps

1. **Monitor CI/CD**: Go to "Actions" tab in GitHub to see workflow status
2. **Create Issues**: Set up issue templates in repository settings
3. **Setup Wiki**: Go to Settings → Features and enable Wiki
4. **Add Collaborators**: Go to Settings → Collaborators to invite team members
5. **Setup Releases**: Create releases page for easier package distribution

## Updating Your Repository

After deployment, to keep repository updated:

```bash
# Make changes locally
# ... edit files ...

# Commit and push
git add .
git commit -m "Your commit message"
git push origin main

# Create a new release (when ready)
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

## Security Best Practices

1. Never commit `.env` files with secrets
2. Use GitHub Secrets for sensitive configuration
3. Enable branch protection on `main` branch
4. Require pull request reviews before merging
5. Use security scanning (GitHub Advanced Security)

## Support

For GitHub-related questions:
- GitHub Documentation: https://docs.github.com
- GitHub Community: https://github.community

For AI Engine questions:
- See README.md and DEPLOYMENT.md in the repository
