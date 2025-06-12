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

echo -e "${BLUE}📊 Copying database file to VM...${NC}"

# Check if database file exists
if [ ! -f "compensation_rates.db" ]; then
    echo -e "${RED}❌ Database file 'compensation_rates.db' not found${NC}"
    exit 1
fi

# Show file size
db_size=$(du -h compensation_rates.db | cut -f1)
echo -e "${BLUE}Database file size: ${db_size}${NC}"

# Confirm before copying
read -p "This may take a while. Continue? (y/N): " continue_copy
if [[ ! $continue_copy =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Copy cancelled.${NC}"
    exit 0
fi

echo -e "${BLUE}📤 Starting database copy...${NC}"
echo -e "${YELLOW}⏳ This may take several minutes depending on file size and connection speed...${NC}"

# Use rsync for better reliability and progress
if command -v rsync &> /dev/null; then
    echo "Using rsync for reliable transfer..."
    rsync -avz --progress compensation_rates.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
else
    echo "Using scp..."
    scp -v compensation_rates.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database file copied successfully${NC}"
    
    # Verify the file on remote
    echo -e "${BLUE}🔍 Verifying file on remote server...${NC}"
    ssh $REMOTE_USER@$REMOTE_HOST "ls -lh $REMOTE_DIR/compensation_rates.db"
    
    echo -e "${GREEN}🎉 Database copy completed!${NC}"
else
    echo -e "${RED}❌ Database copy failed${NC}"
    echo -e "${BLUE}💡 You can try again or copy manually with:${NC}"
    echo "scp compensation_rates.db $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"
    exit 1
fi