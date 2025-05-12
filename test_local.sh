
#!/bin/bash
# Test the built binary locally

if [ -f "releases/opsydian-linux-amd64" ]; then
    ./releases/opsydian-linux-amd64 --version
else
    echo "Binary not found. Run ./build.sh first"
fi
