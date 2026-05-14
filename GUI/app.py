"""
Movie Reservation System - ALL-IN-ONE (Stripe + Premium UI + Admin)
Run: /usr/bin/python3 gui/app.py
"""
import http.server
import webbrowser
import json
import socketserver
from urllib.parse import urlparse

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cinema Pro - Ultimate Cinema Experience</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; overflow-x: hidden; }

  /* ── Auth Screen ── */
  #auth-screen { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%); }
  .auth-box { background: #1e293b; padding: 40px; border-radius: 20px; width: 380px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); border: 1px solid #334155; }
  .auth-box h1 { text-align: center; margin-bottom: 8px; font-size: 28px; font-weight: 700; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .auth-box p { text-align: center; font-size: 14px; color: #94a3b8; margin-bottom: 30px; }
  .tab-btns { display: flex; margin-bottom: 24px; background: #0f172a; padding: 4px; border-radius: 12px; }
  .tab-btn { flex: 1; padding: 10px; background: transparent; border: none; color: #64748b; cursor: pointer; font-size: 14px; font-weight: 600; border-radius: 8px; transition: 0.3s; }
  .tab-btn.active { background: #38bdf8; color: #0f172a; }
  input[type=text], input[type=password] { width: 100%; padding: 12px 16px; margin-bottom: 16px; border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: #f8fafc; font-size: 14px; outline: none; }
  .btn-primary { width: 100%; padding: 14px; background: linear-gradient(to right, #38bdf8, #818cf8); border: none; border-radius: 10px; color: #0f172a; font-size: 16px; cursor: pointer; font-weight: 700; transition: 0.3s; }
  .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.4); }

  /* ── App Shell ── */
  nav { background: #1e293b; padding: 0 40px; display: flex; align-items: center; height: 70px; border-bottom: 1px solid #334155; position: sticky; top: 0; z-index: 100; }
  nav h2 { font-size: 22px; font-weight: 800; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; flex: 1; cursor: pointer; }
  .nav-user { font-size: 14px; font-weight: 600; color: #94a3b8; margin-right: 20px; }
  .btn-logout { background: #ef4444; border: none; color: #fff; padding: 8px 18px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }

  main { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
  .section { background: #1e293b; border-radius: 24px; padding: 32px; margin-bottom: 32px; border: 1px solid #334155; }
  .section h3 { font-size: 20px; margin-bottom: 24px; font-weight: 700; }

  /* ── Movie Cards Grid ── */
  .movie-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }
  .movie-card { background: #0f172a; border-radius: 16px; padding: 24px; cursor: pointer; border: 2px solid transparent; transition: 0.3s; }
  .movie-card:hover { border-color: #38bdf8; transform: translateY(-5px); }
  .movie-card .badge { padding: 4px 12px; background: rgba(56, 189, 248, 0.1); color: #38bdf8; border-radius: 20px; font-size: 12px; font-weight: 700; }

  /* ── Seating ── */
  #seat-section { display: none; text-align: center; }
  .screen { width: 100%; height: 12px; background: #f8fafc; border-radius: 50%; margin: 20px auto 60px; box-shadow: 0 15px 40px 10px rgba(56, 189, 248, 0.4); }
  .seat-grid { display: grid; grid-template-columns: 30px repeat(5, 1fr) 20px repeat(5, 1fr); gap: 10px; align-items: center; margin-bottom: 40px; max-width: 700px; margin-left: auto; margin-right: auto; }
  .seat-row-label { font-weight: 700; color: #64748b; font-size: 14px; }
  .aisle { width: 20px; }
  .seat { aspect-ratio: 1; background: #334155; border-radius: 8px 8px 4px 4px; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: #94a3b8; }
  .seat.available:hover { background: #38bdf8; color: #0f172a; transform: scale(1.1); }
  .seat.selected { background: #38bdf8; color: #0f172a; box-shadow: 0 0 15px rgba(56, 189, 248, 0.6); }
  .seat.booked { background: #1e293b; color: #475569; cursor: not-allowed; opacity: 0.5; }
  .seat.booked.mine { background: #818cf8; color: #0f172a; opacity: 1; border: 2px solid #38bdf8; cursor: pointer; }

  /* ── Status Message Screens ── */
  #status-screen { display: none; flex-direction: column; justify-content: center; align-items: center; min-height: 80vh; text-align: center; }
  .status-icon { font-size: 64px; margin-bottom: 20px; }
  .status-title { font-size: 32px; font-weight: 800; margin-bottom: 10px; }

  .actions-bar { display: flex; justify-content: center; gap: 15px; margin-top: 20px; }
  .btn-action { padding: 14px 30px; border: none; border-radius: 12px; font-size: 15px; font-weight: 700; cursor: pointer; transition: 0.3s; }
  .btn-action.primary { background: #38bdf8; color: #0f172a; }
  .btn-action.danger { background: #ef4444; color: #fff; }
  .btn-action.success { background: #22c55e; color: #fff; }

  /* ── Admin Table ── */
  table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
  th { text-align: left; padding: 12px 20px; color: #64748b; font-size: 13px; }
  td { padding: 16px 20px; background: #0f172a; }
  td:first-child { border-radius: 12px 0 0 12px; }
  td:last-child { border-radius: 0 12px 12px 0; }

  .hidden { display: none !important; }
</style>
</head>
<body>

<div id="auth-screen">
  <div class="auth-box">
    <h1>CINEMA PRO</h1>
    <div class="tab-btns">
      <button class="tab-btn active" id="tab-login" onclick="showTab('login')">Login</button>
      <button class="tab-btn" id="tab-register" onclick="showTab('register')">Register</button>
    </div>
    <div id="login-form">
      <input type="text" id="login-user" placeholder="Username">
      <input type="password" id="login-pass" placeholder="Password">
      <button class="btn-primary" onclick="doLogin()">Sign In</button>
    </div>
    <div id="register-form" class="hidden">
      <input type="text" id="reg-user" placeholder="Choose Username">
      <input type="password" id="reg-pass" placeholder="Choose Password">
      <button class="btn-primary" onclick="doRegister()">Create Account</button>
    </div>
    <div id="auth-msg" style="text-align:center; margin-top:20px; color:#ef4444;"></div>
  </div>
</div>

<div id="app-screen" class="hidden">
  <nav>
    <h2 onclick="location.reload()">CINEMA PRO</h2>
    <span class="nav-user" id="nav-username"></span>
    <button class="btn-logout" onclick="doLogout()">Sign Out</button>
  </nav>

  <main>
    <div class="section" id="movies-section">
      <h3>🎬 Now Playing</h3>
      <div class="movie-grid" id="movie-grid">Loading...</div>
    </div>

    <div class="section" id="seat-section">
      <h3 id="seat-title">Select Seats</h3>
      <div class="screen"></div>
      <div id="seat-grid" class="seat-grid"></div>
      <div class="actions-bar">
        <button class="btn-action primary" id="btn-hold" onclick="startPayment()">Book & Pay with Stripe</button>
        <button class="btn-action danger hidden" id="btn-cancel" onclick="cancelBooking()">Cancel Reservation</button>
      </div>
      <div id="app-msg" style="margin-top:20px; text-align:center; font-weight:600;"></div>
    </div>

    <!-- Admin Sections (Restored) -->
    <div class="section hidden" id="admin-add-section">
      <h3>➕ Add New Movie</h3>
      <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px; margin-bottom:20px;">
        <input type="text" id="add-name" placeholder="Movie Title">
        <input type="text" id="add-duration" placeholder="Duration (min)">
        <input type="datetime-local" id="add-start">
      </div>
      <button class="btn-action primary" onclick="addMovie()">Add to Catalog</button>
    </div>

    <div class="section hidden" id="admin-table-section">
      <h3>📋 Catalog Management</h3>
      <table id="movies-table">
        <thead><tr><th>ID</th><th>Title</th><th>Schedule</th><th>Actions</th></tr></thead>
        <tbody id="movies-tbody"></tbody>
      </table>
    </div>
  </main>
</div>

<div id="status-screen">
  <div class="status-icon">Good-Job!</div>
  <div class="status-title">Booking Confirmed!</div>
  <p>Your payment was successful. Enjoy your movie!</p>
  <button class="btn-action primary" onclick="location.href='/'" style="margin-top:30px">Back to Catalog</button>
</div>

<script>
const API = "http://localhost:8001";
let session = null;
let selectedSeat = null;
let selectedMovieId = null;

// Handle Redirects on Page Load
window.onload = () => {
  const path = window.location.pathname;
  const params = new URLSearchParams(window.location.search);
  if (path === '/success') {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('status-screen').style.display = 'flex';
    const mid = params.get('movie_id');
    const row = params.get('row');
    const num = params.get('num');
    fetch(`${API}/payment/confirm/${mid}/${row}/${num}`, {method:'POST'});
  }
};

function showTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  document.getElementById('tab-login').classList.toggle('active', tab === 'login');
  document.getElementById('tab-register').classList.toggle('active', tab === 'register');
}

async function doLogin() {
  const username = document.getElementById('login-user').value;
  const password = document.getElementById('login-pass').value;
  const res = await fetch(`${API}/login`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
  if (res.ok) { session = await res.json(); startApp(); }
  else { document.getElementById('auth-msg').innerText = "Invalid credentials"; }
}

async function doRegister() {
  const username = document.getElementById('reg-user').value;
  const password = document.getElementById('reg-pass').value;
  const res = await fetch(`${API}/register`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password}) });
  if (res.ok) { alert("Registered! Please login."); showTab('login'); }
  else { const data = await res.json(); document.getElementById('auth-msg').innerText = data.detail; }
}

function startApp() {
  document.getElementById('auth-screen').style.display = 'none';
  document.getElementById('app-screen').classList.remove('hidden');
  document.getElementById('nav-username').innerText = session.username.toUpperCase();
  if (session.role === 'admin') {
    document.getElementById('admin-add-section').classList.remove('hidden');
    document.getElementById('admin-table-section').classList.remove('hidden');
  }
  loadMovies();
}

function doLogout() { location.reload(); }

async function loadMovies() {
  const res = await fetch(`${API}/movies`);
  const all = await res.json();
  const movies = session.role === 'admin' ? all : all.filter(m => new Date(m.start_time) > new Date());
  
  document.getElementById('movie-grid').innerHTML = movies.map(m => `
    <div class="movie-card" onclick="selectMovie(${m.movie_id}, '${m.movie_name}')">
      <div class="badge">NOW PLAYING</div>
      <h4 style="margin-top:15px">${m.movie_name}</h4>
      <p style="font-size:13px; color:#94a3b8; margin-top:5px">${m.duration_minutes} mins</p>
    </div>`).join('');
  
  if (session.role === 'admin') {
    document.getElementById('movies-tbody').innerHTML = all.map(m => `
      <tr><td>#${m.movie_id}</td><td>${m.movie_name}</td><td>${new Date(m.start_time).toLocaleString()}</td>
      <td><button class="btn-action danger" style="padding:8px 16px; font-size:12px" onclick="deleteMovie(${m.movie_id})">DELETE</button></td></tr>`).join('');
  }
}

async function selectMovie(id, name) {
  selectedMovieId = id; selectedSeat = null;
  document.getElementById('seat-title').innerText = `SEATING FOR: ${name.toUpperCase()}`;
  document.getElementById('seat-section').style.display = 'block';
  document.getElementById('btn-hold').classList.add('hidden');
  document.getElementById('btn-cancel').classList.add('hidden');
  loadSeats(id);
}

async function loadSeats(movieId) {
  const res = await fetch(`${API}/movies/${movieId}/seats`);
  const seats = await res.json();
  const rows = ['A','B','C','D','E'];
  let html = '';
  rows.forEach(row => {
    html += `<span class="seat-row-label">${row}</span>`;
    for (let n = 1; n <= 10; n++) {
      if (n === 6) html += `<div class="aisle"></div>`;
      const s = seats.find(x => x.row_label.trim() === row && x.seat_number === n);
      const isMine = s && s.username === session.username;
      const status = s.is_booked ? (isMine ? 'booked mine' : 'booked') : 'available';
      const title = s.is_booked ? `By: ${s.username}` : `$${s.price}`;
      html += `<div class="seat ${status}" id="seat-${row}${n}" title="${title}" onclick="chooseSeat('${row}',${n},${isMine})">${n}</div>`;
    }
  });
  document.getElementById('seat-grid').innerHTML = html;
}

function chooseSeat(row, num, isMine) {
  const el = document.getElementById(`seat-${row}${num}`);
  const isBooked = el.classList.contains('booked');
  
  document.querySelectorAll('.seat.selected').forEach(s => s.classList.remove('selected'));
  selectedSeat = {row, num, isMine};

  if (isBooked) {
    document.getElementById('btn-hold').classList.add('hidden');
    document.getElementById('btn-cancel').classList.toggle('hidden', !isMine && session.role !== 'admin');
  } else {
    el.classList.add('selected');
    document.getElementById('btn-hold').classList.remove('hidden');
    document.getElementById('btn-cancel').classList.add('hidden');
  }
}

async function startPayment() {
  const {row, num} = selectedSeat;
  const hold = await fetch(`${API}/reserve/${selectedMovieId}/${row}/${num}`, {
    method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: session.username})
  });
  if (!hold.ok) return alert("Seat already taken!");
  
  const stripe = await fetch(`${API}/payment/create-session/${selectedMovieId}/${row}/${num}`, {method:'POST'});
  const {checkout_url} = await stripe.json();
  window.location.href = checkout_url;
}

async function cancelBooking() {
  const {row, num} = selectedSeat;
  await fetch(`${API}/reserve/${selectedMovieId}/${row}/${num}`, {
    method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username: session.username, role: session.role})
  });
  loadSeats(selectedMovieId);
}

async function addMovie() {
  const name = document.getElementById('add-name').value;
  const duration = parseInt(document.getElementById('add-duration').value);
  const start = document.getElementById('add-start').value;
  await fetch(`${API}/movies`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, duration_minutes: duration, start_time: start}) });
  loadMovies();
}

async function deleteMovie(id) {
  if (confirm("Delete this movie?")) {
    await fetch(`${API}/movies/${id}`, {method:'DELETE'}); loadMovies();
  }
}
</script>
</body>
</html>
"""

PORT = 9000
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
        self.wfile.write(HTML.encode())
    def log_message(self, format, *args): pass

class ReusableServer(socketserver.TCPServer): allow_reuse_address = True

if __name__ == "__main__":
    with ReusableServer(("", PORT), Handler) as server:
        print(f"✅ Cinema Pro running at http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        server.serve_forever()
