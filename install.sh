#!/usr/bin/env bash
# Universal Agent Skills & Brain - 1-Click Multi-Agent Installer for macOS/Linux
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
RULES_SRC="$SCRIPT_DIR/rules"
TARGET="${1:-antigravity}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "=========================================================="
echo "⚡ Universal Agent Skills & Autonomous Brain - Installer"
echo "=========================================================="
echo "[*] Source: $SCRIPT_DIR"
echo "[*] Target Mode: $TARGET"

if [ ! -d "$SKILLS_SRC" ]; then
    echo "Error: Source 'skills' directory not found at: $SKILLS_SRC"
    exit 1
fi

install_antigravity() {
    DEST_DIR="$HOME/.gemini/config/skills"
    echo -e "\n[*] Installing into Google Antigravity 2.0 ($HOME/.gemini)..."
    
    if [ -d "$DEST_DIR" ]; then
        BACKUP_DIR="$HOME/.gemini/config/skills_backup_$TIMESTAMP"
        echo "[*] Creating safety backup of existing skills at: $BACKUP_DIR"
        cp -r "$DEST_DIR" "$BACKUP_DIR"
    else
        mkdir -p "$DEST_DIR"
    fi

    cp -r "$SKILLS_SRC"/* "$DEST_DIR/"
    if [ -f "$RULES_SRC/GEMINI.md" ]; then
        cp "$RULES_SRC/GEMINI.md" "$HOME/.gemini/GEMINI.md"
    fi
    echo "[✓] 22 Skills & Rules successfully deployed to: $DEST_DIR"
}

install_cursor() {
    echo -e "\n[*] Installing into Cursor IDE project ($PWD)..."
    mkdir -p ".cursor/skills"
    cp -r "$SKILLS_SRC"/* ".cursor/skills/"
    cat << 'EOF' > .cursorrules
# Cursor Agent Directives (Universal Agent Skills)
- Always enforce high-density technical responses (Zero pleasantries, lead with verified results).
- Strict adherence to the 22 modular skills located in '.cursor/skills/'.
- Internal Rigor Invariant: All diagnostics follow 4-Stage Root-Cause (Symptom -> Root Cause -> Target State -> Action Plan).
- Single-Agent First: Default to single unified context for >=90% of tasks.
EOF
    echo "[✓] Cursor skills & .cursorrules configured successfully!"
}

install_claude() {
    echo -e "\n[*] Installing into Claude Code project ($PWD)..."
    mkdir -p ".claude/skills"
    cp -r "$SKILLS_SRC"/* ".claude/skills/"
    cat << 'EOF' > CLAUDE.md
# CLAUDE.md — Senior Agentic Engineering Directives
- Response Economy: Lead with verified facts in 1-2 lines. Eliminate AI writing tells.
- Ponytail Minimal-Change: Smallest complete diff, standard library over unneeded bloat.
- Skills Index: 22 production-grade skills available in '.claude/skills/'.
EOF
    echo "[✓] Claude Code skills & CLAUDE.md configured successfully!"
}

case "$TARGET" in
    antigravity) install_antigravity ;;
    cursor)      install_cursor ;;
    claude)      install_claude ;;
    all)
        install_antigravity
        install_cursor
        install_claude
        ;;
    *)
        echo "Usage: $0 [antigravity|cursor|claude|all]"
        exit 1
        ;;
esac

echo -e "\n=========================================================="
echo "🎉 Installation complete! Agent is ready for high-velocity engineering."
echo "=========================================================="
