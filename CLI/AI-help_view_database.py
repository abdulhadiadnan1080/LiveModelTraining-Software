import requests

API_BASE = "http://localhost:8001"

def display_all_info():
    """Fetches and displays all database info via the API."""
    print("--- Movie Reservation Database Viewer (via API) ---")
    
    try:
        # 1. Movies
        movies_response = requests.get(f"{API_BASE}/movies")
        movies = movies_response.json()

        print(f"\n{'='*60}")
        print(" TABLE: movies")
        print(f"{'='*60}")
        if not movies:
            print(" (No movies found)")
        else:
            header = f"{'ID':<6} {'Name':<20} {'Duration':>10} {'Start Time':<22} {'End Time':<22}"
            print(header)
            print("-" * len(header))
            for m in movies:
                print(f"{m['movie_id']:<6} {m['movie_name']:<20} {m['duration_minutes']:>8} min  {m['start_time']:<22} {m['end_time']:<22}")

        # 2. Seats per movie
        for m in movies:
            seats_response = requests.get(f"{API_BASE}/movies/{m['movie_id']}/seats")
            seats = seats_response.json()
            print(f"\n{'='*60}")
            print(f" SEATS for '{m['movie_name']}' (Movie ID: {m['movie_id']})")
            print(f"{'='*60}")
            print("Legend: [ ] = Available, [X] = Booked")
            current_row = ""
            row_str = ""
            for s in seats:
                row = s['row_label'].strip()
                num = s['seat_number']
                booked = s['is_booked']
                if row != current_row:
                    if row_str: print(row_str)
                    current_row = row
                    row_str = f"{row}: "
                status = "[X]" if booked else "[ ]"
                row_str += f"{num}{status}  "
            if row_str: print(row_str)

        print(f"\n{'='*60}")
        print("End of database information.")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running (python3 workings/api.py).")


if __name__ == "__main__":
    display_all_info()
