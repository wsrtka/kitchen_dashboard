"""Contains main web app entry point."""


from flask import Flask, render_template

from src.utils import setup_logger, prepare_mpk_data, remove_redundant_lines, get_rain_message
from src.apis import get_weather_data, get_departures, LOCATION


app = Flask(__name__)


@app.route('/')
def index():
    # initialize additional services
    setup_logger()

    # get api data
    szwedzka_data = get_departures('szwedzka')
    grunwaldzkie_data = get_departures('grunwaldzkie')
    weather_data = get_weather_data()

    # filter data
    szwedzka_data = prepare_mpk_data(szwedzka_data)
    grunwaldzkie_data = prepare_mpk_data(grunwaldzkie_data)
    grunwaldzkie_data = remove_redundant_lines(szwedzka_data, grunwaldzkie_data)
    weather_data['rain'] = get_rain_message(weather_data)

    # render site
    return render_template('dashboard.html', 
                            location=LOCATION, 
                            weather=weather_data, 
                            szwedzka=szwedzka_data, 
                            grunwaldzkie=grunwaldzkie_data
                        )
