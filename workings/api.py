import json
import os
import stripe
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from datetime import datetime, timedelta
from typing import List, Optional

app = FastAPI(title="Movie Reservation API")

# ── Stripe Config (Replace with your keys) ──────────────────────────────────
stripe.api_key = "sk_test_51TWLZhB5qV6qUznwU91ItUZZRBrTYMKZOEusZYKDdVTu3DMObFIFNVTCFUPNdKGkXb3dHkcVdNU6JXNbqFH6gZx2000NwLXwHz"
GUI_URL = "http://localhost:9000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB Connection ────────────────────────────────────────────────────────────
def get_db_connection():
    return psycopg2.connect(
        dbname="movie_reservation",
        user="postgres",
        password="Abdulhadiadnan1080!",
        host="localhost"
    )

# ── Pydantic Models ──────────────────────────────────────────────────────────
class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    username: str
    role: str

class MovieCreate(BaseModel):
    name: str
    duration_minutes: int
    start_time: datetime

class MovieResponse(BaseModel):
    movie_id: int
    movie_name: str
    duration_minutes: int
    start_time: datetime
    end_time: datetime

class SeatResponse(BaseModel):
    seat_id: int
    row_label: str
    seat_number: int
    is_booked: bool
    price: float
    booked_at: Optional[datetime] = None
    username: Optional[str] = None

# ── Helper: Cleanup ──────────────────────────────────────────────────────────
def cleanup_expired_reservations():
    """Releases seats that were booked more than 5 minutes ago."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # If a seat is booked but no payment confirmation (we'll assume anything > 5m is expired for this demo)
        expiry_limit = datetime.now() - timedelta(minutes=5)
        cur.execute(
            "UPDATE seats SET is_booked = FALSE, booked_at = NULL, username = NULL "
            "WHERE is_booked = TRUE AND booked_at < %s;",
            (expiry_limit,)
        )
        count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        if count > 0:
            print(f"⏰ Timer: Released {count} expired seat(s).")
    except Exception as e:
        print(f"Error in cleanup: {e}")

# ── Auth Endpoints ───────────────────────────────────────────────────────────
@app.get("/users")
def get_users():
    print('APPPPPPPPPPPPPPPPPPPPPP')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        users = cur.fetchall()
        print('APIIIII',users)
        cur.close()
        conn.close()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register", response_model=AuthResponse)
def register(payload: AuthRequest):
    """Register a new regular user in the DB."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'user') RETURNING username, role;",
            (payload.username, payload.password)
        )
        user = cur.fetchone()
        conn.commit()
        return AuthResponse(username=user[0], role=user[1])
    except psycopg2.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username already exists.")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
"""
@app.get("/forgot/password")
def forgot_password(payload: AuthRequest):
    #If user forgets the password is set to hadi

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password = %s WHERE username = %s;",
            ("hadi", payload.username)
        )
        conn.commit()
        cur.close()
        conn.close()

        return AuthResponse(username=payload.username, role="user")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
"""
@app.post("/forgot/password")
def forgot_password(payload: AuthRequest):
    #if user  forgot the password is set 'hadi'hasattr

    try:
        conn= get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "Update users Set password = 'hadi' Where username = %s;",
            (payload.username)
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=404, detail="username not found.")
        return {"message": "password updated successfully."}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
"""
@app.post("/forgot/password")
def forgot_password(payload: AuthRequest):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "UPDATE users SET password = 'hadi' WHERE username = %s RETURNING username;",
            (payload.username,) 
        )
        
        updated_user = cur.fetchone()
        conn.commit()

        if not updated_user:
            raise HTTPException(status_code=404, detail="Username not found.")
            
        return {"message": f"Password for {payload.username} updated successfully."}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest):
    """Login by checking the users table."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT username, role FROM users WHERE username = %s AND password = %s;",
            (payload.username, payload.password)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return AuthResponse(username=user[0], role=user[1])
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Movie Endpoints ──────────────────────────────────────────────────────────

