
#!/bin/bash
set -euo pipefail

echo "Building Opsydian..."

# Ensure we have Python 3
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install pyinstaller cryptography requests pyyaml

# Build the encrypted prompts module
python scripts/build_encrypted_prompts.py

# Build using spec file
pyinstaller build.spec

# Move binary to releases
mkdir -p releases
if [ -f "dist/opsydian" ]; then
    mv dist/opsydian releases/opsydian-linux-amd64
    chmod +x releases/opsydian-linux-amd64
    echo "Build complete: releases/opsydian-linux-amd64"
fi

# Cleanup
rm -rf build dist

# Deactivate virtual environment
deactivate
