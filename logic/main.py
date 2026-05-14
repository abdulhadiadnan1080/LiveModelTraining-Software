import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie import Movie
from CLI.add_movie import add_movie_hardcode, add_movie
from datetime import datetime

API_BASE = "http://localhost:8001"


def Display(list_of_movies):
    print('\n#####--------------------------------------------######')
    print("--- Movie Display Status ---")
    for m in list_of_movies:
        m.update_display_status()
        status = "Visible" if m.display else "Hidden (Started)"
        print(f"Movie: {m.name: <15} | Status: {status}")
    print('#####--------------------------------------------######\n')

def main():
    list_of_movies = []
    
    add_movie_hardcode(list_of_movies)
    
    print('Checking hardcoded movies...')
    Display(list_of_movies)
    
    print('Now add your own:')
    add_movie(list_of_movies)
    
    Display(list_of_movies)


if __name__ == "__main__":
    main()

