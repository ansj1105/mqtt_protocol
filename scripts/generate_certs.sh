#!/bin/bash

# TLS 인증서 생성 스크립트
# Self-signed certificates for development/testing

set -e

CERT_DIR="$(dirname "$0")/../certs"
mkdir -p "$CERT_DIR"

echo "Generating TLS certificates..."
echo "Certificate directory: $CERT_DIR"
echo ""

# Configuration
COUNTRY="KR"
STATE="Seoul"
CITY="Seoul"
ORG="WebSocket Server"
OU="Development"
CN="localhost"
EMAIL="admin@localhost"
DAYS=365

# Generate CA key and certificate
echo "1. Generating CA key and certificate..."
openssl req -x509 -newkey rsa:4096 -days $DAYS -nodes \
    -keyout "$CERT_DIR/ca.key" \
    -out "$CERT_DIR/ca.crt" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=CA/emailAddress=$EMAIL"

echo "   ✓ CA certificate created"

# Generate server key
echo "2. Generating server private key..."
openssl genrsa -out "$CERT_DIR/server.key" 4096
echo "   ✓ Server key created"

# Generate server CSR
echo "3. Generating server certificate signing request..."
openssl req -new -key "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.csr" \
    -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$OU/CN=$CN/emailAddress=$EMAIL"

echo "   ✓ Server CSR created"

# Sign server certificate with CA
echo "4. Signing server certificate with CA..."
openssl x509 -req -in "$CERT_DIR/server.csr" \
    -CA "$CERT_DIR/ca.crt" \
    -CAkey "$CERT_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERT_DIR/server.crt" \
    -days $DAYS \
    -sha256

echo "   ✓ Server certificate signed"

# Clean up CSR
rm "$CERT_DIR/server.csr"

# Set permissions
chmod 600 "$CERT_DIR"/*.key
chmod 644 "$CERT_DIR"/*.crt

echo ""
echo "✅ TLS certificates generated successfully!"
echo ""
echo "Files created:"
echo "  - CA certificate: $CERT_DIR/ca.crt"
echo "  - CA key: $CERT_DIR/ca.key"
echo "  - Server certificate: $CERT_DIR/server.crt"
echo "  - Server key: $CERT_DIR/server.key"
echo ""
echo "⚠️  Note: These are self-signed certificates for development only."
echo "    For production, use certificates from a trusted CA."
echo ""

# Display certificate info
echo "Server certificate details:"
openssl x509 -in "$CERT_DIR/server.crt" -noout -text | grep -A 2 "Subject:"
echo ""

