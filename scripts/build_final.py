
#!/usr/bin/env python3
"""
Final build script for Opsydian
Creates a standalone binary with encrypted prompt
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import base64
from cryptography.fernet import Fernet

def create_encrypted_prompts():
    """Create the prompts module with encrypted data"""
    
    # Read the actual prompt
    with open('src/data/system_prompt.txt', 'r') as f:
        prompt = f.read()
    
    # Generate encryption key
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(prompt.encode())
    
    # Create the production prompts module
    encrypted_module = f'''#!/usr/bin/env python3
"""
Production prompts module with encrypted data
"""

import base64
from cryptography.fernet import Fernet

# Encrypted prompt data
_KEY = {repr(base64.b64encode(key).decode())}
_DATA = {repr(base64.b64encode(encrypted).decode())}

def get_system_prompt():
    """Decrypt and return the system prompt"""
    key = base64.b64decode(_KEY)
    data = base64.b64decode(_DATA)
    fernet = Fernet(key)
    return fernet.decrypt(data).decode()
'''
    
    # Ensure build directory exists
    os.makedirs('build/opsydian', exist_ok=True)
    
    # Save the encrypted version
    with open('build/opsydian/prompts.py', 'w') as f:
        f.write(encrypted_module)

def build_binary():
    """Build the final binary"""
    print("Building Opsydian binary...")
    
    # Create build directory
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # Copy source files
    shutil.copytree("src/opsydian", "build/opsydian")
    
    # Replace prompts with encrypted version
    create_encrypted_prompts()
    
    # Create setup.py for building
    setup_py = '''
from setuptools import setup, find_packages

setup(
    name="opsydian",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "opsydian=opsydian.cli:main",
        ],
    },
    install_requires=[
        "requests",
        "pyyaml",
        "cryptography",
    ],
)
'''
    
    with open('build/setup.py', 'w') as f:
        f.write(setup_py)
    
    # Use PyInstaller to create binary
    os.chdir('build')
    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "opsydian",
        "--distpath", "../releases",
        "opsydian/__main__.py"
    ])
    
    print("Binary created in releases/opsydian")
    
    # Cleanup
    os.chdir('..')
    
    # Optionally keep build directory for debugging
    # shutil.rmtree('build')

if __name__ == "__main__":
    # Ensure directories exist
    Path("build").mkdir(exist_ok=True)
    Path("releases").mkdir(exist_ok=True)
    
    # Build (requirements should be installed by build.sh)
    build_binary()
