#!/bin/bash

# Git commit and push script for AI Resume Ranker

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AI Resume Ranker - Git Push Script ===${NC}\n"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Git repository not initialized. Initializing...${NC}"
    git init
    echo -e "${GREEN}Git repository initialized.${NC}\n"
fi

# Check git status
echo -e "${YELLOW}Checking git status...${NC}"
git status

# Add all changes
echo -e "\n${YELLOW}Adding all changes to staging area...${NC}"
git add .

# Show what will be committed
echo -e "\n${YELLOW}Files to be committed:${NC}"
git status --short

# Prompt for commit message
echo -e "\n${YELLOW}Enter commit message (or press Enter for default):${NC}"
read -r commit_message

# Use default message if empty
if [ -z "$commit_message" ]; then
    commit_message="Update AI Resume Ranker codebase with workflow documentation"
fi

# Commit changes
echo -e "\n${YELLOW}Committing changes...${NC}"
git commit -m "$commit_message"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Changes committed successfully!${NC}\n"
else
    echo -e "${RED}Commit failed. Please check for errors.${NC}"
    exit 1
fi

# Check if remote exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' exists.${NC}"
else
    echo -e "${YELLOW}No remote 'origin' found.${NC}"
    echo -e "${YELLOW}Enter remote repository URL (or press Enter to skip):${NC}"
    read -r remote_url
    
    if [ -n "$remote_url" ]; then
        git remote add origin "$remote_url"
        echo -e "${GREEN}Remote 'origin' added.${NC}\n"
    else
        echo -e "${YELLOW}Skipping remote setup. Run manually: git remote add origin <url>${NC}"
        exit 0
    fi
fi

# Get current branch name
current_branch=$(git branch --show-current)

# Push to remote
echo -e "${YELLOW}Pushing to remote repository (branch: $current_branch)...${NC}"
git push -u origin "$current_branch"

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}=== Successfully pushed to remote! ===${NC}"
else
    echo -e "\n${RED}Push failed. You may need to pull first or check your credentials.${NC}"
    echo -e "${YELLOW}Try: git pull origin $current_branch --rebase${NC}"
    exit 1
fi

echo -e "\n${GREEN}All done! ✓${NC}"
