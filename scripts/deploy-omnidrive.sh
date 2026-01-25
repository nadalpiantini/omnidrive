#!/bin/bash

# OmniDrive Deployment Script for omnidrive.sujeto10.com
# Hybrid CLI + Web Dashboard deployment
# Backend: Railway (FastAPI)
# Frontend: Vercel (Next.js)
# Database: Supabase (PostgreSQL)

set -e

echo "🚀 OmniDrive Deployment - omnidrive.sujeto10.com"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="omnidrive"
DEPLOY_DOMAIN="omnidrive.sujeto10.com"
API_DOMAIN="api.omnidrive.sujeto10.com"
DB_PREFIX="omnidrive_"
BACKEND_DIR="omnidrive-web/api"
FRONTEND_DIR="omnidrive-web/omnidrive-web"

echo ""
echo "${BLUE}📋 Deployment Configuration${NC}"
echo "Project: ${PROJECT_NAME}"
echo "Frontend: ${DEPLOY_DOMAIN}"
echo "Backend API: ${API_DOMAIN}"
echo "DB Prefix: ${DB_PREFIX}"
echo "Backend: Railway (FastAPI)"
echo "Frontend: Vercel (Next.js)"
echo "Database: Supabase"
echo ""

# Function to prompt for input
prompt_input() {
  local prompt="$1"
  local var_name="$2"
  local default="$3"

  if [ -n "$default" ]; then
    read -p "${prompt} [${default}]: " input
    eval $var_name="${input:-$default}"
  else
    read -p "${prompt}: " input
    eval $var_name="$input"
  fi
}

# Function to hide password input
prompt_password() {
  local prompt="$1"
  local var_name="$2"

  echo -n "${prompt}: "
  read -s input
  eval $var_name="$input"
  echo ""
}

# ============================================
# STEP 1: SUPABASE CONFIGURATION
# ============================================
echo "${YELLOW}Step 1: Supabase Database Configuration${NC}"
echo "Please provide your Supabase credentials:"
echo ""

prompt_input "Supabase URL" SUPABASE_URL
prompt_input "Supabase Anon Key" SUPABASE_ANON_KEY
prompt_input "Supabase Service Role Key" SUPABASE_SERVICE_KEY

