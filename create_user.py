import bcrypt
import json
import os

USER_FILE = "users.json"

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def add_user(username, plain_password, role="user"):
    users = load_users()
    if username in users:
        print(f"⚠️ Benutzer '{username}' existiert bereits. Wird überschrieben.")
    hashed_pw = hash_password(plain_password)
    users[username] = {"password": hashed_pw, "role": role}
    save_users(users)
    print(f"✅ Benutzer '{username}' wurde hinzugefügt.")

if __name__ == "__main__":
    username = input("Benutzername: ")
    password = input("Passwort: ")
    add_user(username, password)
