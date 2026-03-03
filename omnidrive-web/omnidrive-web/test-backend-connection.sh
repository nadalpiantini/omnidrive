#!/bin/bash
#############################################################################
# test-backend-connection.sh - Test Backend Connectivity
#
# Usage:
#   ./test-backend-connection.sh <RAILWAY_URL>
#
# Example:
#   ./test-backend-connection.sh https://omnidrive-api.up.railway.app
#############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log_test() { echo -e "${BLUE}🔍 Test: $1${NC}"; }
log_pass() { echo -e "${GREEN}✅ PASS: $1${NC}"; }
log_fail() { echo -e "${RED}❌ FAIL: $1${NC}"; }
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }

# Get Railway URL from argument or env
BACKEND_URL=${1:-$(grep NEXT_PUBLIC_API_URL .env.production 2>/dev/null | cut -d'=' -f2)}

if [ -z "$BACKEND_URL" ]; then
    log_fail "Backend URL not provided!"
    echo ""
    echo "Usage: $0 <RAILWAY_URL>"
    echo ""
    echo "Example:"
    echo "  $0 https://omnidrive-api.up.railway.app"
    exit 1
fi

# Remove trailing slash
BACKEND_URL=${BACKEND_URL%/}

echo ""
echo "=========================================="
echo "  OmniDrive Backend Connection Test"
echo "=========================================="
echo ""
echo "Testing: $BACKEND_URL"
echo ""

# Test counters
PASS=0
FAIL=0

#############################################################################
# Test 1: Health Check
#############################################################################
log_test "Health Endpoint"
HEALTH_URL="$BACKEND_URL/health"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_URL" 2>/dev/null)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    log_pass "Health check returned 200"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    ((PASS++))
else
    log_fail "Health check failed (HTTP $HTTP_CODE)"
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 2: Root Endpoint
#############################################################################
log_test "Root API Endpoint"
ROOT_URL="$BACKEND_URL/"
ROOT_RESPONSE=$(curl -s -w "\n%{http_code}" "$ROOT_URL" 2>/dev/null)
HTTP_CODE=$(echo "$ROOT_RESPONSE" | tail -n1)
BODY=$(echo "$ROOT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    log_pass "Root endpoint returned 200"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    ((PASS++))
else
    log_fail "Root endpoint failed (HTTP $HTTP_CODE)"
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 3: API Docs
#############################################################################
log_test "API Documentation"
DOCS_URL="$BACKEND_URL/docs"
if curl -s -f "$DOCS_URL" > /dev/null 2>&1; then
    log_pass "API docs accessible at $DOCS_URL"
    ((PASS++))
else
    log_fail "API docs not accessible"
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 4: CORS Preflight
#############################################################################
log_test "CORS Preflight Request"
CORS_RESPONSE=$(curl -s -X OPTIONS "$BACKEND_URL/api/v1/auth/status" \
    -H "Origin: https://omnidrive.sujeto10.com" \
    -H "Access-Control-Request-Method: GET" \
    -I 2>/dev/null)

if echo "$CORS_RESPONSE" | grep -qi "access-control-allow"; then
    log_pass "CORS headers present"
    echo "$CORS_RESPONSE" | grep -i "access-control" | head -3
    ((PASS++))
else
    log_fail "CORS headers not found"
    echo "$CORS_RESPONSE" | head -5
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 5: Auth Status Endpoint
#############################################################################
log_test "Auth Status Endpoint"
AUTH_URL="$BACKEND_URL/api/v1/auth/status"
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$AUTH_URL" 2>/dev/null)
HTTP_CODE=$(echo "$AUTH_RESPONSE" | tail -n1)
BODY=$(echo "$AUTH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    log_pass "Auth status returned 200"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    ((PASS++))
else
    log_fail "Auth status failed (HTTP $HTTP_CODE)"
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 6: Response Time
#############################################################################
log_test "API Response Time"
START=$(date +%s%N)
curl -s "$BACKEND_URL/health" > /dev/null 2>&1
END=$(date +%s%N)
DURATION=$(( (END - START) / 1000000 ))  # Convert to milliseconds

if [ $DURATION -lt 1000 ]; then
    log_pass "Response time: ${DURATION}ms (good)"
    ((PASS++))
elif [ $DURATION -lt 2000 ]; then
    log_info "Response time: ${DURATION}ms (acceptable)"
    ((PASS++))
else
    log_fail "Response time: ${DURATION}ms (slow)"
    ((FAIL++))
fi
echo ""

#############################################################################
# Test 7: File Listing Endpoint (Will fail without auth, but should return JSON)
#############################################################################
log_test "File Listing Endpoint (Unauthenticated)"
FILES_URL="$BACKEND_URL/api/v1/files/?service=google_drive&limit=10"
FILES_RESPONSE=$(curl -s -w "\n%{http_code}" "$FILES_URL" 2>/dev/null)
HTTP_CODE=$(echo "$FILES_RESPONSE" | tail -n1)
BODY=$(echo "$FILES_RESPONSE" | sed '$d')

# Accept 200, 401 (unauthorized), or 422 (validation error) as valid API responses
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "422" ]; then
    log_pass "Files endpoint responded (HTTP $HTTP_CODE)"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
    ((PASS++))
else
    log_fail "Files endpoint unexpected response (HTTP $HTTP_CODE)"
    ((FAIL++))
fi
echo ""

#############################################################################
# Summary
#############################################################################
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    log_pass "All tests passed! Backend is ready for integration."
    echo ""
    echo "Next steps:"
    echo "  1. Update Vercel environment variable: NEXT_PUBLIC_API_URL=$BACKEND_URL"
    echo "  2. Deploy to Vercel: vercel --prod"
    echo "  3. Test in production: https://omnidrive.sujeto10.com"
    exit 0
else
    log_fail "Some tests failed. Please review the errors above."
    echo ""
    echo "Common issues:"
    echo "  - Backend not deployed: Check Railway dashboard"
    echo "  - CORS not configured: Update backend main.py"
    echo "  - Wrong URL: Verify the Railway URL is correct"
    exit 1
fi
