#!/bin/bash

# Check if a commit message was provided
if [ -z "$1" ]; then
    echo "Error: Please provide a commit message"
    echo "Usage: ./git-push.sh \"Your commit message\""
    exit 1
fi

# Store the commit message
commit_message="$1"

# Add all changes
echo "Adding changes..."
git add .

# Commit with the provided message
echo "Committing changes with message: $commit_message"
git commit -m "$commit_message"

# Push to origin master
echo "Pushing to origin master..."
git push origin master

# Check if push was successful
if [ $? -eq 0 ]; then
    echo "Successfully pushed changes to origin master"
else
    echo "Error: Failed to push changes"
    exit 1
fi 