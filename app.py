# importing required libraries
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
from weather_api import get_weather
from prometheus_client import Counter
from prometheus_client import Gauge
from dotenv import load_dotenv


class ColorFormatter(logging.Formatter):
    # adding ANSI escape codes for colors
    COLORS = {
        'DEBUG': '\033[37m',  # White
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[41m',  # Red background
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# adding colored printing for console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter(
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%d-%m-%Y %H:%M'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler],
    force=True)

# loading .env file and reading the API key (ensures API key stays private and is not hardcoded)
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


# creating Flask app instance
app = Flask(__name__)
app.logger.info("Weather app started.")

# add /metrics endpoint to our city weather app (prometheus_flask_exporter will push our metrics to /metrics endpoint)
metrics = PrometheusMetrics(app)

# setting custom prometheus metrics
city_weather_requests_total = Counter("city_weather_requests_total",
                                      "Total number of city weather requests including invalid requests")
invalid_city_search_total = Counter("invalid_city_search_total", "Number of times an invalid city was entered")
api_usage_limit_exceed_total = Counter("api_usage_limit_exceed_total", "Number of times API usage limit was exceeded")
city_search_count_total = Counter("city_search_count_total", "Number of times each city was searched", ["city"])
temp_unit_selection_total = Counter("temp_unit_selection_total",
                                    "Number of times each temperature unit (°C/°F) was requested", ["temp_unit"])
city_temperature_value = Gauge("city_temperature_value", "Latest reported temperature of selected city in Celsius",
                               ["city", "temp_unit"])


# call this function when user accesses (GET) or submits a request (POST) to homepage
@app.route("/", methods=["GET", "POST"])
def home():
    # if user has submitted the request (i.e. typed a city name)
    if request.method == "POST":
        app.logger.info("POST request received on '/' route.")
        # incrementing city weather requests counter
        city_weather_requests_total.inc()

        # get the entered city name and the units (Celsius or Fahrenheit)
        city = request.form.get("city", "").strip()
        unit = request.form.get("units", "metric")

        app.logger.info(f"User submitted city: {city} with unit: {unit}")

        # call function to fetch weather data from OpenWeather API
        weather_data = get_weather(city, API_KEY, unit=unit)

        # if error is returned by get_weather function, fill placeholders for all weather information
        if weather_data.get("error"):
            app.logger.error(f"Error fetching weather for {city}: {weather_data['error']}")
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
                app.logger.error(f"Invalid city searched: {city}")
                # incrementing invalid city search counter
                invalid_city_search_total.inc()
            elif weather_data["error"] == "API limit reached. Please wait and try again later.":
                app.logger.error("API limit reached.")
                # incrementing api_usage_limit_exceed_total counter
                api_usage_limit_exceed_total.inc()
        else:
            app.logger.info(f"Weather data fetched successfully for: {city}")

            # adding the unit key in weather_data dict
            weather_data["unit"] = unit

            # incrementing temp_unit_selection_total counter
            temp_unit_selection_total.labels(temp_unit=unit).inc()

            # incrementing counter for city_searches_total
            city_search_count_total.labels(city=city.lower()).inc()

            # noting the latest temperature value of current city
            try:
                temperature = float(weather_data["temperature"])
                city_temperature_value.labels(city=city.lower(), temp_unit=unit).set(temperature)
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
