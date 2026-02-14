#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# Aasirbad — One-Command Deploy to DigitalOcean
#
# Run from your local machine (macOS/Linux):
#   chmod +x deploy.sh
#   ./deploy.sh                        # Interactive — prompts for everything
#   ./deploy.sh 164.90.1.2 aasirbad.com  # Non-interactive
#   ./deploy.sh 164.90.1.2 --no-domain   # IP-only, no SSL
#   ./deploy.sh --update 164.90.1.2      # Update existing deployment
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${CYAN}→${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
err()   { echo -e "${RED}✗${NC} $*" >&2; }
header(){ echo -e "\n${BOLD}═══ $* ═══${NC}\n"; }

REPO_URL="https://github.com/arjunchapagain/aasirbad.git"
APP_DIR="/opt/aasirbad"
SSH_USER="root"
UPDATE_MODE=false
NO_DOMAIN=false

# ── Parse Arguments ───────────────────────────────────────────────────────────
if [[ "${1:-}" == "--update" ]]; then
    UPDATE_MODE=true
    SERVER_IP="${2:-}"
    DOMAIN="${3:-}"
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage:"
    echo "  ./deploy.sh                           # Interactive setup"
    echo "  ./deploy.sh <IP> <domain>             # Full deploy with SSL"
    echo "  ./deploy.sh <IP> --no-domain          # Deploy without domain/SSL"
    echo "  ./deploy.sh --update <IP>             # Update existing deploy"
    echo ""
    echo "Prerequisites:"
    echo "  1. DigitalOcean Droplet (Ubuntu 22.04+, $6/mo minimum)"
    echo "  2. SSH key added to the droplet"
    echo "  3. (Optional) Domain pointing to the droplet IP"
    exit 0
else
    SERVER_IP="${1:-}"
    DOMAIN="${2:-}"
fi

# ── Interactive Prompts ───────────────────────────────────────────────────────
if [[ -z "$SERVER_IP" ]]; then
    header "Aasirbad Deploy"
    echo "This script deploys Aasirbad to a DigitalOcean Droplet."
    echo "You need a Droplet running Ubuntu 22.04+ with SSH access."
    echo ""
    read -rp "$(echo -e "${CYAN}Droplet IP address:${NC} ")" SERVER_IP
    if [[ -z "$SERVER_IP" ]]; then
        err "IP address is required."
        exit 1
    fi
fi

if [[ "$DOMAIN" == "--no-domain" ]]; then
    NO_DOMAIN=true
    DOMAIN=""
fi

if [[ -z "$DOMAIN" && "$NO_DOMAIN" == false && "$UPDATE_MODE" == false ]]; then
    echo ""
    read -rp "$(echo -e "${CYAN}Domain name (or press Enter to skip):${NC} ")" DOMAIN
    if [[ -z "$DOMAIN" ]]; then
        NO_DOMAIN=true
        warn "No domain — will deploy on IP only (no SSL)."
    fi
fi

# ── Validate SSH ──────────────────────────────────────────────────────────────
info "Testing SSH connection to $SSH_USER@$SERVER_IP..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" "echo ok" &>/dev/null; then
    err "Cannot SSH into $SSH_USER@$SERVER_IP"
    echo "  Make sure:"
    echo "  1. The droplet is running"
    echo "  2. Your SSH key is added (~/.ssh/id_rsa or ~/.ssh/id_ed25519)"
    echo "  3. The IP is correct"
    echo ""
    echo "  Test manually: ssh $SSH_USER@$SERVER_IP"
    exit 1
fi
ok "SSH connection successful"

# ══════════════════════════════════════════════════════════════════════════════
# UPDATE MODE — just pull and restart
# ══════════════════════════════════════════════════════════════════════════════
if [[ "$UPDATE_MODE" == true ]]; then
    header "Updating Aasirbad on $SERVER_IP"

    ssh "$SSH_USER@$SERVER_IP" bash -s <<'REMOTE_UPDATE'
set -euo pipefail
cd /opt/aasirbad

echo "→ Pulling latest code..."
git pull origin master

echo "→ Rebuilding containers..."
docker compose build --no-cache

echo "→ Restarting services..."
docker compose up -d

echo "→ Running migrations..."
sleep 5
docker compose exec -T api alembic upgrade head 2>/dev/null || echo "  Migrations skipped"

echo "→ Checking health..."
sleep 5
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✓ API is healthy!"
else
    echo "⚠ API health check failed — check logs: docker compose logs api"
fi

echo ""
echo "✓ Update complete!"
docker compose ps
REMOTE_UPDATE

    ok "Update complete!"
    exit 0
fi

# ══════════════════════════════════════════════════════════════════════════════
# FRESH DEPLOY
# ══════════════════════════════════════════════════════════════════════════════
header "Deploying Aasirbad to $SERVER_IP"
[[ -n "$DOMAIN" ]] && info "Domain: $DOMAIN" || info "No domain (IP-only mode)"

# ── Step 1: Install System Dependencies ───────────────────────────────────────
info "Installing system packages on server..."

ssh "$SSH_USER@$SERVER_IP" bash -s <<'REMOTE_DEPS'
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

echo "→ Updating packages..."
apt-get update -qq

echo "→ Installing dependencies..."
apt-get install -y -qq \
    apt-transport-https ca-certificates curl gnupg lsb-release \
    nginx certbot python3-certbot-nginx \
    ufw fail2ban git

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "→ Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install docker compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "→ Installing Docker Compose plugin..."
    apt-get install -y -qq docker-compose-plugin
fi

echo "✓ System dependencies installed"
REMOTE_DEPS

ok "System packages installed"

# ── Step 2: Configure Firewall ────────────────────────────────────────────────
info "Configuring firewall..."

ssh "$SSH_USER@$SERVER_IP" bash -s <<'REMOTE_FW'
set -euo pipefail
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo "✓ Firewall configured"
REMOTE_FW

ok "Firewall configured (SSH, HTTP, HTTPS)"

# ── Step 3: Clone Repository ─────────────────────────────────────────────────
info "Setting up project..."

ssh "$SSH_USER@$SERVER_IP" bash -s -- "$REPO_URL" "$APP_DIR" <<'REMOTE_CLONE'
set -euo pipefail
REPO_URL="$1"
APP_DIR="$2"

if [ -d "$APP_DIR/.git" ]; then
    echo "→ Project exists, pulling latest..."
    cd "$APP_DIR"
    git pull origin master
else
    echo "→ Cloning repository..."
    git clone "$REPO_URL" "$APP_DIR"
fi

echo "✓ Project ready at $APP_DIR"
REMOTE_CLONE

ok "Repository cloned"

# ── Step 4: Generate .env ─────────────────────────────────────────────────────
info "Generating production secrets..."

CORS_ORIGIN="http://$SERVER_IP"
[[ -n "$DOMAIN" ]] && CORS_ORIGIN="https://$DOMAIN"

ssh "$SSH_USER@$SERVER_IP" bash -s -- "$APP_DIR" "$CORS_ORIGIN" <<'REMOTE_ENV'
set -euo pipefail
APP_DIR="$1"
CORS_ORIGIN="$2"
ENV_FILE="$APP_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo "→ .env already exists, keeping it"
else
    echo "→ Generating secure .env..."
    SECRET_KEY=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    DB_PASSWORD=$(openssl rand -base64 16 | tr -d '=/+')

    cat > "$ENV_FILE" <<EOF
# Aasirbad Production — generated $(date -u +%Y-%m-%dT%H:%M:%SZ)
APP_ENV=production
DEBUG=false
SECRET_KEY=$SECRET_KEY
LOG_LEVEL=INFO

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=$CORS_ORIGIN

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
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Voice Engine
TORCH_DEVICE=cpu
MIN_RECORDINGS_FOR_TRAINING=5
AUDIO_SAMPLE_RATE=22050
EOF

    chmod 600 "$ENV_FILE"
    echo "✓ Secure .env generated"
fi
REMOTE_ENV

ok "Production secrets configured"

# ── Step 5: Build & Start Docker Containers ───────────────────────────────────
info "Building and starting containers (this takes 2-5 minutes)..."

ssh "$SSH_USER@$SERVER_IP" bash -s -- "$APP_DIR" <<'REMOTE_DOCKER'
set -euo pipefail
APP_DIR="$1"
cd "$APP_DIR"

echo "→ Pulling base images..."
docker compose pull postgres redis 2>/dev/null || true

echo "→ Building application containers..."
docker compose build --no-cache api frontend

echo "→ Starting all services..."
docker compose up -d postgres redis
echo "→ Waiting for database to be ready..."
sleep 10

docker compose up -d api frontend

echo "→ Waiting for API to start..."
sleep 10

# Run migrations
echo "→ Running database migrations..."
docker compose exec -T api alembic upgrade head 2>/dev/null || {
    echo "  ⚠ Auto-migration skipped — may need manual run"
}

echo ""
echo "→ Container status:"
docker compose ps

echo ""
# Health check
if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✓ API is healthy!"
else
    echo "⚠ API health check failed — checking logs..."
    docker compose logs api --tail 20
fi
REMOTE_DOCKER

ok "Containers running"

# ── Step 6: Configure Nginx ───────────────────────────────────────────────────
info "Configuring Nginx reverse proxy..."

if [[ -n "$DOMAIN" ]]; then
    NGINX_SERVER_NAME="$DOMAIN"
else
    NGINX_SERVER_NAME="$SERVER_IP"
fi

ssh "$SSH_USER@$SERVER_IP" bash -s -- "$APP_DIR" "$NGINX_SERVER_NAME" <<'REMOTE_NGINX'
set -euo pipefail
APP_DIR="$1"
SERVER_NAME="$2"

# Generate nginx config (works for both domain and IP)
cat > /etc/nginx/sites-available/aasirbad <<NGINX
server {
    listen 80;
    server_name $SERVER_NAME;

    client_max_body_size 50M;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 10s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 86400s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000;
        access_log off;
    }

    # API docs
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }
    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/aasirbad /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "✓ Nginx configured for $SERVER_NAME"
