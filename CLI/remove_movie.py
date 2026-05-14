import requests

API_BASE = "http://localhost:8001"

def remove_movie():
    """Lists movies via API and removes the selected one."""
    print("--- Movie Removal Tool ---")
    
    try:
        # 1. List movies
        response = requests.get(f"{API_BASE}/movies")
        movies = response.json()

        if not movies:
            print("No movies found in the database.")
            return

        print("\nCurrent Movies:")
        for m in movies:
            print(f"[{m['movie_id']}] {m['movie_name']} (Starts: {m['start_time']})")

        # 2. Ask which one to remove
        choice = input("\nEnter the Movie ID you want to remove (or 'q' to quit): ")
        if choice.lower() == 'q':
            return
        if not choice.isdigit():
            print("Invalid input. Please enter a numeric Movie ID.")
            return

        movie_id = int(choice)
        movie_name = next((m['movie_name'] for m in movies if m['movie_id'] == movie_id), None)
        if not movie_name:
            print(f"❌ Movie with ID {movie_id} not found.")
            return

        confirm = input(f"Are you sure you want to remove '{movie_name}'? (y/n): ")
        if confirm.lower() == 'y':
            del_response = requests.delete(f"{API_BASE}/movies/{movie_id}")
            if del_response.status_code == 200:
                print(f"✅ {del_response.json()['message']}")
            else:
                print(f"❌ API Error: {del_response.json().get('detail', del_response.text)}")
        else:
            print("Removal cancelled.")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running (python3 workings/api.py).")


if __name__ == "__main__":
    remove_movie()
