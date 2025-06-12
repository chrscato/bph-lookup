#!/bin/bash

# === CONFIGURATION ===
REMOTE_USER="root"
REMOTE_HOST="159.223.104.254"
REMOTE_DIR="/opt/bph_lookup"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Setting up environment variables on VM...${NC}"

# Check if local .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found locally.${NC}"
    echo -e "${BLUE}Creating a template .env file...${NC}"
    
    cat > .env << 'ENV_EOF'
# Django Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=159.223.104.254,localhost,127.0.0.1

# Database Configuration (if using PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost:5432/bph_lookup

# Email Configuration (optional)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Additional settings
TIME_ZONE=America/New_York
LANGUAGE_CODE=en-us
ENV_EOF
    
    echo -e "${GREEN}✅ Template .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual values before deploying${NC}"
    
    # Ask if they want to edit it now
    read -p "Do you want to edit the .env file now? (y/N): " edit_env
    if [[ $edit_env =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        elif command -v code &> /dev/null; then
            code .env
        else
            echo -e "${YELLOW}Please edit .env manually with your preferred editor${NC}"
        fi
    fi
fi

echo -e "${BLUE}📤 Copying .env file to VM...${NC}"
scp .env $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/.env

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ .env file copied successfully${NC}"
else
    echo -e "${RED}❌ Failed to copy .env file${NC}"
    exit 1
fi

echo -e "${BLUE}🔒 Setting proper permissions on .env file...${NC}"
ssh $REMOTE_USER@$REMOTE_HOST "chmod 600 $REMOTE_DIR/.env"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Permissions set correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Could not set permissions on .env file${NC}"
fi

echo -e "${GREEN}✅ Environment variables configured on VM${NC}"

# Optionally, restart the service to pick up new environment variables
read -p "🔄 Restart the service to apply new environment variables? (y/N): " restart_service
if [[ $restart_service =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🔄 Restarting service...${NC}"
    ssh $REMOTE_USER@$REMOTE_HOST "systemctl restart bph_lookup"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Service restarted successfully${NC}"
        
        # Check service status
        echo -e "${BLUE}📊 Checking service status...${NC}"
        ssh $REMOTE_USER@$REMOTE_HOST "systemctl status bph_lookup --no-pager | head -10"
    else
        echo -e "${RED}❌ Failed to restart service${NC}"
    fi
fi

echo -e "${BLUE}🎉 Environment setup completed!${NC}"