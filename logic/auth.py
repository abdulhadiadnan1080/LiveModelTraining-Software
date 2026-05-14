import requests

API_BASE = "http://localhost:8001"

def register():
    print("\n--- Register ---")
    username = input("Choose a username: ").strip()
    password = input("Choose a password: ").strip()
    try:
        response = requests.post(f"{API_BASE}/register", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registered successfully as '{data['username']}'.")
            return data
        else:
            print(f"❌ {response.json().get('detail', 'Registration failed.')}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running.")
        return None

def login():
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    try:
        response = requests.post(f"{API_BASE}/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Welcome, {data['username']}! (Role: {data['role']})")
            return data
        else:
            print(f"❌ {response.json().get('detail', 'Login failed.')}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running.")
        return None

def auth_menu():
    """Entry point: asks user to login or register."""
    while True:
        print("\n=== Movie Reservation System ===")
        print("[1] Login")
        print("[2] Register")
        print("[q] Quit")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            session = login()
            if session:
                return session
        elif choice == "2":
            session = register()
            if session:
                return session
        elif choice == "q":
            return None
        else:
            print("Invalid choice.")
