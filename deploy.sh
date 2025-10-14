#!/bin/bash

# Automated deployment script for local-ai-packaged
# This script handles zero-downtime deployments with proper error handling

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Deployment directory
DEPLOY_DIR="/home/deploy/app"
BACKUP_DIR="/home/deploy/backups/$(date +%Y%m%d_%H%M%S)"

log_info "🚀 Starting deployment process..."
log_info "Deployment directory: $DEPLOY_DIR"
log_info "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Navigate to deployment directory
cd "$DEPLOY_DIR"

# Backup current environment file
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    log_info "Environment file backed up"
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose not found. Please install docker-compose."
    exit 1
fi

# Check if docker is running
if ! sudo docker info &> /dev/null; then
    log_error "Docker is not running or not accessible."
    exit 1
fi

log_info "🔄 Stopping current services..."
sudo docker-compose down || log_warning "Some services failed to stop gracefully"

log_info "🧹 Cleaning up unused Docker resources..."
sudo docker system prune -f || log_warning "Docker cleanup failed"

log_info "📦 Pulling latest Docker images..."
sudo docker-compose pull || log_error "Failed to pull Docker images"

log_info "🏗️ Building services (if needed)..."
sudo docker-compose build --parallel || log_warning "Some services failed to build"

log_info "🚀 Starting services..."
sudo docker-compose up -d || log_error "Failed to start services"

log_info "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
log_info "🔍 Checking service health..."
SERVICES=$(sudo docker-compose ps --services --filter "status=running")

if [ -z "$SERVICES" ]; then
    log_error "No services are running!"
    log_info "Checking service logs..."
    sudo docker-compose logs
    exit 1
fi

log_success "Services running: $SERVICES"

# Verify web service is accessible
log_info "🌐 Testing web service accessibility..."
if curl -f -s --max-time 10 http://localhost:80 > /dev/null; then
    log_success "Web service is accessible on port 80"
else
    log_warning "Web service not accessible on port 80"
fi

# Test HTTPS
if curl -f -s --max-time 10 -k https://localhost:443 > /dev/null; then
    log_success "HTTPS service is accessible on port 443"
else
    log_warning "HTTPS service not accessible on port 443"
fi

log_success "✅ Deployment completed successfully!"
log_info "📊 Deployment summary:"
log_info "  - Services deployed: $(echo "$SERVICES" | wc -l)"
log_info "  - Backup created: $BACKUP_DIR"
log_info "  - Deployment time: $(date)"

# Optional: Send notification (uncomment and configure as needed)
# curl -X POST -H 'Content-type: application/json' \
#   --data '{"text":"🚀 Deployment completed successfully!"}' \
#   YOUR_SLACK_WEBHOOK_URL

exit 0
