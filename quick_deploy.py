#!/usr/bin/env python3
"""
Quick Git Setup and Deployment Script for AI Engine

This script simplifies the GitHub deployment process by automating git setup.
Run this from the ai-engine directory.

Usage:
    python quick_deploy.py
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a shell command and handle errors."""
    if description:
        print(f"\n▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"✗ Error: {result.stderr}")
            return False
        if result.stdout:
            print(result.stdout.strip())
        return True
    except Exception as e:
        print(f"✗ Error executing command: {e}")
        return False


def check_git_installed():
    """Check if git is installed."""
    result = subprocess.run("git --version", shell=True, capture_output=True, text=True)
    return result.returncode == 0


def main():
    """Main deployment script."""
    print("=" * 60)
    print("NyxOS AI Engine - GitHub Deployment Setup")
    print("=" * 60)
    
    # Check git
    print("\n📋 Checking prerequisites...")
    if not check_git_installed():
        print("✗ Git is not installed!")
        print("\nInstall Git from: https://git-scm.com/download/win")
        print("Or use: winget install Git.Git")
        return 1
    
    print("✓ Git is installed")
    
    # Check if in correct directory
    if not os.path.exists("requirements.txt") or not os.path.exists("api"):
        print("✗ Please run this script from the ai-engine directory")
        return 1
    
    print("✓ Running from ai-engine directory")
    
    # Check git status
    is_git_repo = os.path.exists(".git")
    if is_git_repo:
        print("✓ Git repository already initialized")
    else:
        print("○ Git repository not yet initialized")
    
    # Git setup
    print("\n📝 Git Configuration")
    
    if not is_git_repo:
        if not run_command("git init", "Initializing git repository"):
            return 1
        print("✓ Git repository initialized")
        
        if not run_command("git add .", "Adding files to git"):
            return 1
        print("✓ Files added")
        
        if not run_command("git commit -m \"Initial commit: NyxOS AI Engine\"", "Creating initial commit"):
            return 1
        print("✓ Initial commit created")
    
    # Get repository URL
    print("\n🔗 Remote Repository Setup")
    print("\nTo deploy to GitHub, you need:")
    print("1. A GitHub account (https://github.com/signup)")
    print("2. Create a new repository at https://github.com/new")
    print("   - Name: nyxos-ai-engine")
    print("   - DO NOT initialize with README")
    print("3. Copy the repository URL (https://github.com/YOUR_USERNAME/nyxos-ai-engine.git)")
    
    github_url = input("\nEnter your GitHub repository URL (or press Enter to skip): ").strip()
    
    if not github_url:
        print("\n⚠ Skipping remote setup")
        print("\nTo complete deployment later, run:")
        print("  git remote add origin <YOUR_GITHUB_URL>")
        print("  git branch -M main")
        print("  git push -u origin main")
        return 0
    
    if not github_url.startswith(("https://", "git@")):
        print("✗ Invalid GitHub URL")
        return 1
    
    # Add remote
    run_command("git remote remove origin", "Removing existing remote (if any)")
    
    if not run_command(f"git remote add origin {github_url}", "Adding GitHub remote"):
        return 1
    print("✓ Remote repository configured")
    
    if not run_command("git branch -M main", "Renaming branch to main"):
        return 1
    print("✓ Branch renamed to main")
    
    # Push to GitHub
    print("\n⬆ Pushing to GitHub...")
    print("(You may be prompted for credentials)")
    print("(Use your GitHub token, not your password)")
    
    if not run_command("git push -u origin main", "Pushing to GitHub"):
        print("\n✗ Push failed. Troubleshooting:")
        print("  1. Verify GitHub URL is correct")
        print("  2. Check you have push access to the repository")
        print("  3. Ensure you're using a GitHub token for authentication")
        print("     Get token: https://github.com/settings/tokens")
        return 1
    
    print("✓ Code pushed to GitHub")
    
    # Success
    print("\n" + "=" * 60)
    print("✓ Deployment Complete!")
    print("=" * 60)
    print(f"\nRepository: {github_url}")
    print(f"View at: {github_url.replace('.git', '')}")
    print("\nNext steps:")
    print("  1. Visit your repository on GitHub")
    print("  2. Check 'Actions' tab for workflow status")
    print("  3. Setup PyPI token for automatic publishing (optional)")
    print("  4. Create releases using: git tag v1.0.0 && git push origin v1.0.0")
    print("\nDocumentation: See GITHUB_DEPLOYMENT.md for more details")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
