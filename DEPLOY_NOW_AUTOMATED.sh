#!/bin/bash

# OmniDrive Automated Deployment Script
# Target: omnidrive.sujeto10.com

set -e

echo "🚀 OmniDrive Deployment - omnidrive.sujeto10.com"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "${BLUE}📋 Configuration Summary${NC}"
echo "Frontend: https://omnidrive.sujeto10.com (Vercel)"
echo "Backend: Railway (instructions below)"
echo "Database: https://josxxqkdnvqodxvtjgov.supabase.co"
echo ""

# ============================================
# STEP 1: DATABASE SETUP
# ============================================
echo "${YELLOW}Step 1: Database Setup${NC}"
echo ""
echo "✅ SQL Schema created: supabase_schema.sql"
echo ""
echo "📋 Please run the SQL in Supabase SQL Editor:"
echo "   URL: https://josxxqkdnvqodxvtjgov.supabase.co"
echo "   Go to: SQL Editor > New Query"
echo "   Paste contents from: supabase_schema.sql"
echo ""
echo "Press ENTER when done..."
read

echo "${GREEN}✅ Database confirmed${NC}"
echo ""

# ============================================
# STEP 2: BACKEND (Railway)
# ============================================
echo "${YELLOW}Step 2: Backend Deployment (Railway)${NC}"
echo ""
echo "📋 Follow RAILWAY_SETUP.md for detailed instructions:"
echo ""
echo "Quick commands:"
echo "  1. npm install -g @railway/cli"
echo "  2. railway login"
echo "  3. cd omnidrive-web/api"
echo "  4. railway init"
echo "  5. railway variables set PYTHON_VERSION=3.10"
echo "  6. railway variables set SUPABASE_URL=https://josxxqkdnvqodxvtjgov.supabase.co"
echo "  7. railway variables set SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impvc3h4cWtkbnZxb2R4dnRqZ292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY4NDcxMDgsImV4cCI6MjA3MjQyMzEwOH0.mqje6kdzf8rl2Fdkenxzj4nDhEelY4H5EW4k7bdtHUU"
echo "  8. railway variables set PROJECT_PREFIX=omnidrive_"
echo "  9. railway variables set OPENAI_API_KEY=sk-e2537cbaff974532ac35cb20a7177ca1"
echo " 10. railway variables set FRONTEND_URL=https://omnidrive.sujeto10.com"
echo " 11. railway up"
echo ""
echo "Press ENTER when backend is deployed..."
read

echo "${GREEN}✅ Backend deployment noted${NC}"
echo ""

# ============================================
# STEP 3: FRONTEND (Vercel)
# ============================================
echo "${YELLOW}Step 3: Frontend Deployment (Vercel)${NC}"
echo ""
echo "Installing dependencies..."
cd omnidrive-web/omnidrive-web
npm install --silent

echo "Building project..."
npm run build

echo "Deploying to Vercel..."
vercel --prod --yes

echo "Setting custom domain..."
vercel domains add omnidrive.sujeto10.com 2>/dev/null || true

cd ../..

echo "${GREEN}✅ Frontend deployed to Vercel${NC}"
echo ""

# ============================================
# STEP 4: DNS (Cloudflare)
# ============================================
echo "${YELLOW}Step 4: DNS Configuration (Cloudflare)${NC}"
echo ""
echo "📋 Add these records in Cloudflare (sujeto10.com):"
echo ""
echo "  Type: CNAME | Name: omnidrive | Content: cname.vercel.net | Proxy: Orange cloud"
echo "  Type: CNAME | Name: api        | Content: railway.app  | Proxy: Grey cloud"
echo ""
echo "Press ENTER when DNS is configured..."
read

echo "${GREEN}✅ DNS configured${NC}"
echo ""

# ============================================
# COMPLETE
# ============================================
echo "${GREEN}🎉 Deployment Process Complete!${NC}"
echo ""
echo "${BLUE}📋 URLs${NC}"
echo "  Frontend:  https://omnidrive.sujeto10.com"
echo "  Dashboard: https://omnidrive.sujeto10.com/dashboard"
echo "  Database:  https://josxxqkdnvqodxvtjgov.supabase.co"
echo ""
echo "${BLUE}⏳ Wait 5-10 minutes for DNS propagation${NC}"
echo ""
echo "${GREEN}Ready to access! 🚀${NC}"
