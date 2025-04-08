import os
import secrets

# Generate a 24-character random string
secret_key = secrets.token_hex(24)
print(f"Generated SECRET_KEY: {secret_key}")