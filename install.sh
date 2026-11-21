#!/usr/bin/env bash
# =============================================================================
#  BILLING & INVENTORY SOFTWARE — INSTALLER
#  PC (Linux/Mac):     bash <(curl -fsSL https://raw.githubusercontent.com/djkalirdp/billpro-official/main/install.sh)
#  Termux (Android):   curl -fsSL https://raw.githubusercontent.com/djkalirdp/billpro-official/main/install.sh -o install.sh && bash install.sh
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✔${NC}  $1"; }
info() { echo -e "  ${CYAN}→${NC}  $1"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  $1"; }
step() { echo -e "\n${BOLD}${BLUE}▶  $1${NC}"; }

clear
echo ""
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║        BILLING & INVENTORY SOFTWARE — INSTALLER              ║${NC}"
echo -e "${BLUE}${BOLD}║        Flask + SQLite + ReportLab + GST Reports              ║${NC}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1 — DETECT ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────
step "Detecting environment..."

IS_TERMUX=false
IS_LINUX=false
IS_MAC=false
PKG=""

if [[ -n "$TERMUX_VERSION" ]] || [[ -d "/data/data/com.termux" ]] || [[ "$PREFIX" == *"com.termux"* ]]; then
    IS_TERMUX=true
    ok "Termux (Android) detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    IS_MAC=true
    ok "macOS detected"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IS_LINUX=true
    if   command -v apt-get &>/dev/null; then PKG="apt"
    elif command -v dnf     &>/dev/null; then PKG="dnf"
    elif command -v pacman  &>/dev/null; then PKG="pacman"
    else PKG="unknown"; fi
    ok "Linux detected (package manager: $PKG)"
else
    warn "Unknown OS — proceeding anyway"
fi

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2 — INSTALL SYSTEM DEPENDENCIES
# ─────────────────────────────────────────────────────────────────────────────
step "Installing system dependencies..."

if [[ "$IS_TERMUX" == true ]]; then
    info "Updating Termux packages..."
    pkg update -y 2>/dev/null || true
    info "Installing Python, git, curl..."
    pkg install -y python git curl 2>/dev/null && ok "Termux packages installed" || warn "Some failed — continuing"
    pkg install -y ca-certificates 2>/dev/null || true

elif [[ "$IS_LINUX" == true ]]; then
    if [[ "$PKG" == "apt" ]]; then
        sudo apt-get update -qq 2>/dev/null || warn "apt update failed"
        sudo apt-get install -y -qq python3-pip python3-venv fonts-dejavu-core curl git 2>/dev/null || true
    elif [[ "$PKG" == "dnf" ]]; then
        sudo dnf install -y python3-pip python3-virtualenv dejavu-sans-fonts curl git 2>/dev/null || true
    elif [[ "$PKG" == "pacman" ]]; then
        sudo pacman -Sy --noconfirm python-pip python-virtualenv ttf-dejavu curl git 2>/dev/null || true
    fi
    ok "System packages done"

elif [[ "$IS_MAC" == true ]]; then
    command -v brew &>/dev/null && brew install python3 git 2>/dev/null || true
    ok "Mac packages done"
fi

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3 — CHECK PYTHON
# ─────────────────────────────────────────────────────────────────────────────
step "Checking Python..."

PYTHON=""
for cmd in python3 python3.12 python3.11 python3.10 python3.9 python3.8 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 8 ]]; then
            PYTHON="$cmd"
            ok "Found $cmd (version $VER)"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    echo -e "${RED}  Python 3.8+ not found!${NC}"
    [[ "$IS_TERMUX" == true ]] && echo "  Run: pkg install python"
    [[ "$IS_LINUX"  == true ]] && echo "  Run: sudo apt install python3"
    [[ "$IS_MAC"    == true ]] && echo "  Download: https://www.python.org/downloads/"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4 — CLONE REPO
# ─────────────────────────────────────────────────────────────────────────────
step "Downloading from GitHub..."

REPO_URL="https://github.com/djkalirdp/billpro-official.git"
REPO_RAW="https://raw.githubusercontent.com/djkalirdp/billpro-official/main"
INSTALL_TARGET="billing-app"

