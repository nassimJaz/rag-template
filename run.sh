#!/bin/bash

# Configuration
VENV_DIR="venv"
REQUIREMENTS="requirements.txt"
APP_SCRIPT="app_cli.py"

# --- Palette de Couleurs ---
GREEN='\033[0;32m'
B_GREEN='\033[1;32m'
BLUE='\033[0;34m'
B_BLUE='\033[1;34m'
RED='\033[0;31m'
B_RED='\033[1;31m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color (Reset)

# --- Entête ---
echo -e "${B_BLUE}=======================================${NC}"
echo -e "${B_BLUE}          RAG GÉNÉRAL CLI              ${NC}"
echo -e "${B_BLUE}=======================================${NC}"

# 1. Check/Create Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${CYAN}[1/4] Création de l'environnement virtuel...${NC}"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${B_RED}Erreur : Échec lors de la création de l'environnement virtuel.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✔ Environnement virtuel détecté.${NC}"
fi

# 2. Activate Virtual Environment & Docker
echo -e "${CYAN}[2/4] Activation des services...${NC}"
source "$VENV_DIR/bin/activate"

echo -e "${BLUE}  → Lancement de Qdrant (Docker)...${NC}"
docker compose up qdrant -d
if [ $? -eq 0 ]; then
    echo -e "${B_GREEN}✔ Base de données vectorielle Qdrant prête.${NC}"
else
    echo -e "${B_RED}✘ Erreur : Docker n'a pas pu lancer Qdrant.${NC}"
fi

# 3. Install/Update Dependencies
if [ -f "$REQUIREMENTS" ]; then
    echo -ne "${YELLOW}Veux-tu installer les dépendances python ? (y/N): ${NC}"
    read -r install_deps
    if [[ "$install_deps" =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}[3/4] Mise à jour de pip et installation...${NC}"
        pip install --upgrade pip
        pip install -r "$REQUIREMENTS"
    else
        echo -e "${BLUE}Skipping : Installation des dépendances ignorée.${NC}"
    fi
else
    echo -e "${B_RED}⚠ Avertissement : $REQUIREMENTS non trouvé.${NC}"
fi

# 4. Run the Application
echo -e "\n${B_GREEN}🚀 Mise en marche du RAG CLI...${NC}"
echo -e "${BLUE}(Tapez 'exit' pour quitter)${NC}"
echo -e "${B_BLUE}---------------------------------------${NC}"

python "$APP_SCRIPT"

# 5. Deactivate on exit
deactivate
echo -e "\n${B_BLUE}---------------------------------------${NC}"
echo -e "${YELLOW}Environnement désactivé. À bientôt !${NC}"