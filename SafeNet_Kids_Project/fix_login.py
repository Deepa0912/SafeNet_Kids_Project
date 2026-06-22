"""Reset all users' both passwords AND parent passwords to match their username."""
import json, hashlib, secrets

with open('data/users.json','r') as f:
    users = json.load(f)

for username in users:
    pw = username  # both passwords = username
    s1 = secrets.token_hex(16)
    s2 = secrets.token_hex(16)
    users[username]['salt'] = s1
    users[username]['hashed_password'] = hashlib.sha256((s1+pw).encode()).hexdigest()
    users[username]['parent_salt'] = s2
    users[username]['parent_hashed_password'] = hashlib.sha256((s2+pw).encode()).hexdigest()
    print(f'[OK] {username}: login="{pw}"  parent="{pw}"')

with open('data/users.json','w') as f:
    json.dump(users, f, indent=2)
print('\nDone. Both passwords set to the username for each user.')
