# importing required libraries
import os
from datetime import datetime
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
from weather_api import get_weather
# for reading API key securely, we will use dotenv
from dotenv import load_dotenv

# loading .env file and reading the API key (ensures API key stays private and is not hardcoded)
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# creating Flask app instance
app = Flask(__name__)
# add /metrics endpoint to our city weather app (so that our metrics become available at /metrics endpoint)
metrics = PrometheusMetrics(app)


# call this function when user accesses (GET) or submits a request (POST) to homepage
@app.route("/", methods=["GET", "POST"])
def home():
    # if user has submitted the request (i.e. typed a city name)
    if request.method == "POST":
        # get the entered city name and the units (Celsius or Fahrenheit)
        city = request.form.get("city", "").strip()
        unit = request.form.get("units", "metric")

        # call function to fetch weather data from OpenWeather API
        weather_data = get_weather(city, API_KEY, unit=unit)

        # if error is returned by get_weather function, fill placeholders for all weather information
        if weather_data.get("error"):
            weather_data = {
                "city": "",
                "country": "---",
                "temperature": "---",
                "humidity": "---",
                "sky": "---",
                "wind": "---",
                "icon": None,
                "local_time": "---",
                "sunrise": "---",
                "sunset": "---",
                "error": weather_data["error"],
                "unit": unit
            }
        else:
            # adding the unit key in weather_data dict
            weather_data["unit"] = unit

    else:
        # show default placeholders on initial url load
        weather_data = {
            "city": "",
            "country": "---",
            "temperature": "---",
            "humidity": "---",
            "sky": "---",
            "wind": "---",
            "icon": None,
            "local_time": "---",
            "sunrise": "---",
            "sunset": "---",
            "error": None,
            "unit": "metric"
        }

    # setting the current data
    current_date = datetime.now().strftime("%d.%m.%Y")
    # sending all weather data to html for rendering
    return render_template("index.html", weather=weather_data, date=current_date)


# Start the Flask server in debug mode
if __name__ == "__main__":
    app.run()
