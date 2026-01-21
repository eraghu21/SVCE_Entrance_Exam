import hashlib

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, stored_hash):
    return hash_password(password) == stored_hash
