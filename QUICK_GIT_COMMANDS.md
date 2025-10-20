# Quick Git Commands Reference

## Automated Scripts

### Windows
```bash
# Run the batch script
git_push.bat
```

### Linux/Mac
```bash
# Make script executable (first time only)
chmod +x git_push.sh

# Run the script
./git_push.sh
```

---

## Manual Git Commands

### First Time Setup (One-time only)

```bash
# Initialize git repository
git init

# Configure your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add remote repository
git remote add origin https://github.com/yourusername/ai-resume-ranker.git
```

### Regular Workflow

#### 1. Check Status
```bash
# See what files have changed
git status

# See detailed differences
git diff
```

#### 2. Stage Changes
```bash
# Add all changes
git add .

# Add specific file
git add filepath/filename.py

# Add specific folder
git add src/
```

#### 3. Commit Changes
```bash
# Commit with message
git commit -m "Your commit message here"

# Commit with detailed message
git commit -m "Short description" -m "Detailed explanation of changes"
```

#### 4. Push to Remote
```bash
# Push to main branch
git push origin main

# Push to master branch
git push origin master

# Push current branch
git push origin HEAD

# Force push (use with caution)
git push -f origin main
```

---

## Common Scenarios

### Scenario 1: First Push to New Repository

```bash
# Initialize and add remote
git init
git remote add origin https://github.com/yourusername/ai-resume-ranker.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Resume Ranker project"

# Push (creates main branch)
git push -u origin main
```

### Scenario 2: Regular Update

```bash
# Add all changes
git add .

# Commit with message
git commit -m "Add workflow documentation file"

# Push to remote
git push origin main
```

### Scenario 3: Update Specific Files

```bash
# Add specific files
git add WORKFLOW.md README.md

# Commit
git commit -m "Update documentation files"

# Push
git push origin main
```

### Scenario 4: Fix Last Commit Message

```bash
# Amend the last commit
git commit --amend -m "Corrected commit message"

# Force push (if already pushed)
git push -f origin main
```

### Scenario 5: Undo Changes

```bash
# Discard changes in working directory
git checkout -- filename.py

# Unstage file (keep changes)
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## Branch Management

### Create and Switch Branches

```bash
# Create new branch
git branch feature-branch

# Switch to branch
git checkout feature-branch

# Create and switch in one command
git checkout -b feature-branch

# List all branches
git branch -a
```

### Merge Branches

```bash
# Switch to main branch
git checkout main

# Merge feature branch into main
git merge feature-branch

# Push merged changes
git push origin main
```

### Delete Branches

```bash
# Delete local branch
git branch -d feature-branch

# Force delete local branch
git branch -D feature-branch

# Delete remote branch
git push origin --delete feature-branch
```

---

## Syncing with Remote

### Pull Changes

```bash
# Pull from main branch
git pull origin main

# Pull with rebase
git pull --rebase origin main
```

### Fetch Changes

```bash
# Fetch all branches
git fetch origin

# View fetched changes
git log origin/main
```

---

## Viewing History

```bash
# View commit history
git log

# View compact history
git log --oneline

# View history with graph
git log --oneline --graph --all

# View last 5 commits
git log -5

# View changes in specific commit
git show commit-hash
```

---

## Configuration

### View Configuration

```bash
# View all config
git config --list

# View specific config
git config user.name
git config user.email
```

### Update Configuration

```bash
# Set username
git config --global user.name "Your Name"

# Set email
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "code --wait"

# Set default branch name
git config --global init.defaultBranch main
```

---

## Troubleshooting

### Problem: Push Rejected

```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Problem: Merge Conflicts

```bash
# View conflicts
git status

# After resolving conflicts manually
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

### Problem: Committed Wrong Files

```bash
# Remove file from last commit
git reset HEAD~1 filename.py
git commit --amend

# Or reset and recommit
git reset --soft HEAD~1
# Edit files
git add corrected-files
git commit -m "Corrected commit"
```

---

## Best Practices

### Commit Messages

✅ **Good**:
```bash
git commit -m "Add workflow documentation file"
git commit -m "Fix: Resolve parsing error for PDF files"
git commit -m "Feature: Add CSV export functionality"
```

❌ **Bad**:
```bash
git commit -m "updates"
git commit -m "fix"
git commit -m "changes"
```

### Commit Frequency

- Commit often with logical changes
- Each commit should be a complete, working state
- Don't commit broken code to main branch

### Branch Naming

```bash
feature/add-export-function
bugfix/fix-pdf-parsing
hotfix/critical-security-update
docs/update-readme
```

---

## Quick Commands for This Project

### Add New Feature

```bash
git checkout -b feature/your-feature-name
# Make changes
git add .
git commit -m "Feature: Add your feature description"
git push origin feature/your-feature-name
```

### Update Documentation

```bash
git add README.md WORKFLOW.md
git commit -m "Docs: Update project documentation"
git push origin main
```

### Fix Bug

```bash
git checkout -b bugfix/issue-description
# Fix the bug
git add .
git commit -m "Fix: Resolve issue description"
git push origin bugfix/issue-description
```

### Release Version

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## GitHub Specific

### Clone Repository

```bash
git clone https://github.com/yourusername/ai-resume-ranker.git
cd ai-resume-ranker
```

### Fork Workflow

```bash
# Clone your fork
git clone https://github.com/yourname/ai-resume-ranker.git

# Add upstream remote
git remote add upstream https://github.com/original/ai-resume-ranker.git

# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main
```

### Create Pull Request

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push to your fork
git push origin feature/new-feature

# Then create PR on GitHub web interface
```

---

## Useful Aliases

Add to your `.gitconfig`:

```bash
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --all
```

Usage:
```bash
git st          # Instead of git status
git co main     # Instead of git checkout main
git visual      # Pretty log view
```
