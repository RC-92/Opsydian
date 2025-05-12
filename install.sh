#!/bin/bash
set -euo pipefail

echo "=================================="
echo "  Opsydian Installer"
echo "=================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root"
   exit 1
fi

# Detect OS
if [[ -f /etc/debian_version ]]; then
    OS="debian"
    echo "Detected Debian/Ubuntu system"
else
    echo "Error: This installer only supports Debian/Ubuntu"
    exit 1
fi

# GitHub release info
GITHUB_USER="RC-92"
GITHUB_REPO="Opsydian"
BINARY_NAME="opsydian-linux-amd64"

echo "Downloading Opsydian binary..."

# Get latest release download URL
LATEST_RELEASE=$(curl -s https://api.github.com/repos/$GITHUB_USER/$GITHUB_REPO/releases/latest | grep browser_download_url | grep $BINARY_NAME | cut -d '"' -f 4)

if [ -z "$LATEST_RELEASE" ]; then
    echo "Error: Could not find latest release"
    exit 1
fi

# Download binary
curl -L -o /tmp/opsydian $LATEST_RELEASE
chmod +x /tmp/opsydian

# Install binary
mv /tmp/opsydian /usr/local/bin/opsydian

echo "Installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip

echo "Installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

echo "Creating service user..."
useradd -r -m -s /bin/bash opsydian || true

echo "Setting up directories..."
mkdir -p /opt/opsydian/{data,logs,jobs}
chown -R opsydian:opsydian /opt/opsydian

echo "Installation complete!"
echo "Run 'opsydian --help' to get started"
