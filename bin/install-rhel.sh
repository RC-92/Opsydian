#!/bin/bash
IP=$1
USER=$2
PASSWORD=$3
PACKAGE=$4

echo "Installing $PACKAGE"

# Check existence
if ! dnf list "$PACKAGE" &>/dev/null; then
  echo "❌ Package $PACKAGE not found."
  exit 1
fi

# Install
sudo dnf install -y "$PACKAGE"