REMOTE_NGINX

ok "Nginx configured"

# ── Step 7: SSL (domain only) ────────────────────────────────────────────────
if [[ -n "$DOMAIN" ]]; then
    info "Setting up SSL certificate for $DOMAIN..."

    ssh "$SSH_USER@$SERVER_IP" bash -s -- "$DOMAIN" <<'REMOTE_SSL'
set -euo pipefail
DOMAIN="$1"

certbot --nginx -d "$DOMAIN" \
    --non-interactive --agree-tos \
    --email "admin@$DOMAIN" \
    --redirect || {
    echo ""
    echo "⚠ SSL setup failed. This usually means:"
    echo "  1. DNS for $DOMAIN is not pointing to this server yet"
    echo "  2. DNS propagation hasn't completed"
    echo ""
    echo "  Fix: Point your domain's A record to this server's IP,"
    echo "  wait a few minutes, then run:"
    echo "    ssh root@<IP> certbot --nginx -d $DOMAIN"
}
REMOTE_SSL

    ok "SSL certificate installed"
else
    warn "No domain — skipping SSL. Site available at http://$SERVER_IP"
fi

# ── Step 8: Setup Auto-Renewal & Monitoring ───────────────────────────────────
info "Setting up auto-restart and log rotation..."

ssh "$SSH_USER@$SERVER_IP" bash -s -- "$APP_DIR" <<'REMOTE_CRON'
set -euo pipefail
APP_DIR="$1"

