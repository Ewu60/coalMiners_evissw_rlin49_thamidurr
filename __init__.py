from flask import Flask
from flask import render_template

app = Flask("__main__")

@app.route("/")
def homepage():
    return "this is homepage"

app.debug = True
app.run()
