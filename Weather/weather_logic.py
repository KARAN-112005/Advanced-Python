"""
weather_logic.py - Pure API-calling and parsing logic for the Weather App
(Advanced Tier)
------------------------------------------------------------------------------
Kept separate from the GUI so it can be tested without opening a window
or needing a live internet connection for every check.

Uses OpenWeatherMap's free "Current Weather" and "5 day / 3 hour
Forecast" endpoints (the free tier does not offer a true hour-by-hour
forecast, so "next 6 hours" is approximated using the first two
3-hour forecast steps - documented in the README).
"""

import datetime
import requests

CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
IP_LOCATION_URL = "https://ipinfo.io/json"
ICON_URL_TEMPLATE = "https://openweathermap.org/img/wn/{icon_code}@2x.png"


class WeatherError(Exception):
    """Raised for any weather/location lookup failure, so the GUI can
    show a friendly in-window message instead of crashing."""
    pass


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


def icon_url(icon_code):
    """Build the full image URL for an OpenWeatherMap icon code (e.g. '04d')."""
    return ICON_URL_TEMPLATE.format(icon_code=icon_code)


def fetch_current_weather(city, api_key):
    """Call the Current Weather API and return the parsed JSON dict."""
    params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(CURRENT_URL, params=params, timeout=8)
    except requests.exceptions.Timeout:
        raise WeatherError("The request timed out. Check your internet connection.")
    except requests.exceptions.ConnectionError:
        raise WeatherError("Couldn't connect to the weather service.")

    if response.status_code == 404:
        raise WeatherError(f"City '{city}' not found. Check the spelling.")
    if response.status_code == 401:
        raise WeatherError("Invalid API key. Check config in weather_gui_advanced.py.")
    if response.status_code != 200:
        raise WeatherError(f"Weather service error (status {response.status_code}).")

    return response.json()


def fetch_forecast(city, api_key):
    """Call the 5 day / 3 hour Forecast API and return the parsed JSON dict."""
    params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=8)
    except requests.exceptions.Timeout:
        raise WeatherError("The forecast request timed out.")
    except requests.exceptions.ConnectionError:
        raise WeatherError("Couldn't connect to the weather service.")

    if response.status_code == 404:
        raise WeatherError(f"City '{city}' not found.")
    if response.status_code == 401:
        raise WeatherError("Invalid API key.")
    if response.status_code != 200:
        raise WeatherError(f"Weather service error (status {response.status_code}).")

    return response.json()


def parse_hourly(forecast_json, count=2):
    """
    Return the next `count` forecast steps (each 3 hours apart) as a
    list of dicts: {time, temp, description, icon}.
    Approximates "next 6 hours" using 2 steps of the free tier's
    3-hour forecast data.
    """
    entries = forecast_json.get("list", [])[:count]
    results = []
    for entry in entries:
        time_str = datetime.datetime.fromtimestamp(entry["dt"]).strftime("%H:%M")
        results.append({
            "time": time_str,
            "temp": entry["main"]["temp"],
            "description": entry["weather"][0]["description"],
            "icon": entry["weather"][0]["icon"],
        })
    return results


def parse_daily(forecast_json, days=5):
    """
    Reduce the 3-hour-step forecast list down to one entry per day
    (the one closest to 12:00), for up to `days` days, as a list of
    dicts: {date, temp, description, icon}.
    """
    entries = forecast_json.get("list", [])
    by_date = {}

    for entry in entries:
        dt = datetime.datetime.fromtimestamp(entry["dt"])
        date_key = dt.date()
        hour_distance_from_noon = abs(dt.hour - 12)

        if date_key not in by_date or hour_distance_from_noon < by_date[date_key][0]:
            by_date[date_key] = (hour_distance_from_noon, entry)

    results = []
    for date_key in sorted(by_date.keys())[:days]:
        _, entry = by_date[date_key]
        results.append({
            "date": date_key.strftime("%a %d %b"),
            "temp": entry["main"]["temp"],
            "description": entry["weather"][0]["description"],
            "icon": entry["weather"][0]["icon"],
        })
    return results


def get_location_by_ip():
    """
    Look up the user's approximate city using their IP address via
    ipinfo.io's free tier. Returns the city name as a string.
    """
    try:
        response = requests.get(IP_LOCATION_URL, timeout=6)
    except requests.exceptions.RequestException:
        raise WeatherError("Couldn't detect your location automatically.")

    if response.status_code != 200:
        raise WeatherError("Location service returned an error.")

    data = response.json()
    city = data.get("city")
    if not city:
        raise WeatherError("Couldn't determine a city from your location.")
    return city
