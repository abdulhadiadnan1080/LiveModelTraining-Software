import requests
import re
from datetime import datetime

API_BASE = "http://localhost:8001"

def reserve_seat(role="user"):
    """Displays movies and seats via API, then books the selected seat.
    Regular users only see upcoming (Visible) movies.
    Admins see all movies.
    """
    print("--- Movie Seat Reservation Tool ---")
    
    try:
        # 1. Fetch all movies from API
        response = requests.get(f"{API_BASE}/movies")
        all_movies = response.json()

        # 2. Filter: regular users only see upcoming movies
        if role == "admin":
            movies = all_movies
        else:
            now = datetime.now()
            movies = [
                m for m in all_movies
                if datetime.fromisoformat(m['start_time']) > now
            ]

        if not movies:
            print("No available movies found.")
            return

        print("\nAvailable Movies:")
        for m in movies:
            print(f"[{m['movie_id']}] {m['movie_name']} (Starts: {m['start_time']})")

        movie_choice = input("\nEnter the Movie ID you want to book for: ")
        if not movie_choice.isdigit():
            print("Invalid Movie ID.")
            return

        movie_id = int(movie_choice)
        movie = next((m for m in movies if m['movie_id'] == movie_id), None)
        if not movie:
            print(f"❌ Movie ID {movie_id} not found.")
            return

        # 3. Fetch and display seats
        seats_response = requests.get(f"{API_BASE}/movies/{movie_id}/seats")
        seats_data = seats_response.json()

        if not seats_data:
            print("No seats found for this movie.")
            return

        print(f"\n--- Seats for '{movie['movie_name']}' ---")
        print("Legend: [ ] = Available, [X] = Booked")

        current_row = ""
        row_str = ""
        for s in seats_data:
            row = s['row_label'].strip()
            num = s['seat_number']
            booked = s['is_booked']
            if row != current_row:
                if row_str: print(row_str)
                current_row = row
                row_str = f"{row}: "
            status = "[X]" if booked else "[ ]"
            row_str += f"{num}{status}  "
        print(row_str)  # print last row

        # 4. User selects a seat
        seat_input = input("\nEnter seat number to book (e.g., 1A, 5B, A10): ").upper().strip()

        match = re.match(r'([A-E])(\d+)|(\d+)([A-E])', seat_input)
        if not match:
            print("❌ Invalid format. Please use something like '1A' or 'A1'.")
            return

        if match.group(1):  # A1 format
            row_label = match.group(1)
            seat_num = int(match.group(2))
        else:               # 1A format
            row_label = match.group(4)
            seat_num = int(match.group(3))

        # 5. Reserve via API
        reserve_response = requests.post(f"{API_BASE}/reserve/{movie_id}/{row_label}/{seat_num}")
        if reserve_response.status_code == 200:
            print(f"✅ {reserve_response.json()['message']}")
        else:
            print(f"❌ {reserve_response.json().get('detail', reserve_response.text)}")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running (python3 workings/api.py).")


if __name__ == "__main__":
    reserve_seat()