if command -v git &>/dev/null; then
    if [[ -d "$INSTALL_TARGET/.git" ]]; then
        info "Already cloned — pulling latest..."
        cd "$INSTALL_TARGET" && git pull --quiet && cd ..
    elif [[ -d "$INSTALL_TARGET" ]]; then
        info "billing-app folder exists — skipping clone"
    else
        info "Cloning from GitHub..."
        git clone "$REPO_URL" "$INSTALL_TARGET"
        ok "Repo cloned"
    fi
else
    warn "git not found — downloading via curl..."
    mkdir -p "$INSTALL_TARGET"
    for f in app.py database_manager.py pdf_generator.py pdf_generator_v2.py reports_generator.py; do
        info "Downloading $f..."
        curl -fsSL "$REPO_RAW/$f" -o "$INSTALL_TARGET/$f" 2>/dev/null || warn "$f failed"
    done
fi

cd "$INSTALL_TARGET"
mkdir -p data backups invoices reports static/uploads templates/mobile
ok "Directories ready"

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 5 — VIRTUAL ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────
step "Setting up Python environment..."

USE_VENV=true

if [[ "$IS_TERMUX" == true ]]; then
    if [[ -d "venv" ]]; then
        warn "venv exists — reusing"
    else
        # --system-site-packages: pkg se install hue Pillow etc. venv mein accessible honge
        $PYTHON -m venv venv --system-site-packages 2>/dev/null || USE_VENV=false
        [[ "$USE_VENV" == true ]] && ok "Virtual environment created (system-site-packages)" || warn "venv failed — using system Python"
    fi
else
    if [[ -d "venv" ]]; then
        warn "venv exists — reusing"
    else
        $PYTHON -m venv venv 2>/dev/null || {
            pip3 install virtualenv 2>/dev/null
            $PYTHON -m virtualenv venv
        }
        ok "Virtual environment created"
    fi
fi

if [[ "$USE_VENV" == true ]] && [[ -d "venv" ]]; then
    VENV_PY="venv/bin/python"
    VENV_PIP="venv/bin/pip"
else
    VENV_PY="$PYTHON"
    VENV_PIP="pip3"
fi

info "Upgrading pip..."
"$VENV_PIP" install --upgrade pip --quiet 2>/dev/null || true
ok "pip ready"

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 6 — INSTALL PACKAGES
# ─────────────────────────────────────────────────────────────────────────────
step "Installing Python packages..."
echo ""

if [[ "$IS_TERMUX" == true ]]; then
    # Step 1: pkg se pre-built Python packages install karo (no compilation needed)
    info "Termux pre-built packages install ho rahi hain..."
    pkg install -y python-pillow 2>/dev/null && ok "Pillow (pkg) installed" || warn "Pillow pkg failed"
    pkg install -y libjpeg-turbo libpng 2>/dev/null || true

    # Step 2: pip se baaki packages — reportlab ko no-deps se install karo
    # taaki woh Pillow source build karne ki koshish na kare
    PACKAGES=("flask" "werkzeug" "openpyxl" "num2words" "qrcode" "charset-normalizer")
    for pkg in "${PACKAGES[@]}"; do
        printf "  ${CYAN}→${NC}  Installing %-22s" "$pkg..."
        if "$VENV_PIP" install "$pkg" --quiet 2>/dev/null; then
            echo -e " ${GREEN}✔${NC}"
        else
            echo -e " ${YELLOW}⚠ warning${NC}"
        fi
    done

    # reportlab — install karo without Pillow dependency (Pillow already in system)
    printf "  ${CYAN}→${NC}  Installing %-22s" "reportlab..."
    if "$VENV_PIP" install reportlab --no-deps --quiet 2>/dev/null; then
        echo -e " ${GREEN}✔${NC}"
    elif "$VENV_PIP" install reportlab --quiet 2>/dev/null; then
        echo -e " ${GREEN}✔${NC}"
    else
        echo -e " ${YELLOW}⚠ warning${NC}"
    fi

