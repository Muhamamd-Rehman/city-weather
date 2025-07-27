# importing required libraries
import os
from datetime import datetime
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
from weather_api import get_weather
from prometheus_client import Counter
from prometheus_client import Gauge
from dotenv import load_dotenv

# loading .env file and reading the API key (ensures API key stays private and is not hardcoded)
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# creating Flask app instance
app = Flask(__name__)
# add /metrics endpoint to our city weather app (so that our metrics become available at /metrics endpoint)
metrics = PrometheusMetrics(app)

# setting custom prometheus metrics
city_weather_requests_total = Counter("city_weather_requests_total", "Total number of city weather requests including invalid requests")
invalid_city_search_total = Counter("invalid_city_search_total", "Number of times an invalid city was entered")
api_usage_limit_exceed_total = Counter("api_usage_limit_exceed_total", "Number of times API usage limit was exceeded")
city_searches_total = Counter("city_searches_total", "Number of times each city was searched", ["city"])
temp_unit_selection_total = Counter("temp_unit_selection_total", "Number of times each temperature unit (°C/°F) was requested", ["temp_unit"])
city_temperature_value = Gauge("city_temperature_value", "Latest reported temperature of selected city in Celsius", ["city"])


# call this function when user accesses (GET) or submits a request (POST) to homepage
@app.route("/", methods=["GET", "POST"])
def home():
    # if user has submitted the request (i.e. typed a city name)
    if request.method == "POST":
        # incrementing city weather requests counter
        city_weather_requests_total.inc()

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
                "unit": unit}

            if weather_data["error"] == "City not found!":
                # incrementing invalid city search counter
                invalid_city_search_total.inc()
            elif weather_data["error"] == "API limit reached. Please wait and try again later.":
                # incrementing api_usage_limit_exceed_total counter
                api_usage_limit_exceed_total.inc()
        else:
            # adding the unit key in weather_data dict
            weather_data["unit"] = unit

            # incrementing temp_unit_selection_total counter
            temp_unit_selection_total.labels(temp_unit=unit).inc()

            # incrementing counter if specific city has been searched
            city_lower = weather_data["city"].lower()
            if city_lower in ["ulm", "melbourne", "seattle", "lahore", "jakarta", "doha", "rawalpindi", "hamburg"]:
                city_searches_total.labels(city=city_lower).inc()

            # noting the latest temperature value of current city
            try:
                temperature = float(weather_data["temperature"])
                city_temperature_value.labels(city=city).set(temperature)
            except (ValueError, TypeError):
                pass
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
