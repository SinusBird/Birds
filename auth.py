import json
import bcrypt

def load_users(path="users.json"):
    with open(path, "r") as f:
        return json.load(f)

def verify_login(username, password):
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    hashed_pw = user["password"]
    return bcrypt.checkpw(password.encode(), hashed_pw.encode())
