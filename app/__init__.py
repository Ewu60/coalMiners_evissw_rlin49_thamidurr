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
    c.execute("INSERT INTO page (link, name, content) VALUES (?, ?, ?)", (link, name, text))
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
            return redirect(url_for("homepage"))
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

@app.route("/homepage")
def homepage():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("homepage.html")
if __name__ == "__main__":
    app.debug = True
    app.run()
