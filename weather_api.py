# importing required libraries
import requests
from typing import Optional
from datetime import datetime


def get_weather(city: Optional[str], api_key: str, unit) -> dict:
    """
    Fetches current weather data for a given city using the OpenWeatherMap API.

    Parameters
    ----------
    city : str or None
        Name of the city to retrieve weather information for.
    api_key : str
        API key for authenticating with the OpenWeatherMap API.
    unit : str
        Metric for displaying the numerical values.

    Returns
    -------
    dict
        A dictionary containing complete weather data
    """
    # if city is None, return the error message
    # if not city:
    # return {"error": "City name is required."}

    # making the OpenWeatherMap API URL
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={unit}"

    # sending the GET request and retrieving the weather information
    response = requests.get(url)
    data = response.json()

    # checking if the request failed or city was not found, then returns dict with an error message
    if response.status_code != 200 or data.get("cod") != 200:
        return {"error": "City not found!"}

    # checking if we have reached the API usage limit
    if response.status_code == 429:
        return {"error": "API limit reached. Please wait and try again later."}

    # convert timestamps to local time
    timezone_offset = data["timezone"]
    local_time = datetime.utcfromtimestamp(data["dt"] + timezone_offset)
    sunrise_time = datetime.utcfromtimestamp(data["sys"]["sunrise"] + timezone_offset)
    sunset_time = datetime.utcfromtimestamp(data["sys"]["sunset"] + timezone_offset)

    # returning a dictionary with extracted weather details
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": round(data["main"]["temp"], 1),
        "humidity": data["main"]["humidity"],
        "sky": data["weather"][0]["description"].title(),
        "wind": data["wind"]["speed"],
        "icon": data["weather"][0]["icon"],
        "local_time": local_time.strftime(" %H:%M"),
        "sunrise": sunrise_time.strftime("%H:%M"),
        "sunset": sunset_time.strftime("%H:%M")}
