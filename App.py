from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Results table taake career path save ho sakay
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recommendation TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    # Home page par purana result dikhane ke liye data fetch karna
    last_result = None
    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT recommendation FROM results WHERE user_id=? ORDER BY id DESC LIMIT 1", (session['user_id'],))
        row = cursor.fetchone()
        if row:
            last_result = row[0]
        conn.close()
    
    return render_template('AI.html', last_result=last_result)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('fullname')
        email = request.form.get('email')
        pwd = request.form.get('password')
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)", (name, email, pwd))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            return "Email already exists!"
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, pwd))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('home'))
        else:
            return "Invalid Login!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    prediction = None
    if request.method == 'POST':
        interest = request.form.get('interest')
        gpa_val = request.form.get('gpa')
        gpa = float(gpa_val) if gpa_val else 0
        
        # --- INTELLIGENT AI GUIDANCE LOGIC ---
        if interest == 'coding':
            if gpa >= 3.5:
                prediction = "Artificial Intelligence & Data Science Engineer"
            elif 2.5 <= gpa < 3.5:
                prediction = "Full-Stack Web & Software Developer"
            else:
                prediction = "Tech Support & Frontend Web Designer"

        elif interest == 'design':
            if gpa >= 3.0:
                prediction = "UI/UX Product Designer (Digital Architecture)"
            else:
                prediction = "Creative Graphic Designer & Brand Specialist"

        elif interest == 'business':
            if gpa >= 3.2:
                prediction = "Fintech Analyst & Data-Driven Marketer"
            else:
                prediction = "E-Commerce Specialist & Digital Sales Manager"

        elif interest == 'science':
            if gpa >= 3.4:
                prediction = "Bio-Informatics & Healthcare Data Scientist"
            else:
                prediction = "Health Informatics & Clinical IT Support"
                
        else:
            prediction = "General AI Fundamentals & Tech Literacy Path"
        
        # SAVE TO DATABASE: Prediction ko database mein save karna
        # SAVE TO DATABASE: Prediction ko database mein save karna
        if prediction:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO results (user_id, recommendation) VALUES (?, ?)", (session['user_id'], prediction))
            conn.commit()
            conn.close()
            
    return render_template('assessment.html', prediction=prediction)
if __name__ == '__main__':
    app.run(debug=True)