#!/bin/bash
# Setup script for Telegram Learning Bot
# Run this after cloning the repository

set -e  # Exit on error

echo "======================================"
echo "Telegram Learning Bot - Setup Script"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create logs directory
echo ""
echo "Creating logs directory..."
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Check if .env exists
echo ""
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env and add your TELEGRAM_BOT_TOKEN${NC}"
    echo -e "${YELLOW}   Run: nano .env${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# Check if TELEGRAM_BOT_TOKEN is set
if grep -q "TELEGRAM_BOT_TOKEN=.*[0-9]" .env; then
    echo -e "${GREEN}✓ TELEGRAM_BOT_TOKEN is configured${NC}"
else
    echo -e "${RED}✗ TELEGRAM_BOT_TOKEN not configured in .env${NC}"
    echo ""
    echo "Please:"
    echo "1. Create a bot with @BotFather on Telegram"
    echo "2. Get the bot token"
    echo "3. Edit .env and set TELEGRAM_BOT_TOKEN"
    echo ""
    read -p "Press Enter to edit .env now, or Ctrl+C to exit: "
    ${EDITOR:-nano} .env
fi

# Seed database with topics
echo ""
echo "Seeding database with topics..."
python scripts/seed_topics.py
SEED_RESULT=$?

if [ $SEED_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Topics seeded successfully${NC}"
else
    echo -e "${RED}✗ Topic seeding failed${NC}"
    exit 1
fi

# Run diagnostics
echo ""
echo "Running diagnostics..."
python scripts/diagnose_database.py
DIAG_RESULT=$?

# Summary
echo ""
echo "======================================"
if [ $DIAG_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "To start the bot:"
    echo "  source venv/bin/activate"
    echo "  python main.py"
    echo ""
    echo "Test in Telegram:"
    echo "  1. Find your bot"
    echo "  2. Send /start"
    echo "  3. Send /topics (should show 2 topics)"
else
    echo -e "${RED}✗ Setup incomplete${NC}"
    echo ""
    echo "Please check the errors above and:"
    echo "  1. Verify your .env configuration"
    echo "  2. Run: python scripts/diagnose_database.py"
    echo "  3. Check logs for errors"
fi
echo "======================================"
