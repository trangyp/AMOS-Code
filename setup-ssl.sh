#!/bin/bash
#
# AMOS Brain SSL Certificate Setup
# Automates Let's Encrypt certificate generation
#

set -e

DOMAIN="neurosyncai.tech"
EMAIL="admin@neurosyncai.tech"  # Change this

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║           AMOS BRAIN SSL CERTIFICATE SETUP                    ║"
echo "║                     $DOMAIN                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗${NC} Please run as root (use sudo)"
    exit 1
fi

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    apt-get update
    apt-get install -y certbot
fi

# Create webroot for ACME challenge
mkdir -p /var/www/certbot

# Obtain certificate
echo ""
echo "Obtaining SSL certificate for $DOMAIN..."
echo "Make sure $DOMAIN points to this server's IP address"
echo ""

certbot certonly \
    --standalone \
    --preferred-challenges http \
    --agree-tos \
    --non-interactive \
    --email $EMAIL \
    -d $DOMAIN

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} SSL certificate obtained successfully!"
    echo ""
    echo "Certificate location:"
    echo "  /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "  /etc/letsencrypt/live/$DOMAIN/privkey.pem"
    echo ""
    echo -e "${GREEN}✓${NC} SSL setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Deploy with: docker-compose -f docker-compose.ssl.yml up -d"
    echo "  2. Verify at: https://$DOMAIN"
else
    echo -e "${RED}✗${NC} Failed to obtain certificate"
    echo "Check that $DOMAIN resolves to this server"
    exit 1
fi
