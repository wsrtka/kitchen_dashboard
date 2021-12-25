"""Contains main web app entry point."""


from flask import Flask, render_template

from src.apis import get_weather_data


app = Flask(__name__)

@app.route('/')
def index():
    get_weather_data()
    return render_template('dashboard.html')