# Validate URL format
if [[ ! $SUPABASE_URL =~ ^https://.*\.supabase\.co$ ]]; then
  echo "${RED}❌ Invalid Supabase URL format${NC}"
  echo "Expected: https://your-project.supabase.co"
  exit 1
fi

echo "${GREEN}✅ Supabase configuration collected${NC}"
echo ""

# ============================================
# STEP 2: AI SERVICES CONFIGURATION
# ============================================
echo "${YELLOW}Step 2: AI Services Configuration${NC}"
echo "OpenAI API is required for RAG (semantic search)"
echo ""

prompt_input "OpenAI API Key" OPENAI_API_KEY

if [[ ! $OPENAI_API_KEY =~ ^sk- ]]; then
  echo "${RED}❌ Invalid OpenAI API key format${NC}"
  echo "Expected: sk-..."
  exit 1
fi

echo "${GREEN}✅ OpenAI configuration collected${NC}"
echo ""

# ============================================
# STEP 3: GOOGLE DRIVE CONFIGURATION
# ============================================
echo "${YELLOW}Step 3: Google Drive Configuration${NC}"
echo "You need a Google Service Account JSON file"
echo "Create one at: https://console.cloud.google.com"
echo ""

prompt_input "Path to service account JSON file" GOOGLE_SA_PATH ""

if [ -z "$GOOGLE_SA_PATH" ] || [ ! -f "$GOOGLE_SA_PATH" ]; then
  echo "${YELLOW}⚠️  Service account file not found, skipping Google Drive config${NC}"
  GOOGLE_SA_JSON=""
else
  # Read and escape JSON
  GOOGLE_SA_JSON=$(cat "$GOOGLE_SA_PATH" | jq -c .)
  echo "${GREEN}✅ Google Drive service account loaded${NC}"
fi
echo ""

# ============================================
# STEP 4: FOLDERFORT CONFIGURATION
# ============================================
echo "${YELLOW}Step 4: Folderfort Configuration${NC}"
echo ""

prompt_input "Folderfort Email" FOLDERFORT_EMAIL ""
prompt_password "Folderfort Password" FOLDERFORT_PASSWORD

if [ -z "$FOLDERFORT_EMAIL" ] || [ -z "$FOLDERFORT_PASSWORD" ]; then
  echo "${YELLOW}⚠️  Folderfort credentials not provided, skipping${NC}"
else
  echo "${GREEN}✅ Folderfort configuration collected${NC}"
fi
echo ""

# ============================================
# STEP 5: DEPLOYMENT TOKENS
# ============================================
echo "${YELLOW}Step 5: Deployment Tokens${NC}"
echo ""

prompt_input "Railway Token" RAILWAY_TOKEN ""
prompt_input "Vercel Token" VERCEL_TOKEN ""

echo "${GREEN}✅ Deployment tokens collected${NC}"
echo ""

# ============================================
# STEP 6: CREATE ENVIRONMENT FILES
# ============================================
echo "${YELLOW}Step 6: Creating Environment Files${NC}"

# Backend .env for Railway
cat > ${BACKEND_DIR}/.env.production << EOF
# OmniDrive Backend - Production Environment
# Generated: $(date)

# Database
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
PROJECT_PREFIX=${DB_PREFIX}

# AI Services
OPENAI_API_KEY=${OPENAI_API_KEY}

# Google Drive
GOOGLE_SERVICE_ACCOUNT_JSON=${GOOGLE_SA_JSON}

# Folderfort
FOLDERFORT_API_URL=https://na2.folderfort.com
FOLDERFORT_EMAIL=${FOLDERFORT_EMAIL}
FOLDERFORT_PASSWORD=${FOLDERFORT_PASSWORD}

# App Config
PYTHON_VERSION=3.10
PORT=8000
FRONTEND_URL=https://${DEPLOY_DOMAIN}
APP_NAME=OmniDrive
APP_VERSION=1.0.0
ENVIRONMENT=production
LOG_LEVEL=info
EOF

echo "${GREEN}✅ Backend .env.production created${NC}"

# Frontend .env for Vercel
cat > ${FRONTEND_DIR}/.env.production << EOF
# OmniDrive Frontend - Production Environment
# Generated: $(date)

# API Endpoints
NEXT_PUBLIC_API_URL=https://${API_DOMAIN}
NEXT_PUBLIC_WS_URL=wss://${API_DOMAIN}/ws

# App Config
NEXT_PUBLIC_APP_NAME=OmniDrive
NEXT_PUBLIC_APP_URL=https://${DEPLOY_DOMAIN}
NEXT_PUBLIC_VERSION=1.0.0

# Database (Supabase Client)
NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
EOF

echo "${GREEN}✅ Frontend .env.production created${NC}"
echo ""

# ============================================
# STEP 7: BACKEND DEPLOYMENT (Railway)
# ============================================
echo "${YELLOW}Step 7: Deploying Backend to Railway${NC}"
echo ""

if [ -z "$RAILWAY_TOKEN" ]; then
  echo "${YELLOW}⚠️  Railway token not provided, skipping backend deployment${NC}"
  echo "You can deploy manually later using the Railway CLI or dashboard"
else
  echo "Installing Railway CLI..."
  npm install -g @railway/cli 2>/dev/null || true

  echo "Logging in to Railway..."
  echo "$RAILWAY_TOKEN" | railway login 2>/dev/null || true

  cd ${BACKEND_DIR}

  echo "Initializing Railway project..."
  railway init --name omnidrive-api || echo "Project may already exist"

  echo "Setting environment variables..."
  railway variables set PYTHON_VERSION=3.10
  railway variables set SUPABASE_URL=${SUPABASE_URL}
  railway variables set SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
  railway variables set SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
  railway variables set PROJECT_PREFIX=${DB_PREFIX}
  railway variables set OPENAI_API_KEY=${OPENAI_API_KEY}
  railway variables set FRONTEND_URL=https://${DEPLOY_DOMAIN}
  railway variables set APP_NAME=OmniDrive
  railway variables set ENVIRONMENT=production

  if [ -n "$GOOGLE_SA_JSON" ]; then
    railway variables set GOOGLE_SERVICE_ACCOUNT_JSON="${GOOGLE_SA_JSON}"
  fi

  if [ -n "$FOLDERFORT_EMAIL" ]; then
    railway variables set FOLDERFORT_EMAIL=${FOLDERFORT_EMAIL}
    railway variables set FOLDERFORT_PASSWORD=${FOLDERFORT_PASSWORD}
  fi

  echo "Deploying to Railway..."
  railway up

  BACKEND_URL=$(railway domain | head -n 1)
  echo "${GREEN}✅ Backend deployed: ${BACKEND_URL}${NC}"

  cd ../..
fi
echo ""

# ============================================
# STEP 8: FRONTEND DEPLOYMENT (Vercel)
# ============================================
echo "${YELLOW}Step 8: Deploying Frontend to Vercel${NC}"
echo ""

if [ -z "$VERCEL_TOKEN" ]; then
  echo "${YELLOW}⚠️  Vercel token not provided, skipping frontend deployment${NC}"
  echo "You can deploy manually later using the Vercel CLI or dashboard"
else
  echo "Installing Vercel CLI..."
  npm install -g vercel 2>/dev/null || true

  cd ${FRONTEND_DIR}

  echo "Logging in to Vercel..."
  echo "$VERCEL_TOKEN" | vercel login 2>/dev/null || true

  echo "Installing dependencies..."
  npm install

  echo "Building project..."
  npm run build

  echo "Deploying to Vercel..."
  vercel --prod --yes

  echo "Setting custom domain..."
  vercel domains add ${DEPLOY_DOMAIN} 2>/dev/null || echo "Domain may already be set"

  echo "${GREEN}✅ Frontend deployed: https://${DEPLOY_DOMAIN}${NC}"

  cd ../..
fi
echo ""

# ============================================
# STEP 9: DATABASE SCHEMA SETUP
# ============================================
echo "${YELLOW}Step 9: Database Schema Setup${NC}"
echo ""
echo "📋 To complete the setup, run these SQL commands in your Supabase SQL editor:"
echo ""
echo "${BLUE}--- Copy and paste this into Supabase SQL Editor ---${NC}"
echo ""
cat << 'EOF'
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create tables with omnidrive_ prefix
CREATE TABLE IF NOT EXISTS omnidrive_files (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  service VARCHAR(50) NOT NULL,
  file_id VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(500) NOT NULL,
  mime_type VARCHAR(100),
  size BIGINT,
  parent_id VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  metadata JSONB
);

CREATE TABLE IF NOT EXISTS omnidrive_embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_id VARCHAR(255) NOT NULL,
  content TEXT,
  embedding vector(1536),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  FOREIGN KEY (file_id) REFERENCES omnidrive_files(file_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS omnidrive_sync_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_service VARCHAR(50) NOT NULL,
  target_service VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  files_synced INTEGER DEFAULT 0,
  total_files INTEGER DEFAULT 0,
  error_message TEXT,
  started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_files_service ON omnidrive_files(service);
CREATE INDEX IF NOT EXISTS idx_files_file_id ON omnidrive_files(file_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_file_id ON omnidrive_embeddings(file_id);
CREATE INDEX IF NOT EXISTS idx_sync_jobs_status ON omnidrive_sync_jobs(status);

-- Enable Row Level Security
ALTER TABLE omnidrive_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE omnidrive_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE omnidrive_sync_jobs ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your auth strategy)
CREATE POLICY "Enable all access for authenticated users" ON omnidrive_files
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON omnidrive_embeddings
  FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Enable all access for authenticated users" ON omnidrive_sync_jobs
  FOR ALL USING (auth.role() = 'authenticated');
EOF
echo ""
echo "${BLUE}--- End of SQL commands ---${NC}"
echo ""

read -p "Have you run the SQL schema in Supabase? (y/n): " confirm_sql
if [[ $confirm_sql != [Yy]* ]]; then
  echo "${YELLOW}⚠️  Please run the SQL schema first for full functionality${NC}"
else
  echo "${GREEN}✅ Database schema confirmed${NC}"
fi
echo ""

# ============================================
# STEP 10: DNS CONFIGURATION
# ============================================
echo "${YELLOW}Step 10: DNS Configuration${NC}"
echo ""
echo "Configure these DNS records in Cloudflare for sujeto10.com:"
echo ""
echo "${BLUE}Frontend (Next.js on Vercel)${NC}"
echo "  Type: CNAME"
echo "  Name: omnidrive"
echo "  Content: cname.vercel.net"
echo "  Proxy: Proxied (Orange cloud)"
echo ""
echo "${BLUE}Backend (FastAPI on Railway)${NC}"
echo "  Type: CNAME"
echo "  Name: api"
echo "  Content: railway.app"
echo "  Proxy: DNS only (Grey cloud)"
echo ""
read -p "Have you configured the DNS records? (y/n): " confirm_dns
if [[ $confirm_dns != [Yy]* ]]; then
  echo "${YELLOW}⚠️  Please configure DNS for custom domain to work${NC}"
else
  echo "${GREEN}✅ DNS configuration noted${NC}"
fi
echo ""

# ============================================
# STEP 11: VERIFICATION & TESTING
# ============================================
echo "${YELLOW}Step 11: Verification${NC}"
echo ""

# Check if backend URL is available
if [ -n "$BACKEND_URL" ]; then
  echo "Testing backend health endpoint..."
  if curl -f -s "${BACKEND_URL}/health" > /dev/null 2>&1; then
    echo "${GREEN}✅ Backend is responding${NC}"
  else
    echo "${YELLOW}⚠️  Backend health check failed (may still be deploying)${NC}"
  fi
fi

echo ""
echo "Manual verification steps:"
echo "1. Frontend: https://${DEPLOY_DOMAIN}"
echo "2. Backend API: https://${API_DOMAIN}"
echo "3. API Docs: https://${API_DOMAIN}/docs"
echo ""

# ============================================
# FINAL INSTRUCTIONS
# ============================================
echo "${GREEN}🎉 Deployment Process Complete!${NC}"
echo "===================================="
echo ""
echo "${BLUE}📋 Next Steps:${NC}"
echo ""
echo "1. Wait for DNS propagation (5-10 minutes)"
echo "2. Verify frontend loads: https://${DEPLOY_DOMAIN}"
echo "3. Verify backend API: https://${API_DOMAIN}/health"
echo "4. Test authentication (Google Drive, Folderfort)"
echo "5. Test file operations (list, upload, download)"
echo "6. Test sync functionality between services"
echo "7. Test semantic search (RAG)"
echo ""
echo "${BLUE}🔗 Useful URLs:${NC}"
echo "- Frontend: https://${DEPLOY_DOMAIN}"
echo "- Dashboard: https://${DEPLOY_DOMAIN}/dashboard"
echo "- API Docs: https://${API_DOMAIN}/docs"
echo "- Health Check: https://${API_DOMAIN}/health"
echo ""
echo "${BLUE}📊 Monitoring:${NC}"
echo "- Railway Dashboard: https://railway.app/project/omnidrive-api"
echo "- Vercel Dashboard: https://vercel.com/dashboard"
echo "- Supabase Dashboard: ${SUPABASE_URL}"
echo ""
echo "${BLUE}🔧 Local CLI Usage:${NC}"
echo "The CLI is still available:"
echo "  cd omnidrive-cli"
echo "  python3 -m omnidrive list google"
echo "  python3 -m omnidrive --help"
echo ""
echo "${GREEN}Happy multi-cloud syncing! 🚀${NC}"