else
    PACKAGES=("flask" "werkzeug" "reportlab" "openpyxl" "num2words" "qrcode[pil]" "Pillow")
    for pkg in "${PACKAGES[@]}"; do
        printf "  ${CYAN}→${NC}  Installing %-22s" "$pkg..."
        if "$VENV_PIP" install "$pkg" --quiet 2>/dev/null; then
            echo -e " ${GREEN}✔${NC}"
        else
            echo -e " ${YELLOW}⚠ warning${NC}"
        fi
    done
fi

ok "Packages done"

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 7 — FONTS (₹ symbol)
# ─────────────────────────────────────────────────────────────────────────────
step "Setting up fonts..."

FONT_COPIED=false

if [[ "$IS_TERMUX" == true ]]; then
    # Install dejavu via pkg
    pkg install -y ttf-dejavu 2>/dev/null || true

    # Termux font locations — check all possible paths
    FONT_DIRS=(
        "$PREFIX/share/fonts/truetype/dejavu"
        "$PREFIX/share/fonts/TTF"
        "$PREFIX/share/fonts/dejavu"
        "$HOME/.termux/font"
        "$HOME/.fonts"
    )

    for dir in "${FONT_DIRS[@]}"; do
        if [[ -f "$dir/DejaVuSans.ttf" ]]; then
            cp "$dir/DejaVuSans.ttf"      . 2>/dev/null
            cp "$dir/DejaVuSans-Bold.ttf" . 2>/dev/null || true
            ok "Fonts copied from $dir"
            FONT_COPIED=true
            break
        fi
    done

    # Search more broadly in PREFIX
    if [[ "$FONT_COPIED" == false ]]; then
        FOUND=$(find "$PREFIX/share/fonts" -name "DejaVuSans.ttf" 2>/dev/null | head -1)
        if [[ -n "$FOUND" ]]; then
            cp "$FOUND" . 2>/dev/null
            BOLD_DIR=$(dirname "$FOUND")
            cp "$BOLD_DIR/DejaVuSans-Bold.ttf" . 2>/dev/null || true
            ok "Fonts found and copied: $FOUND"
            FONT_COPIED=true
        fi
    fi
else
    for dir in "/usr/share/fonts/truetype/dejavu" "/usr/share/fonts/dejavu" "/Library/Fonts"; do
        if [[ -f "$dir/DejaVuSans.ttf" ]]; then
            cp "$dir/DejaVuSans.ttf" . 2>/dev/null
            cp "$dir/DejaVuSans-Bold.ttf" . 2>/dev/null
            ok "Fonts copied" && FONT_COPIED=true && break
        fi
    done
fi

if [[ "$FONT_COPIED" == false ]]; then
    info "Downloading fonts from GitHub..."
    BASE="https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf"
    curl -fsSL "$BASE/DejaVuSans.ttf"      -o DejaVuSans.ttf      2>/dev/null && \
    curl -fsSL "$BASE/DejaVuSans-Bold.ttf" -o DejaVuSans-Bold.ttf 2>/dev/null && \
    ok "Fonts downloaded" || warn "Fonts nahi mili — PDF mein Rs. dikhega"
fi

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 8 — CREATE START SCRIPT
# ─────────────────────────────────────────────────────────────────────────────
step "Creating start.sh..."

if [[ "$IS_TERMUX" == true ]]; then
cat > start.sh << 'STARTEOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
[[ -f "venv/bin/activate" ]] && source venv/bin/activate

echo ""
echo "  ┌──────────────────────────────────────────────────────┐"
echo "  │  BILLING SOFTWARE — Android (Termux)                 │"
echo "  │  Browser mein kholo: http://localhost:5000           │"
echo "  │  Ya: http://127.0.0.1:5000                          │"
echo "  │  Band karne ke liye: Ctrl+C dabao                    │"
echo "  └──────────────────────────────────────────────────────┘"
echo ""

