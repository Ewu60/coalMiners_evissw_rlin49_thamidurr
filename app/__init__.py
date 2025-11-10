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
    c.execute("CREATE TABLE page (link TEXT, name TEXT, content TEXT, author TEXT)")
    usernames = ["ricky", "ewu"]
    passwords = ["rickyp", "ewup"]
    bios = ["rickys", "ewus"]
    for i in range(len(usernames)):
        c.execute("INSERT INTO account VALUES (?, ?, ?)", (usernames[i], passwords[i], bios[i]))
    links = []
    names = []
    content = []
    for i in range(len(links)):
        c.execute("INSERT INTO page VALUES (?, ?, ?)", (links[i], names[i], content[i], "anonymous"))
    db.commit()
    db.close()
#==========================================================

def add_account(username, password, bio=""):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("INSERT INTO account VALUES (?, ?, ?)", (username, password, bio))
    db.commit()
    db.close()

def add_page(link, name, text="", username=None):
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()

    c.execute("PRAGMA table_info(page)")
    cols = [r[1] for r in c.fetchall()]
    if 'author' not in cols:
        try:
            c.execute("ALTER TABLE page ADD COLUMN author TEXT DEFAULT 'anonymous'")
        except sqlite3.OperationalError:
            pass

    if username is None:
        try:
            username = session.get('username')  # works when called inside a request
        except RuntimeError:
            username = None

    if not username:
        username = 'anonymous'

    c.execute(
        "INSERT OR IGNORE INTO page (link, name, content, author) VALUES (?, ?, ?, ?)",
        (link, name, text, username)
    )

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
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT content FROM page WHERE link = ?", (link,))
    row = c.fetchone()
    old_content = row[0] if row and row[0] is not None else ""
    if old_content.strip() == "":
        combined = new_text
    else:
        combined = new_text + "\n\n---\n\n" + old_content

    if editor is None:
        try:
            editor = session.get('username')
        except RuntimeError:
            editor = None
    if not editor:
        editor = 'anonymous'

    if row:
        c.execute("UPDATE page SET content = ?, author = ? WHERE link = ?", (combined, editor, link))
    else:
        name = link.replace('-', ' ').title()
        c.execute("INSERT INTO page (link, name, content, author) VALUES (?, ?, ?, ?)", (link, name, combined, editor))

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

@app.route("/page/<link>")
def view_page(link):
    page = get_page(link)
    if not page:
        return "Page not found", 404
    name = page[1]
    content = page[2]
    entries = get_history_parts(content)  # Split content history
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT author FROM page WHERE link = ?", (link,))
    author_row = c.fetchone()
    db.close()
    author = author_row[0] if author_row else ""
    # Pass 'entries', 'link' to template
    return render_template("page.html", name=name, entries=entries, author=author, username=session.get("username"), link=page[0])

@app.route("/homepage")
def homepage():
    if "username" not in session:
        return redirect(url_for("login"))
    pages = get_all_pages()  # Fetch pages from DB
    return render_template("homepage.html", username=session["username"], pages=pages)

@app.route("/newpage", methods=["GET", "POST"])
def new_page():
    if "username" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"].strip()
        link = name.replace(" ", "-").lower()
        content = request.form["content"].strip()
        add_page(link, name, content)
        return redirect(url_for("homepage"))
    return render_template("newpage.html", username=session["username"])

@app.route("/edit/<link>", methods=["GET", "POST"])
def edit_page(link):
    if "username" not in session:
        return redirect(url_for("login"))
    page = get_page(link)
    if not page:
        return "Page not found", 404
    name, content = page[1], page[2]
    db = sqlite3.connect(DB_FILE)
    c = db.cursor()
    c.execute("SELECT author FROM page WHERE link = ?", (link,))
    author_row = c.fetchone()
    db.close()
    author = author_row[0] if author_row else ""
    if author != session["username"]:
        return "You do not have permission to edit this page.", 403
    if request.method == "POST":
        new_content = request.form["content"].strip()
        update_page(link, new_content, editor=session["username"])
        return redirect(url_for("view_page", link=link))
    return render_template("editpage.html", name=name, content=content, link=link, username=session["username"])

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("profile.html", username=session["username"], blogarea="")

if __name__ == "__main__":
    app.debug = True
    app.run()
