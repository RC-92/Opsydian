
#!/usr/bin/env python3
"""
Build script for Opsydian
Creates compiled binary with encrypted system prompt
"""

import os
import sys
import base64
import shutil
from cryptography.fernet import Fernet
from pathlib import Path

def encrypt_prompt():
    """Encrypt the system prompt"""
    # Read the prompt
    with open('src/data/system_prompt.txt', 'r') as f:
        prompt = f.read()
    
    # Generate a key (in production, this should be more secure)
    key = Fernet.generate_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(prompt.encode())
    
    # Encode both key and encrypted data
    return base64.b64encode(key).decode(), base64.b64encode(encrypted).decode()

def create_compiled_version():
    """Create a version with embedded encrypted prompt"""
    key_encoded, prompt_encoded = encrypt_prompt()
    
    # Create the main script with embedded data
    compiled_code = f'''
import base64
from cryptography.fernet import Fernet

# Embedded encrypted data
KEY_ENCODED = "{key_encoded}"
PROMPT_ENCODED = "{prompt_encoded}"

def get_system_prompt():
    """Decrypt and return the system prompt"""
    key = base64.b64decode(KEY_ENCODED)
    encrypted = base64.b64decode(PROMPT_ENCODED)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted).decode()

# Add the rest of your application code here
'''
    
    with open('src/opsydian_compiled.py', 'w') as f:
        f.write(compiled_code)
    
    print("Created compiled version with encrypted prompt")

if __name__ == "__main__":
    create_compiled_version()
