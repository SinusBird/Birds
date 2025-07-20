import json
import bcrypt

def load_users(path="users.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warnung: {path} nicht gefunden. Leeres Benutzer-Dictionary wird zurückgegeben.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Fehler beim Laden der JSON-Datei: {e}")
        return {}

def verify_login(username, password):
    users = load_users()
    user = users.get(username)
    if username not in users:
        return False, None
    #print('User: ',user)
    hashed_pw = user.get("password")
    #print('Hashed PW: ', hashed_pw)
    if isinstance(hashed_pw, str):
        hashed_pw_bytes = hashed_pw.encode('utf-8')
    else:
        hashed_pw_bytes = hashed_pw

    return bcrypt.checkpw(password.encode('utf-8'), hashed_pw_bytes)