# Android browser mein open karne ki koshish
termux-open-url "http://localhost:5000" 2>/dev/null || \
am start -a android.intent.action.VIEW -d "http://localhost:5000" 2>/dev/null || \
echo "  Browser mein manually kholo: http://127.0.0.1:5000"

python app.py
STARTEOF

else
cat > start.sh << 'STARTEOF'
#!/usr/bin/env bash
cd "$(dirname "$0")"
[[ -f "venv/bin/activate" ]] && source venv/bin/activate

echo ""
echo "  ┌─────────────────────────────────────────────────────┐"
echo "  │  BILLING SOFTWARE — Starting...                     │"
echo "  │  Browser: http://localhost:5000                     │"
echo "  │  Login: admin / admin123                            │"
echo "  │  Stop: Ctrl+C                                       │"
echo "  └─────────────────────────────────────────────────────┘"
echo ""
python app.py
STARTEOF
fi

chmod +x start.sh
ok "start.sh ready"

# ─────────────────────────────────────────────────────────────────────────────
#  STEP 9 — VERIFY
# ─────────────────────────────────────────────────────────────────────────────
step "Verifying..."

"$VENV_PY" - << 'PYTEST'
import sys
results = {}
def test(name, code):
    try: exec(code); results[name] = True
    except Exception as e: results[name] = str(e)

test("Flask",     "import flask")
test("ReportLab", "from reportlab.platypus import SimpleDocTemplate")
test("openpyxl",  "import openpyxl")
test("num2words", "from num2words import num2words")
test("Werkzeug",  "from werkzeug.security import generate_password_hash")
test("Pillow",    "from PIL import Image")
test("QR Code",   "import qrcode")

for pkg, res in results.items():
    icon = "\033[32m✔\033[0m" if res is True else "\033[33m⚠\033[0m"
    note = "" if res is True else f" — {res}"
    print(f"  {icon}  {pkg}{note}")
PYTEST

# ─────────────────────────────────────────────────────────────────────────────
#  DONE
# ─────────────────────────────────────────────────────────────────────────────
LOCAL_IP=""
if [[ "$IS_TERMUX" == true ]]; then
    LOCAL_IP=$(ip addr show wlan0 2>/dev/null | grep 'inet ' | awk '{print $2}' | cut -d/ -f1 | head -1)
else
    LOCAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}') || true
fi

echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║          INSTALLATION COMPLETE!                              ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$IS_TERMUX" == true ]]; then
    echo -e "  ${BOLD}App start karo:${NC}"
    echo -e "  ${CYAN}  bash start.sh${NC}"
    echo ""
    echo -e "  ${BOLD}Browser mein kholo:${NC}"
    echo -e "  ${CYAN}  http://localhost:5000${NC}"
    echo -e "  ${CYAN}  http://127.0.0.1:5000${NC}"
    [[ -n "$LOCAL_IP" ]] && echo -e "\n  ${BOLD}PC se access (same WiFi):${NC}\n  ${CYAN}  http://${LOCAL_IP}:5000${NC}"
    echo ""
    echo -e "  ${YELLOW}  TIP: Ek Termux session mein app chalao${NC}"
    echo -e "  ${YELLOW}       Doosre session ya browser mein open karo${NC}"
else
    echo -e "  ${BOLD}Start:${NC}  ${CYAN}bash start.sh${NC}"
    echo -e "  ${BOLD}Browser:${NC} ${CYAN}http://localhost:5000${NC}"
    [[ -n "$LOCAL_IP" ]] && echo -e "  ${BOLD}Mobile:${NC}  ${CYAN}http://${LOCAL_IP}:5000${NC}"
fi

echo ""
echo -e "  ${BOLD}Login:${NC}  admin / admin123"
echo -e "  ${YELLOW}  ⚠  Pehli baar login ke baad password zaroor badlo!${NC}"
echo ""

set +e
read -p "  App abhi start karu? (y/N): " START_NOW
if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    echo ""
    [[ -f "venv/bin/activate" ]] && source venv/bin/activate
    echo -e "  ${GREEN}Starting... Browser mein kholo: http://localhost:5000${NC}"
    echo ""
    python app.py
fi
