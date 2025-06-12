#!/bin/bash

# === CONFIGURATION ===
REMOTE_USER="root"
REMOTE_HOST="159.223.104.254"
REMOTE_DIR="/opt/bph_lookup"
SERVICE_NAME="bph_lookup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting BPH Lookup deployment...${NC}"

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ Not in a git repository. Please run from project root.${NC}"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes:${NC}"
    git status --short
    read -p "Continue with deployment? (y/N): " continue_deploy
    if [[ ! $continue_deploy =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Deployment cancelled.${NC}"
        exit 0
    fi
fi

# Step 1: Copy non-git files (database, settings, etc.)
echo -e "${BLUE}📤 Copying non-git files to VM...${NC}"

# Copy database file if it exists
if [ -f "compensation_rates.db" ]; then
    echo "Copying database file..."
    scp compensation_rates.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
    check_status "Database file copied"
fi

# Copy settings file if it exists
if [ -f "bph_lookup/bph_lookup/settings.py" ]; then
    echo "Copying settings.py..."
    scp bph_lookup/bph_lookup/settings.py $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/bph_lookup/bph_lookup/
    check_status "Settings file copied"
fi

# Copy .env file if it exists
if [ -f ".env" ]; then
    echo "Copying .env file..."
    scp .env $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
    ssh $REMOTE_USER@$REMOTE_HOST "chmod 600 $REMOTE_DIR/.env"
    check_status "Environment file copied"
fi

# Step 2: Git push from local
echo -e "${BLUE}📤 Pushing to git repository...${NC}"
git add .
if [ -n "$(git diff --staged)" ]; then
    read -p "Enter commit message (or press Enter for default): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="Deploy $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    git commit -m "$commit_msg"
    check_status "Local commit created"
fi

git push origin master
check_status "Code pushed to repository"

# Step 3: Deploy on VM
echo -e "${BLUE}🔄 Deploying on VM...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST << 'EOF'
set -e

# Colors for remote output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REMOTE_DIR="/opt/bph_lookup"
SERVICE_NAME="bph_lookup"

cd $REMOTE_DIR

# Pull latest code
echo -e "${BLUE}📥 Pulling latest code...${NC}"
git pull origin master

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🐍 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Django setup
echo -e "${BLUE}🗃️  Running Django setup...${NC}"
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Check if service exists, if not create it
if [ ! -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    echo -e "${YELLOW}⚠️  Service file not found. Creating systemd service...${NC}"
    cat > /etc/systemd/system/${SERVICE_NAME}.service << 'SERVICE_EOF'
[Unit]
Description=BPH Lookup Django Application
After=network.target

[Service]
Type=exec
User=root
WorkingDirectory=/opt/bph_lookup
Environment=PATH=/opt/bph_lookup/venv/bin
EnvironmentFile=/opt/bph_lookup/.env
ExecStart=/opt/bph_lookup/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE_EOF
    
    systemctl daemon-reload
    systemctl enable ${SERVICE_NAME}
    echo -e "${GREEN}✅ Service created and enabled${NC}"
fi

# Restart service
echo -e "${BLUE}🔄 Restarting service...${NC}"
systemctl restart ${SERVICE_NAME}
systemctl status ${SERVICE_NAME} --no-pager

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${BLUE}🌐 Application should be running on: http://$(curl -s ifconfig.me):8000${NC}"
EOF

check_status "VM deployment completed"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Checking service status...${NC}"

# Show final status
ssh $REMOTE_USER@$REMOTE_HOST "systemctl status $SERVICE_NAME --no-pager | head -10"