@app.get("/movies", response_model=List[MovieResponse])
def list_movies():
    """Returns all movies in the database (with auto-cleanup check)."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT movie_id, movie_name, duration_minutes, start_time, end_time FROM movies ORDER BY movie_id;")
        movies = cur.fetchall()
        cur.close()
        conn.close()
        return [
            MovieResponse(movie_id=m[0], movie_name=m[1], duration_minutes=m[2], start_time=m[3], end_time=m[4])
            for m in movies
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/movies", response_model=MovieResponse)
def add_movie(movie: MovieCreate):
    """Adds a new movie. The DB trigger automatically generates 50 seats."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        end_time = movie.start_time + timedelta(minutes=movie.duration_minutes)
        cur.execute(
            "INSERT INTO movies (movie_name, duration_minutes, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING movie_id;",
            (movie.name, movie.duration_minutes, movie.start_time, end_time)
        )
        movie_id = cur.fetchone()[0]
        conn.commit()
        return MovieResponse(
            movie_id=movie_id,
            movie_name=movie.name,
            duration_minutes=movie.duration_minutes,
            start_time=movie.start_time,
            end_time=end_time
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    """Deletes a movie and all its seats (via ON DELETE CASCADE)."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE movie_id = %s RETURNING movie_name;", (movie_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not deleted:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {"message": f"Movie '{deleted[0]}' and its seats removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/movies/{movie_id}/seats", response_model=List[SeatResponse])
def list_seats(movie_id: int):
    """Returns all seats for a given movie (with auto-cleanup check)."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT seat_id, row_label, seat_number, is_booked, price, booked_at, username FROM seats WHERE movie_id = %s ORDER BY row_label, seat_number;",
            (movie_id,)
        )
        seats = cur.fetchall()
        cur.close()
        conn.close()
        return [
            SeatResponse(
                seat_id=s[0], row_label=s[1], seat_number=s[2], 
                is_booked=s[3], price=float(s[4]), booked_at=s[5], username=s[6]
            )
            for s in seats
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reserve/{movie_id}/{row_label}/{seat_number}")
def reserve_seat(movie_id: int, row_label: str, seat_number: int, username: str = Body(..., embed=True)):
    """Books a specific seat for a movie. Starts the 5-minute timer."""
    cleanup_expired_reservations()
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        now = datetime.now()
        cur.execute(
            "UPDATE seats SET is_booked = TRUE, booked_at = %s, username = %s "
            "WHERE movie_id = %s AND row_label = %s AND seat_number = %s AND is_booked = FALSE "
            "RETURNING seat_id;",
            (now, username, movie_id, row_label.upper(), seat_number)
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=400, detail="Seat not available or already booked")
        return {"message": "Seat held for 5 minutes. Please complete payment.", "booked_at": now}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.delete("/reserve/{movie_id}/{row_label}/{seat_number}")
def cancel_reservation(movie_id: int, row_label: str, seat_number: int, username: str = Body(..., embed=True), role: str = Body(..., embed=True)):
    """Cancels a booking. Admin can cancel any, Users can only cancel their own."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check ownership unless admin
        if role != "admin":
            cur.execute(
                "SELECT username FROM seats WHERE movie_id = %s AND row_label = %s AND seat_number = %s;",
                (movie_id, row_label.upper(), seat_number)
            )
            owner = cur.fetchone()
            if not owner or owner[0] != username:
                raise HTTPException(status_code=403, detail="You can only cancel your own bookings.")

        cur.execute(
            "UPDATE seats SET is_booked = FALSE, booked_at = NULL, username = NULL "
            "WHERE movie_id = %s AND row_label = %s AND seat_number = %s RETURNING seat_id;",
            (movie_id, row_label.upper(), seat_number)
        )
        updated = cur.fetchone()
        conn.commit()
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found.")
        return {"message": "Reservation cancelled successfully."}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@app.post("/payment/create-session/{movie_id}/{row}/{num}")
def create_payment_session(movie_id: int, row: str, num: int):
    """Creates a real Stripe Checkout Session for a seat booking."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get seat price and movie name for Stripe
        cur.execute(
            "SELECT s.price, m.movie_name FROM seats s JOIN movies m ON s.movie_id = m.movie_id "
            "WHERE s.movie_id = %s AND s.row_label = %s AND s.seat_number = %s;",
            (movie_id, row.upper(), num)
        )
        data = cur.fetchone()
        cur.close()
        conn.close()
        
        if not data:
            raise HTTPException(status_code=404, detail="Seat or Movie not found")
        
        price_cents = int(data[0] * 100) # Stripe uses cents
        movie_name = data[1]

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': f"Seat {row}{num} - {movie_name}"},
                    'unit_amount': price_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{GUI_URL}/success?movie_id={movie_id}&row={row}&num={num}",
            cancel_url=f"{GUI_URL}/cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment/confirm/{movie_id}/{row}/{num}")
def confirm_payment(movie_id: int, row: str, num: int):
    """Finalizes the booking after 'payment'."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # We assume payment is successful, so we clear the timer but keep the seat booked
        # In a real app, we'd mark 'is_paid' = TRUE
        cur.execute(
            "UPDATE seats SET booked_at = NULL WHERE movie_id = %s AND row_label = %s AND seat_number = %s RETURNING seat_id;",
            (movie_id, row.upper(), num)
        )
        updated = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not updated:
             raise HTTPException(status_code=404, detail="Reservation not found.")
        return {"message": "Payment confirmed. Your ticket is ready!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
