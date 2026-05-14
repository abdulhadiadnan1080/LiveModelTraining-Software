import psycopg2

class seats:
    def __init__(self, Movie, total_seats):
        self.Movie = Movie
        self.total_seats = total_seats
        self.booked_seats = []
        self.remaining_seats = total_seats

def add_seats_to_db(movie_id):
    """
    Generates 50 seats for a specific movie in the database.
    Rows A and E are premium ($15), others are standard ($10).
    """
    try:
        conn = psycopg2.connect(
            dbname="movie_reservation",
            user="postgres",
            password="Abdulhadiadnan1080!",
            host="localhost"
        )
        cur = conn.cursor()
        
        rows = ['A', 'B', 'C', 'D', 'E']
        print(f"--- Generating seats for Movie ID: {movie_id} ---")
        
        for row in rows:
            for seat_num in range(1, 11):
                price = 15.00 if row in ['A', 'E'] else 10.00
                cur.execute(
                    """
                    INSERT INTO seats (movie_id, row_label, seat_number, price) 
                    VALUES (%s, %s, %s, %s) 
                    ON CONFLICT (movie_id, row_label, seat_number) DO NOTHING
                    """,
                    (movie_id, row, seat_num, price)
                )
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Seats generated successfully.")
    except Exception as e:
        print(f"❌ Error generating seats: {e}")
