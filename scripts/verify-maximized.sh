#!/bin/bash
# Verify OmniDrive Maximizado
# Checks all components: Shield, Skills, Electron, Twin

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 Verifying OmniDrive Maximizado...${NC}"
echo ""

PASS=0
FAIL=0

check() {
    local name="$1"
    local condition="$2"

    if eval "$condition" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} $name"
        ((PASS++))
    else
        echo -e "   ${RED}✗${NC} $name"
        ((FAIL++))
    fi
}

# 1. Shield (Frontier Integration)
echo -e "${BLUE}1. Shield Integration${NC}"
check "governance/__init__.py exists" "[ -f ~/Dev/omnidrive-cli/omnidrive/governance/__init__.py ]"
check "frontier_bridge.py exists" "[ -f ~/Dev/omnidrive-cli/omnidrive/governance/frontier_bridge.py ]"
check "decorators.py exists" "[ -f ~/Dev/omnidrive-cli/omnidrive/governance/decorators.py ]"
check "policies.json exists" "[ -f ~/Dev/omnidrive-cli/omnidrive/governance/policies.json ]"
echo ""

# 2. OmniDrive Skills
echo -e "${BLUE}2. OmniDrive Skills${NC}"
check "omnidrive-sync.skill.js" "[ -f ~/.openclaw/skills/omnidrive-sync.skill.js ]"
check "omnidrive-search.skill.js" "[ -f ~/.openclaw/skills/omnidrive-search.skill.js ]"
check "omnidrive-browse.skill.js" "[ -f ~/.openclaw/skills/omnidrive-browse.skill.js ]"
check "omnidrive-twin.skill.js" "[ -f ~/.openclaw/skills/omnidrive-twin.skill.js ]"
echo ""

# 3. Intents Registered
echo -e "${BLUE}3. OpenClaw Intents${NC}"
check "omnidrive_sync intent" "grep -q 'omnidrive_sync' ~/.openclaw/constitution/intents.json"
check "omnidrive_search intent" "grep -q 'omnidrive_search' ~/.openclaw/constitution/intents.json"
check "omnidrive_browse intent" "grep -q 'omnidrive_browse' ~/.openclaw/constitution/intents.json"
check "omnidrive_delegate intent" "grep -q 'omnidrive_delegate' ~/.openclaw/constitution/intents.json"
echo ""

# 4. Electron App
echo -e "${BLUE}4. Electron Desktop App${NC}"
check "omnidrive-desktop exists" "[ -d ~/Dev/omnidrive-cli/omnidrive-desktop ]"
check "package.json exists" "[ -f ~/Dev/omnidrive-cli/omnidrive-desktop/package.json ]"
check "electron/main.ts exists" "[ -f ~/Dev/omnidrive-cli/omnidrive-desktop/electron/main.ts ]"
check "electron/preload.ts exists" "[ -f ~/Dev/omnidrive-cli/omnidrive-desktop/electron/preload.ts ]"
check "src/App.tsx exists" "[ -f ~/Dev/omnidrive-cli/omnidrive-desktop/src/App.tsx ]"
check "node_modules installed" "[ -d ~/Dev/omnidrive-cli/omnidrive-desktop/node_modules ]"
echo ""

# 5. Twin Scripts
echo -e "${BLUE}5. Twin Flow Scripts${NC}"
check "sync-to-m1.sh exists" "[ -f ~/.openclaw/workspace/lady/clawd/.twin/omnidrive/sync-to-m1.sh ]"
check "delegate-task.sh exists" "[ -f ~/.openclaw/workspace/lady/clawd/.twin/omnidrive/delegate-task.sh ]"
check "collect-result.sh exists" "[ -f ~/.openclaw/workspace/lady/clawd/.twin/omnidrive/collect-result.sh ]"
echo ""

# 6. M1 Connectivity
echo -e "${BLUE}6. M1 Connectivity${NC}"
check "SSH to M1 works" "ssh -o BatchMode=yes -o ConnectTimeout=5 server 'echo ok'"
check "omnidrive-cli on M1" "ssh server '[ -d /Users/server/dev/omnidrive-cli ]'"
echo ""

# Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ OmniDrive Maximizado is fully operational!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some components need attention${NC}"
    exit 1
fi