# Auto-restart containers on reboot
cat > /etc/systemd/system/aasirbad.service <<EOF
[Unit]
Description=Aasirbad Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable aasirbad.service

# Docker log rotation
cat > /etc/docker/daemon.json <<EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
systemctl restart docker

# Wait for containers to come back up
sleep 15

echo "✓ Auto-restart and log rotation configured"
REMOTE_CRON

ok "Auto-restart enabled (survives reboots)"

# ══════════════════════════════════════════════════════════════════════════════
# DONE
# ══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${BOLD}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Aasirbad is deployed!${NC}"
echo ""
if [[ -n "$DOMAIN" ]]; then
    echo -e "  🌐  ${BOLD}https://$DOMAIN${NC}"
    echo -e "  📊  Health: https://$DOMAIN/health"
    echo -e "  📖  API Docs: https://$DOMAIN/docs"
else
    echo -e "  🌐  ${BOLD}http://$SERVER_IP${NC}"
    echo -e "  📊  Health: http://$SERVER_IP/health"
    echo -e "  📖  API Docs: http://$SERVER_IP/docs"
fi
echo ""
echo "  Commands:"
echo "    ./deploy.sh --update $SERVER_IP    # Deploy updates"
echo "    ssh root@$SERVER_IP                # SSH into server"
echo ""
echo -e "${BOLD}════════════════════════════════════════════════════${NC}"
