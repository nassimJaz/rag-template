#!/bin/bash

# Configuration
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
APP_SCRIPT="app_cli.py"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RAG CLI Starter ===${NC}"

# 1. Check/Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# 2. Activate Virtual Environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# 3. Install/Update Dependencies
if [ -f "$REQUIREMENTS" ]; then
    read -p "Do you want to install/update dependencies? (y/N): " install_deps
    if [[ "$install_deps" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Checking/Installing dependencies...${NC}"
        pip install --upgrade pip
        pip install -r "$REQUIREMENTS"
    else
        echo -e "${BLUE}Skipping dependency installation.${NC}"
    fi
else
    echo "Warning: $REQUIREMENTS not found. Skipping installation."
fi

# 4. Run the Application
echo -e "${GREEN}Starting RAG CLI...${NC}"
echo -e "${BLUE}(Type 'exit' to quit)${NC}"
python "$APP_SCRIPT"

# 5. Deactivate on exit
deactivate
