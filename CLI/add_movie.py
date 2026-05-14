import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import re
import requests
from logic.movie import Movie
from datetime import datetime, timedelta
from dateutil import parser

API_BASE = "http://localhost:8001"

def add_movie(target_list):
    name = input("Enter movie name: ")
    
    raw_duration = input("Enter movie duration (e.g., 1.5h, 90m): ")
    duration_in_mins = correct_to_minutes(raw_duration)
    
    print("--- Scheduling Movie ---")
    start_time = get_valid_datetime()
    
    movie = Movie(name, duration_in_mins, start_time)
    target_list.append(movie)
    
    # Save via API
    save_movie_via_api(movie)
    
    print(f"\n Added {name}")
    print(f"   Duration: {duration_in_mins} mins")
    print(f"   Starts:   {start_time.strftime('%A, %b %d at %I:%M %p')}")
    return movie

def save_movie_via_api(movie):
    """Saves the movie by calling the REST API."""
    try:
        response = requests.post(f"{API_BASE}/movies", json={
            "name": movie.name,
            "duration_minutes": movie.duration,
            "start_time": movie.start_time.isoformat()
        })
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Movie '{movie.name}' saved to DB via API with ID: {data['movie_id']}")
            return data['movie_id']
        else:
            print(f"❌ API Error saving movie: {response.json().get('detail', response.text)}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure api.py is running (python3 workings/api.py).")
        return None


def correct_to_minutes(user_input):
    text = user_input.lower().replace(" ", "")
    
    if re.match(r'^\d+\.?\d*$', text):
        val = float(text)
        if '.' in text or val < 10:
            return int(val * 60)
        return int(val)
    
    hours_match = re.search(r'(\d*\.?\d+)\s*(?:h|hour)', text)
    mins_match = re.search(r'(\d*\.?\d+)\s*(?:m|min)', text)
    
    hours = float(hours_match.group(1)) if hours_match else 0
    minutes = float(mins_match.group(1)) if mins_match else 0
    
    return int((hours * 60) + minutes)


def get_valid_datetime():
    while True:
        try:
            date_input = input("Enter date (e.g., May 12, 12/05/26, tomorrow): ")
            time_input = input("Enter time (e.g., 2:30 PM, 14:30, 2pm): ")
            combined_string = f"{date_input} {time_input}"
            full_datetime = parser.parse(combined_string, fuzzy=True)
            return full_datetime
        except (ValueError, OverflowError):
            print("Invalid format. Try something like 'May 12' and '2:30pm'.")


def add_movie_hardcode(target_list):
    movie1 = Movie("The Matrix", 136, datetime.now() - timedelta(minutes=10))
    movie2 = Movie("Inception", 148, datetime.now() + timedelta(hours=1))
    target_list.append(movie1)
    target_list.append(movie2)
