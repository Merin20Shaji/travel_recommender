from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# MySQL connection setup
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',  # Replace with your MySQL username
        password='dbms@123',  # Replace with your MySQL password
        database='tour_booking'
    )

travel_data = {
    "Paris": {
        "image": "paris.jpg",
        "activities": ["Eiffel Tower visit", "Seine River Cruise"],
       "places_to_visit": [
            {"name": "Louvre Museum", "map_link": "https://www.google.com/maps?q=Louvre+Museum"},
            {"name": "Notre-Dame", "map_link": "https://www.google.com/maps?q=Notre+Dame"}
        ],
        "famous_food_spots": [
            {"name": "Le Meurice", "map_link": "https://www.google.com/maps?q=Le+Meurice+Paris"},
            {"name": "Pierre Hermé", "map_link": "https://www.google.com/maps?q=Pierre+Hermé+Paris"}
        ]
    },
    "Tokyo": {
        "image": "tokyo.jpeg",
        "activities": ["Senso-ji Temple tour", "Tsukiji Fish Market visit"],
       "places_to_visit": [
            {"name": "Tokyo Skytree", "map_link": "https://www.google.com/maps?q=Tokyo+Skytree"},
            {"name": "Shibuya Crossing", "map_link": "https://www.google.com/maps?q=Shibuya+Crossing"}
        ],
        "famous_food_spots": [
            {"name": "Ichiran Ramen", "map_link": "https://www.google.com/maps?q=Ichiran+Ramen+Tokyo"},
            {"name": "Sushi Dai", "map_link": "https://www.google.com/maps?q=Sushi+Dai+Tokyo"}
        ]
    }
}


# Default Route (Login page)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('index.html', css_url=url_for('static', filename='styles.css'))

# Sign Up Page Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', 
                           (username, email, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')

    return render_template('signup.html', css_url=url_for('static', filename='styles.css'))

# Home Page Route (Accessible after login)
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    user_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    return render_template('home.html', cities=travel_data ,cs_url=url_for('static', filename='style.css'))

@app.route('/city/<city>')
def city_details(city):
    if city in travel_data:
        return render_template("city.html", city=city, data=travel_data[city],cs_url=url_for('static', filename='style.css'))
    return jsonify({"message": "City not found"}), 404

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Tour Booking Page: User selects a tour
@app.route('/book/<int:tour_id>', methods=['GET', 'POST'])
def book(tour_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tours WHERE id = %s', (tour_id,))
    tour = cursor.fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        cursor.execute('INSERT INTO bookings (name, email, tour_id) VALUES (%s, %s, %s)', 
                       (name, email, tour_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Booking confirmed!', 'success')
        return redirect(url_for('home'))

    cursor.close()
    conn.close()
    return render_template('book.html', tour=tour, css_url=url_for('static', filename='styles.css'))

if __name__ == '__main__':
    app.run(debug=True)
