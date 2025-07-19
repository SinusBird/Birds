import json
import bcrypt

def load_users(path="users.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def verify_login(username, password):
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    hashed_pw = user["password"]
    return bcrypt.checkpw(password.encode(), hashed_pw.encode())
