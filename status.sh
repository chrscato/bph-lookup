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

echo -e "${BLUE}📊 Checking BPH Lookup application status...${NC}"

ssh $REMOTE_USER@$REMOTE_HOST << 'EOF'
# Colors for remote output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REMOTE_DIR="/opt/bph_lookup"
SERVICE_NAME="bph_lookup"

echo -e "${BLUE}🖥️  System Information:${NC}"
echo "Hostname: $(hostname)"
echo "IP Address: $(curl -s ifconfig.me)"
echo "Uptime: $(uptime -p)"
echo "Disk Usage: $(df -h / | awk 'NR==2{printf "Used: %s/%s (%s)", $3,$2,$5}')"
echo ""

echo -e "${BLUE}📁 Project Directory:${NC}"
if [ -d "$REMOTE_DIR" ]; then
    echo -e "${GREEN}✅ Project directory exists: $REMOTE_DIR${NC}"
    cd $REMOTE_DIR
    
    # Git status
    if [ -d ".git" ]; then
        echo "Git branch: $(git branch --show-current)"
        echo "Last commit: $(git log -1 --format='%h - %s (%cr)')"
    fi
    
    # Virtual environment
    if [ -d "venv" ]; then
        echo -e "${GREEN}✅ Virtual environment exists${NC}"
    else
        echo -e "${RED}❌ Virtual environment missing${NC}"
    fi
    
    # Database
    if [ -f "compensation_rates.db" ]; then
        db_size=$(du -h compensation_rates.db | cut -f1)
        echo -e "${GREEN}✅ Database file exists (${db_size})${NC}"
    else
        echo -e "${YELLOW}⚠️  Database file not found${NC}"
    fi
    
    # Settings
    if [ -f "bph_lookup/bph_lookup/settings.py" ]; then
        echo -e "${GREEN}✅ Settings file exists${NC}"
    else
        echo -e "${RED}❌ Settings file missing${NC}"
    fi
    
    # Environment file
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ Environment file exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Environment file not found${NC}"
    fi
else
    echo -e "${RED}❌ Project directory not found: $REMOTE_DIR${NC}"
fi

echo ""

echo -e "${BLUE}🔧 Service Status:${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✅ Service is running${NC}"
    systemctl status $SERVICE_NAME --no-pager -l | head -15
else
    echo -e "${RED}❌ Service is not running${NC}"
    if systemctl list-unit-files | grep -q $SERVICE_NAME; then
        echo "Service exists but is stopped. Recent logs:"
        journalctl -u $SERVICE_NAME --no-pager -n 10
    else
        echo -e "${YELLOW}⚠️  Service file not found${NC}"
    fi
fi

echo ""

echo -e "${BLUE}🌐 Network Status:${NC}"
if netstat -tuln | grep -q ":8000 "; then
    echo -e "${GREEN}✅ Application is listening on port 8000${NC}"
    
    # Test HTTP response
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200"; then
        echo -e "${GREEN}✅ HTTP endpoint responding (200 OK)${NC}"
    else
        response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
        echo -e "${YELLOW}⚠️  HTTP endpoint responding with code: $response_code${NC}"
    fi
else
    echo -e "${RED}❌ No service listening on port 8000${NC}"
fi

echo ""

echo -e "${BLUE}📝 Recent Logs:${NC}"
if journalctl -u $SERVICE_NAME --no-pager -n 5 -q; then
    journalctl -u $SERVICE_NAME --no-pager -n 5
else
    echo "No recent logs available"
fi

echo ""
echo -e "${BLUE}🔗 Application URL: http://$(curl -s ifconfig.me):8000${NC}"
EOF