from flask import Flask
from flask import render_template
import sqlite3
import csv
import os


app = Flask("__main__")

#==========================================================
DB_FILE = "data.db"
os.remove(DB_FILE)
db = sqlite3.connect(DB_FILE)
c = db.cursor()

usernames = []
passwords = []
bios = []

links = []
names = []
content = []

c.execute("DROP TABLE IF EXISTS account")
c.execute("DROP TABLE IF EXISTS page")

c.execute("CREATE TABLE account (user TEXT, password TEXT, bios TEXT)")
c.execute("CREATE TABLE page (link TEXT, name TEXT, content TEXT)")

for i in range(len(usernames)):
    c.execute("INSERT INTO account VALUES (?, ?, ?)", (username[i], passwords[i], bios[i]))
for i in range(len(links)):
    c.execute("INSERT INTO page VALUES (?, ?, ?)", (links[i], names[i], content[i]))

#==========================================================

@app.route("/")
def homepage():
    return "this is homepage"

app.debug = True
app.run()
