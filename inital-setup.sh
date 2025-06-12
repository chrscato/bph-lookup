#!/bin/bash

# === CONFIGURATION ===
REMOTE_USER="root"
REMOTE_HOST="159.223.104.254"
REMOTE_DIR="/opt/bph_lookup"
REPO_URL="https://github.com/chrscato/bph-lookup.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Initial setup for BPH Lookup on VM...${NC}"

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

# Prompt for repository URL if not set
if [[ $REPO_URL == *"chrscato/bph-lookup"* ]]; then
    echo "Using repository: $REPO_URL"
else
    read -p "Enter your git repository URL: " input_repo
    if [ -n "$input_repo" ]; then
        REPO_URL="$input_repo"
    else
        echo -e "${RED}❌ Repository URL is required${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}📋 Setup Configuration:${NC}"
echo "Remote Host: $REMOTE_HOST"
echo "Remote Directory: $REMOTE_DIR" 
echo "Repository: $REPO_URL"
echo ""

read -p "Continue with setup? (y/N): " continue_setup
if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Setup cancelled.${NC}"
    exit 0
fi

# Initial VM setup
echo -e "${BLUE}🔧 Setting up VM environment...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST << EOF
set -e

# Colors for remote output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\${BLUE}📦 Installing minimal dependencies...\${NC}"

# Install only what we need
apt update
apt install -y python3 python3-pip python3-venv git

echo -e "\${GREEN}✅ Dependencies installed\${NC}"

# Create project directory and clone
echo -e "\${BLUE}📁 Setting up project...\${NC}"
mkdir -p $REMOTE_DIR
cd $REMOTE_DIR

if [ -d ".git" ]; then
    git pull origin master
else
    git clone $REPO_URL .
fi

# Quick Python setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Basic Django setup
if [ ! -f "bph_lookup/bph_lookup/settings.py" ]; then
    cp bph_lookup/bph_lookup/settings_template.py bph_lookup/bph_lookup/settings.py
fi

echo -e "\${GREEN}🎉 Basic setup completed!\${NC}"
EOF

check_status "VM setup completed"

# Copy initial files if they exist
echo -e "${BLUE}📤 Copying initial files...${NC}"

# Copy database if it exists
if [ -f "compensation_rates.db" ]; then
    echo "Copying database file..."
    scp compensation_rates.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
    check_status "Database file copied"
fi

# Copy .env if it exists
if [ -f ".env" ]; then
    echo "Copying .env file..."
    scp .env $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
    ssh $REMOTE_USER@$REMOTE_HOST "chmod 600 $REMOTE_DIR/.env"
    check_status "Environment file copied"
else
    echo -e "${YELLOW}⚠️  No .env file found. You may need to create one on the VM.${NC}"
fi

echo -e "${GREEN}🎉 Basic setup completed!${NC}"
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Run ./setup-env.sh to configure environment"
echo "2. Run ./deploy.sh to start the application"