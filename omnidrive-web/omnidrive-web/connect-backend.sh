#!/bin/bash
#############################################################################
# connect-backend.sh - Frontend ↔ Backend Integration Script
#
# Usage:
#   1. Get Railway backend URL (e.g., https://omnidrive-api.up.railway.app)
#   2. Run: ./connect-backend.sh <RAILWAY_URL>
#
# Example:
#   ./connect-backend.sh https://omnidrive-api.up.railway.app
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if Railway URL is provided
if [ -z "$1" ]; then
    log_error "Railway URL is required!"
    echo ""
    echo "Usage: $0 <RAILWAY_URL>"
    echo ""
    echo "Example:"
    echo "  $0 https://omnidrive-api.up.railway.app"
    exit 1
fi

RAILWAY_URL=$1

# Validate URL format
if [[ ! $RAILWAY_URL =~ ^https?:// ]]; then
    log_error "Invalid URL format. Must start with http:// or https://"
    exit 1
fi

# Remove trailing slash if present
RAILWAY_URL=${RAILWAY_URL%/}

log_info "Starting Frontend ↔ Backend integration..."
log_info "Backend URL: $RAILWAY_URL"
echo ""

#############################################################################
# Step 1: Update .env.production
#############################################################################
log_info "Step 1: Updating .env.production..."

ENV_FILE=".env.production"
BACKUP_FILE=".env.production.backup.$(date +%Y%m%d_%H%M%S)"

# Backup current .env.production
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$BACKUP_FILE"
    log_success "Backed up current .env.production to $BACKUP_FILE"
fi

# Update NEXT_PUBLIC_API_URL
if [ -f "$ENV_FILE" ]; then
    sed -i.bak "s|^NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$RAILWAY_URL|" "$ENV_FILE"
    rm -f "${ENV_FILE}.bak"
    log_success "Updated NEXT_PUBLIC_API_URL=$RAILWAY_URL"
else
    log_error ".env.production file not found!"
    exit 1
fi

#############################################################################
# Step 2: Verify backend connectivity
#############################################################################
log_info "Step 2: Verifying backend connectivity..."

# Test health endpoint
HEALTH_URL="$RAILWAY_URL/health"
log_info "Testing health endpoint: $HEALTH_URL"

if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
    log_success "Backend health check passed!"
    curl -s "$HEALTH_URL" | jq '.' 2>/dev/null || curl -s "$HEALTH_URL"
else
    log_error "Backend health check failed!"
    log_warning "Make sure the Railway backend is deployed and accessible"
fi

#############################################################################
# Step 3: Test API endpoint (root)
#############################################################################
log_info "Step 3: Testing root API endpoint..."

ROOT_URL="$RAILWAY_URL/"
if curl -s -f "$ROOT_URL" > /dev/null 2>&1; then
    log_success "API root endpoint accessible!"
else
    log_warning "Root endpoint not accessible (may not be deployed yet)"
fi

#############################################################################
# Step 4: Check Vercel CLI
#############################################################################
log_info "Step 4: Checking Vercel CLI..."

if ! command -v vercel &> /dev/null; then
    log_warning "Vercel CLI not found. Install with: npm i -g vercel"
    log_info "You'll need to set environment variables manually in Vercel dashboard"
else
    log_success "Vercel CLI found"
fi

#############################################################################
# Step 5: Instructions for Vercel deployment
#############################################################################
echo ""
log_info "Step 5: Vercel Environment Variables Setup"
echo ""
echo "To complete the integration, you need to update Vercel environment variables:"
echo ""
echo "Option A: Using Vercel CLI"
echo "  1. Run: vercel env add NEXT_PUBLIC_API_URL production"
echo "  2. Paste: $RAILWAY_URL"
echo "  3. Run: vercel --prod"
echo ""
echo "Option B: Using Vercel Dashboard"
echo "  1. Go to: https://vercel.com/dashboard"
echo "  2. Select omnidrive-web project"
echo "  3. Settings → Environment Variables"
echo "  4. Add/Update: NEXT_PUBLIC_API_URL = $RAILWAY_URL"
echo "  5. Trigger new deployment"
echo ""

#############################################################################
# Step 6: Create integration test script
#############################################################################
log_info "Step 6: Creating integration test script..."

cat > test-backend-connection.sh << 'EOF'
#!/bin/bash
#############################################################################
# test-backend-connection.sh - Test Backend Connectivity
#############################################################################

BACKEND_URL=${1:-$(grep NEXT_PUBLIC_API_URL .env.production | cut -d'=' -f2)}

echo "Testing Backend Connection: $BACKEND_URL"
echo ""

# Test 1: Health endpoint
echo "🔍 Test 1: Health Endpoint"
HEALTH=$(curl -s "$BACKEND_URL/health")
echo "$HEALTH" | jq '.' 2>/dev/null || echo "$HEALTH"
echo ""

# Test 2: Root endpoint
echo "🔍 Test 2: Root Endpoint"
ROOT=$(curl -s "$BACKEND_URL/")
echo "$ROOT" | jq '.' 2>/dev/null || echo "$ROOT"
echo ""

# Test 3: API Docs
echo "🔍 Test 3: API Docs Availability"
if curl -s -f "$BACKEND_URL/docs" > /dev/null 2>&1; then
    echo "✅ API docs available at $BACKEND_URL/docs"
else
    echo "❌ API docs not accessible"
fi
echo ""

# Test 4: CORS (preflight)
echo "🔍 Test 4: CORS Preflight"
CORS=$(curl -s -X OPTIONS "$BACKEND_URL/api/v1/auth/status" \
    -H "Origin: https://omnidrive.sujeto10.com" \
    -H "Access-Control-Request-Method: GET" \
    -I)
echo "$CORS" | grep -i "access-control-allow" || echo "⚠️  CORS headers not visible"
echo ""

# Test 5: Auth Status endpoint
echo "🔍 Test 5: Auth Status Endpoint"
AUTH_STATUS=$(curl -s "$BACKEND_URL/api/v1/auth/status")
echo "$AUTH_STATUS" | jq '.' 2>/dev/null || echo "$AUTH_STATUS"
echo ""

echo "✅ Tests completed!"
EOF

chmod +x test-backend-connection.sh
log_success "Created test-backend-connection.sh"

#############################################################################
# Step 7: Create README for integration steps
#############################################################################
log_info "Step 7: Creating integration documentation..."

cat > BACKEND_INTEGRATION.md << 'EOF'
# Backend ↔ Frontend Integration Guide

## Prerequisites

1. ✅ Backend deployed on Railway
2. ✅ Frontend deployed on Vercel
3. ✅ Railway URL obtained

## Integration Steps

### 1. Update Vercel Environment Variables

#### Option A: Vercel CLI (Recommended)

```bash
# Install Vercel CLI if needed
npm i -g vercel

# Login to Vercel
vercel login

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production

# When prompted, paste your Railway URL:
# https://omnidrive-api.up.railway.app

# Deploy to production
vercel --prod
```

#### Option B: Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Select `omnidrive-web` project
3. Navigate to **Settings** → **Environment Variables**
4. Update `NEXT_PUBLIC_API_URL` with your Railway URL
5. Click **Save**
6. Trigger new deployment (or wait for auto-deploy)

### 2. Verify Integration

Run the connection test script:

```bash
./test-backend-connection.sh https://omnidrive-api.up.railway.app
```

### 3. Test in Production

Visit your production site: https://omnidrive.sujeto10.com

Open browser DevTools (F12) and check:

- **Network Tab**: Look for API calls to the Railway URL
- **Console Tab**: Check for any CORS or connectivity errors

### 4. Update Backend CORS (if needed)

If you see CORS errors, update the backend CORS configuration:

**File**: `omnidrive-web/api/app/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://omnidrive.sujeto10.com",
        "https://omnidrive-web.vercel.app",
        # Add your production domain if different
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend on Railway.

## API Endpoints to Test

### 1. Health Check
```bash
curl https://omnidrive-api.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "google_drive": "available",
    "folderfort": "available"
  }
}
```

### 2. Auth Status
```bash
curl https://omnidrive-api.up.railway.app/api/v1/auth/status
```

### 3. API Documentation
Visit: https://omnidrive-api.up.railway.app/docs

## Troubleshooting

### Issue: CORS Errors

**Symptoms**: Browser console shows CORS policy errors

**Solution**:
1. Check backend CORS configuration
2. Ensure your frontend domain is in `allow_origins`
3. Redeploy backend after changes

### Issue: Network Timeout

**Symptoms**: API calls timeout or fail

**Solution**:
1. Verify Railway backend is running (check Railway dashboard)
2. Check backend logs for errors
3. Test backend health endpoint directly

### Issue: Environment Variable Not Working

**Symptoms**: Frontend still uses old API URL

**Solution**:
1. Verify environment variable is set in Vercel (not .env.local)
2. Trigger new deployment on Vercel
3. Clear browser cache and hard refresh (Ctrl+Shift+R)

## WebSocket Connection (Future)

The backend also supports WebSocket at `/ws` endpoint.

Test with:
```javascript
const ws = new WebSocket('wss://omnidrive-api.up.railway.app/ws');
ws.onopen = () => console.log('WebSocket connected');
ws.onmessage = (event) => console.log('Message:', event.data);
```

## Monitoring

### Backend Monitoring (Railway)
- Railway Dashboard: https://railway.app
- Check logs, metrics, and deployment status

### Frontend Monitoring (Vercel)
- Vercel Dashboard: https://vercel.com/dashboard
- Check deployments, build logs, and analytics

## Next Steps

1. ✅ Complete integration
2. ✅ Test all API endpoints
3. ✅ Verify authentication flows
4. ✅ Test file operations (upload, download, delete)
5. ✅ Test sync functionality
6. ✅ Load testing and optimization

## Support

For issues or questions:
- Backend logs: Railway dashboard
- Frontend logs: Vercel dashboard
- API documentation: https://omnidrive-api.up.railway.app/docs
EOF

log_success "Created BACKEND_INTEGRATION.md"

#############################################################################
# Summary
#############################################################################
echo ""
log_success "Integration preparation completed!"
echo ""
echo "📋 Summary:"
echo "  - Updated: .env.production (NEXT_PUBLIC_API_URL=$RAILWAY_URL)"
echo "  - Created: test-backend-connection.sh"
echo "  - Created: BACKEND_INTEGRATION.md"
echo ""
echo "🚀 Next Steps:"
echo "  1. Update Vercel environment variables (see BACKEND_INTEGRATION.md)"
echo "  2. Deploy to Vercel: vercel --prod"
echo "  3. Test connectivity: ./test-backend-connection.sh $RAILWAY_URL"
echo "  4. Verify in production: https://omnidrive.sujeto10.com"
echo ""
log_success "Ready for frontend-backend integration!"
