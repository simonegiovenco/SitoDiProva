from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "chiave_segreta"

# Creazione della cartella per salvare i file (immagini e video)
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

# Creazione del database e della tabella dei contenuti
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Funzione per aggiungere contenuti
def add_content(title, content_type, content):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO content (title, content_type, content) VALUES (?, ?, ?)", (title, content_type, content))
    conn.commit()
    conn.close()

# Home page
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("dashboard"))  # Reindirizza l'admin alla dashboard
        else:
            return "Login fallito!"

    return render_template("login.html")


# Dashboard (per l'admin)
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content")
        contents = cursor.fetchall()
        conn.close()
        return render_template("dashboard.html", contents=contents)
    return redirect("/login")

# Pagina per postare contenuti
@app.route("/post_content", methods=["GET", "POST"])
def post_content():
    if "user" in session:
        if request.method == "POST":
            title = request.form["title"]
            content_type = request.form["content_type"]
            content = request.form["content"]

            if content_type == "image" or content_type == "video":
                file = request.files["file"]
                filename = os.path.join('static/uploads', file.filename)
                file.save(filename)
                content = filename  # Salviamo solo il percorso del file

            add_content(title, content_type, content)
            return redirect("/dashboard")

        return render_template("post_content.html")

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
