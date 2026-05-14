import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.auth import auth_menu

# Import working scripts from CLI folder
from CLI import add_movie as add_movie_module
from CLI import remove_movie as remove_movie_module
from CLI import reserve_seat as reserve_seat_module
from CLI import remove_booking as remove_booking_module


def admin_menu(session):
    while True:
        print(f"\n=== Admin Menu ({session['username']}) ===")
        print("[1] Add Movie")
        print("[2] Remove Movie")
        print("[3] Reserve a Seat")
        print("[4] Remove a Booking")
        print("[5] View Database")
        print("[q] Logout")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            add_movie_module.add_movie([])
        elif choice == "2":
            remove_movie_module.remove_movie()
        elif choice == "3":
            reserve_seat_module.reserve_seat(role="admin")
        elif choice == "4":
            remove_booking_module.remove_booking()
        elif choice == "5":
            print("Database viewer currently unavailable.")
            # view_database_module.display_all_info()
        elif choice == "q":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")


def user_menu(session):
    while True:
        print(f"\n=== Movie Reservation ({session['username']}) ===")
        print("[1] Reserve a Seat")
        print("[2] Remove a Booking")
        print("[q] Logout")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            reserve_seat_module.reserve_seat(role="user")
        elif choice == "2":
            remove_booking_module.remove_booking()
        elif choice == "q":
            print("Logged out.")
            break
        else:
            print("Invalid choice.")


def main():
    session = auth_menu()
    if not session:
        print("Goodbye.")
        return

    if session["role"] == "admin":
        admin_menu(session)
    else:
        user_menu(session)


if __name__ == "__main__":
    main()
