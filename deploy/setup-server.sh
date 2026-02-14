#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# Aasirbad — Server Setup Script
# Run this on a fresh Ubuntu 22.04+ VPS (DigitalOcean, Hetzner, etc.)
#
# Usage:
#   chmod +x deploy/setup-server.sh
#   ./deploy/setup-server.sh your-domain.com
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

DOMAIN="${1:-}"
if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <your-domain.com>"
    exit 1
fi

echo "════════════════════════════════════════════════════"
echo "  Aasirbad Server Setup — $DOMAIN"
echo "════════════════════════════════════════════════════"

# ── 1. System Dependencies ───────────────────────────────────────────────────
echo "→ Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    apt-transport-https ca-certificates curl gnupg lsb-release \
    nginx certbot python3-certbot-nginx \
    ufw fail2ban

# ── 2. Install Docker ────────────────────────────────────────────────────────
echo "→ Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER"
    echo "  Docker installed. You may need to log out and back in."
fi

# ── 3. Firewall ──────────────────────────────────────────────────────────────
echo "→ Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# ── 4. Clone Project ─────────────────────────────────────────────────────────
APP_DIR="/opt/aasirbad"
echo "→ Setting up project at $APP_DIR..."
sudo mkdir -p "$APP_DIR"
sudo chown "$USER:$USER" "$APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
    echo "  Please clone your repo to $APP_DIR"
    echo "  git clone <your-repo-url> $APP_DIR"
    echo "  Then re-run this script."
fi

# ── 5. Create Production .env ────────────────────────────────────────────────
ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "→ Creating production .env..."
    SECRET_KEY=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    DB_PASSWORD=$(openssl rand -base64 16)

    cat > "$ENV_FILE" <<EOF
# Production environment — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)
APP_ENV=production
DEBUG=false
SECRET_KEY=$SECRET_KEY

BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=https://$DOMAIN

# Database (Docker Compose managed)
DB_BACKEND=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=aasirbad
POSTGRES_PASSWORD=$DB_PASSWORD
POSTGRES_DB=aasirbad

# Redis (Docker Compose managed)
REDIS_HOST=redis
REDIS_PORT=6379

# Storage
STORAGE_BACKEND=local
LOCAL_STORAGE_DIR=/app/storage

# Auth
JWT_SECRET_KEY=$JWT_SECRET
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Voice Engine
TORCH_DEVICE=cpu
MIN_RECORDINGS_FOR_TRAINING=5
AUDIO_SAMPLE_RATE=22050

LOG_LEVEL=INFO
EOF
    echo "  Edit $ENV_FILE to customize settings if needed."
fi

# ── 6. Nginx Configuration ──────────────────────────────────────────────────
echo "→ Configuring Nginx..."
sudo cp "$APP_DIR/deploy/nginx/aasirbad.conf" /etc/nginx/sites-available/aasirbad
sudo sed -i "s/YOUR_DOMAIN/$DOMAIN/g" /etc/nginx/sites-available/aasirbad
sudo sed -i "s/server_name _;/server_name $DOMAIN;/g" /etc/nginx/sites-available/aasirbad
sudo ln -sf /etc/nginx/sites-available/aasirbad /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# ── 7. SSL Certificate ──────────────────────────────────────────────────────
echo "→ Obtaining SSL certificate..."
sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --email "admin@$DOMAIN" || {
    echo "  ⚠  Certbot failed. Make sure DNS is pointing to this server."
    echo "  Run manually: sudo certbot --nginx -d $DOMAIN"
}

# ── 8. Start Application ────────────────────────────────────────────────────
echo "→ Starting Aasirbad..."
cd "$APP_DIR"
docker compose pull
docker compose up -d

# Wait for services
echo "→ Waiting for services to start..."
sleep 10

# Run database migrations
docker compose exec api alembic upgrade head 2>/dev/null || echo "  ⚠  Migrations may need to be run manually."

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════"
echo "  ✓ Aasirbad is deployed!"
echo ""
echo "  🌐  https://$DOMAIN"
echo "  📊  Health: https://$DOMAIN/health"
echo "  📖  API Docs: https://$DOMAIN/docs"
echo ""
echo "  Next steps:"
echo "  1. Visit https://$DOMAIN/register to create your account"
echo "  2. docker compose logs -f  (to watch logs)"
echo "════════════════════════════════════════════════════"
