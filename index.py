"""Contains main web app entry point."""


from flask import Flask, render_template

from src.apis import get_weather_data, setup_logger, LOCATION


app = Flask(__name__)

@app.route('/')
def index():
    setup_logger()
    weather_data = get_weather_data()
    return render_template('dashboard.html', location=LOCATION, weather=weather_data)
