#!/usr/bin/env bash
# deploy.sh — Deploy or redeploy api.maediia.com
#
# Usage:
#   First deploy:   sudo bash deploy/deploy.sh --setup
#   Redeploy:       sudo bash deploy/deploy.sh
#
# Assumes:
#   - Running as root or with sudo on the VPS
#   - Git repo cloned to /projects/maediia_platform/maediia-api
#   - .env file present at /projects/maediia_platform/maediia-api/.env
#   - PostgreSQL and Redis running

set -euo pipefail

APP_DIR="/projects/maediia_platform/maediia-api"
VENV="$APP_DIR/.venv"
PYTHON="$VENV/bin/python"
PIP="$VENV/bin/pip"

log() { echo "[$(date '+%H:%M:%S')] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
[[ -f "$APP_DIR/.env" ]] || die ".env not found at $APP_DIR/.env — copy .env.example and fill in values"
[[ -d "$APP_DIR" ]]      || die "App directory not found: $APP_DIR"

cd "$APP_DIR"

# ---------------------------------------------------------------------------
# --setup: first-deploy tasks (run once)
# ---------------------------------------------------------------------------
if [[ "${1:-}" == "--setup" ]]; then
    log "=== First-deploy setup ==="

    log "Installing system packages..."
    apt-get update -qq
    apt-get install -y -qq python3.12 python3.12-venv python3-pip nginx supervisor certbot python3-certbot-nginx

    log "Creating virtualenv..."
    python3.12 -m venv "$VENV"

    log "Installing Python dependencies..."
    $PIP install --quiet --upgrade pip
    $PIP install --quiet -r requirements.txt

    log "Creating log directories..."
    mkdir -p /var/log/supervisor
    chown www-data:www-data /var/log/supervisor || true

    log "Installing Nginx config..."
    cp deploy/nginx/api.maediia.com.conf /etc/nginx/sites-available/api.maediia.com
    ln -sf /etc/nginx/sites-available/api.maediia.com /etc/nginx/sites-enabled/api.maediia.com
    rm -f /etc/nginx/sites-enabled/default
    nginx -t
    systemctl enable nginx
    systemctl start nginx

    log "Issuing SSL certificate (Let's Encrypt)..."
    certbot --nginx -d api.maediia.com --non-interactive --agree-tos -m admin@maediia.com

    log "Installing Supervisor configs..."
    cp deploy/supervisor/maediia-api.conf    /etc/supervisor/conf.d/maediia-api.conf
    cp deploy/supervisor/maediia-worker.conf /etc/supervisor/conf.d/maediia-worker.conf
    systemctl enable supervisor
    systemctl start supervisor

    log "Running database migrations..."
    $VENV/bin/alembic upgrade head

    log "Loading Supervisor programs..."
    supervisorctl reread
    supervisorctl update
    supervisorctl start maediia-api maediia-worker

    log "=== Setup complete ==="
    log "Health check: curl https://api.maediia.com/health"
    exit 0
fi

# ---------------------------------------------------------------------------
# Standard redeploy
# ---------------------------------------------------------------------------
log "=== Redeploying api.maediia.com ==="

log "Pulling latest code..."
git pull --ff-only

log "Installing/updating dependencies..."
$PIP install --quiet -r requirements.txt

log "Running database migrations..."
$VENV/bin/alembic upgrade head

log "Restarting API server..."
supervisorctl restart maediia-api

log "Restarting ARQ worker..."
supervisorctl restart maediia-worker

log "Waiting for API to come up..."
sleep 3

log "Health check..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)
if [[ "$HTTP_STATUS" == "200" ]]; then
    log "Health check passed (HTTP $HTTP_STATUS)"
else
    die "Health check failed (HTTP $HTTP_STATUS) — check: supervisorctl tail maediia-api"
fi

log "=== Redeploy complete ==="
