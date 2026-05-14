import requests
import re

API_BASE = "http://localhost:8001"

def remove_booking():
    print("--- Remove Booking Tool ---")
    
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()

    # Login to get role
    try:
        login_res = requests.post(f"{API_BASE}/login", json={"username": username, "password": password})
        if login_res.status_code != 200:
            print("❌ Invalid credentials.")
            return
        session = login_res.json()
        role = session['role']
        
        # 1. Fetch movies
        movies_res = requests.get(f"{API_BASE}/movies")
        movies = movies_res.json()
        
        print("\nAvailable Movies:")
        for m in movies:
            print(f"[{m['movie_id']}] {m['movie_name']}")
            
        movie_id = input("\nEnter Movie ID to manage bookings: ")
        
        # 2. Fetch seats
        seats_res = requests.get(f"{API_BASE}/movies/{movie_id}/seats")
        seats = seats_res.json()
        
        # Filter: if user, show only their bookings. If admin, show all booked.
        booked_seats = [
            s for s in seats 
            if s['is_booked'] and (role == 'admin' or s['username'] == username)
        ]
        
        if not booked_seats:
            print("\nNo bookings found that you can remove.")
            return
            
        print("\nYour current bookings (or all if admin):")
        for s in booked_seats:
            print(f"- Seat {s['row_label']}{s['seat_number']} (User: {s['username']})")
            
        seat_to_remove = input("\nEnter seat to remove (e.g., 1A): ").upper().strip()
        
        match = re.match(r'([A-E])(\d+)|(\d+)([A-E])', seat_to_remove)
        if not match:
            print("❌ Invalid format.")
            return
            
        row = match.group(1) or match.group(4)
        num = int(match.group(2) or match.group(3))
        
        # 3. Call DELETE
        del_res = requests.delete(
            f"{API_BASE}/reserve/{movie_id}/{row}/{num}",
            json={"username": username, "role": role}
        )
        
        if del_res.ok:
            print(f"✅ {del_res.json()['message']}")
        else:
            print(f"❌ {del_res.json().get('detail', 'Failed to remove booking.')}")

    except requests.exceptions.ConnectionError:
        print("❌ API is not running.")

if __name__ == "__main__":
    remove_booking()
