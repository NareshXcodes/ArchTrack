import secrets

def generate_invite_token():
    return secrets.token_hex(32)
