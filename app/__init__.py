from flask import Flask
from flask import render_template
import sqlite3
import csv
import os
from flask import request
from flask import session
from flask import redirect, url_for

app = Flask(__name__)

#==========================================================
DB_FILE = os.path.join("static", "data.db")
if not os.path.exists(DB_FILE):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("CREATE TABLE account (user TEXT, password TEXT, bios TEXT)")
    c.execute("CREATE TABLE page (link TEXT, name TEXT, content TEXT)")

    usernames = ["ricky", "ewu"]
    passwords = ["rickyp", "ewup"]
    bios = ["rickys", "ewus"]

    for i in range(len(usernames)):
        c.execute("INSERT INTO account VALUES (?, ?, ?)", (usernames[i], passwords[i], bios[i]))
    links = []
    names = []
    content = []


    for i in range(len(links)):
        c.execute("INSERT INTO page VALUES (?, ?, ?)", (links[i], names[i], content[i]))
    db.commit()
    db.close()
#==========================================================


def add_account(username, password, bio=""):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("INSERT INTO account VALUES (?, ?, ?)", (username, password, bio))
    db.commit()
    db.close()

def add_page(link, name, text=""):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("INSERT OR IGNORE INTO page (link, name, content) VALUES (?, ?, ?)", (link, name, text))
    db.commit()
    db.close()

def get_pass(username):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT password FROM account WHERE user = ?", (username,))
    result = c.fetchone()
    db.close()
    if result:
        return result[0]
    return None

def get_all_pages():
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT * FROM page")
    pages = c.fetchall()
    db.close()
    return pages

def get_page(link):
    """Return (link, name, content) or None"""
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT link, name, content FROM page WHERE link = ?", (link,))
    row = c.fetchone()
    db.close()
    return row

def update_page(link, new_text, editor=None):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT content FROM page WHERE link = ?", (link,))
    row = c.fetchone()
    old_content = row[0] if row and row[0] is not None else ""

    meta = ""
    if editor:
        meta = f"\n\n-- edited by {editor} on {now} --"

    if old_content.strip() == "":
        combined = new_text + meta
    else:
        combined = new_text + meta + "\n\n---\n\n" + old_content

    if row:
        c.execute("UPDATE page SET content = ? WHERE link = ?", (combined, link))
    else:
        name = link.replace('-', ' ').title()
        c.execute("INSERT INTO page (link, name, content) VALUES (?, ?, ?)", (link, name, combined))
    db.commit()
    db.close()

def get_current_content(full_content):
    if not full_content:
        return ""
    parts = full_content.split("\n---\n", 1)
    return parts[0].strip()

def get_history_parts(full_content):
    if not full_content:
        return []
    parts = [p.strip() for p in full_content.split("\n---\n")]
    return parts
#==========================================================

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/", methods=['GET', 'POST'])
def index():
    if "username" in session:
        return f"Logged in as {session['username']}<br><a href='/logout'>Logout</a>"
    return redirect(url_for("login"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        stored_pass = get_pass(username)

        if stored_pass and stored_pass == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if get_pass(username) is not None:
            return render_template("register.html", error="Username already exists!")

        add_account(username, password)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/auth", methods = ['GET', 'POST'])
def authenticate():
    user = request.form["username"]
    return render_template('page.html', username = user, method = request.method)


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.debug = True
    app.run()
