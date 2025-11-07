from flask import Flask
from flask import render_template
import sqlite3
import csv
import os
from flask import request
from flask import session
from flask import redirect, url_for

app = Flask("__main__")

#==========================================================
DB_FILE = "static/data.db"
os.remove(DB_FILE)
db = sqlite3.connect(DB_FILE)
c = db.cursor()

usernames = ["ricky", "ewu"]
passwords = ["rickyp", "ewup"]
bios = ["rickys", "ewus"]

links = []
names = []
content = []

c.execute("DROP TABLE IF EXISTS account")
c.execute("DROP TABLE IF EXISTS page")

c.execute("CREATE TABLE account (user TEXT, password TEXT, bios TEXT)")
c.execute("CREATE TABLE page (link TEXT, name TEXT, content TEXT)")

for i in range(len(usernames)):
    c.execute("INSERT INTO account VALUES (?, ?, ?)", (usernames[i], passwords[i], bios[i]))
for i in range(len(links)):
    c.execute("INSERT INTO page VALUES (?, ?, ?)", (links[i], names[i], content[i]))

def add_account(username, password, bio=""):
    usernames.append(username)
    passwords.append(password)
    bios.append(bio)

def add_page(link, name, content=""):
    links.append(link)
    names.append(name)
    content.append(content)

def get_pass(username):
    for i in range(len(usernames)):
        if usernames[i] == username:
            return(passwords[i])
    return("temp")

#==========================================================
app = Flask(__name__)    #create Flask object

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/", methods=['GET', 'POST'])
def disp_loginpage():
    return render_template( 'login.html' )
def index():
    if name in session:
        return f'Logged in as {session["username"]}'
    return 'You are not logged in'
@app.route("/auth", methods = ['GET', 'POST'])
def authenticate():
    user = request.form["username"]
    return render_template('response.html', username = user, method = request.method)


@app.route("/exit")
def exit():
    session.pop("username", None)
    return redirect(url_for('disp_loginpage'))

app.debug = True
app.run()
