#!/usr/bin/env python3
"""
Create encrypted prompts module
"""

import base64
from cryptography.fernet import Fernet
from pathlib import Path

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

# Save the encrypted version
Path('src/opsydian/prompts_encrypted.py').write_text(encrypted_module)
print("Created encrypted prompts module")
