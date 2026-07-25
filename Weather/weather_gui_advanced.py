"""
weather_gui_advanced.py - Basic Weather App (Advanced Tier) - GUI
----------------------------------------------------------------------
A tkinter desktop app that shows current weather, a 6-hour forecast, a
5-day forecast, weather icons, a Celsius/Fahrenheit toggle, and
optional automatic location detection via your IP address.

Run this file directly to open the window.

Setup required before running - see README.md:
1. Create a free OpenWeatherMap account and API key
2. Paste it into API_KEY below, or set the OPENWEATHERMAP_API_KEY
   environment variable
"""

import os
from io import BytesIO

import requests
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from weather_logic import (
    fetch_current_weather, fetch_forecast, parse_hourly, parse_daily,
    celsius_to_fahrenheit, icon_url, get_location_by_ip, WeatherError,
)

API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "PASTE_YOUR_API_KEY_HERE")


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App - Advanced")
        self.geometry("560x560")
        self.resizable(False, False)

        self.unit = "C"  # or "F" - toggled by the unit button
        self.current_json = None
        self.forecast_json = None
        self.icon_images = []  # keeps PhotoImage references alive

        self._build_widgets()

    def _build_widgets(self):
        top = ttk.Frame(self)
        top.pack(pady=12)

        self.city_entry = ttk.Entry(top, width=24)
        self.city_entry.grid(row=0, column=0, padx=5)
        self.city_entry.insert(0, "Enter a city name")

        ttk.Button(top, text="Get Weather", command=self.on_get_weather).grid(row=0, column=1, padx=5)
        ttk.Button(top, text="Use My Location", command=self.on_use_location).grid(row=0, column=2, padx=5)
        self.unit_button = ttk.Button(top, text="Switch to °F", command=self.on_toggle_unit)
        self.unit_button.grid(row=0, column=3, padx=5)

        # Errors are shown here, in the window - never just printed to a terminal
        self.error_label = tk.Label(self, text="", fg="#dc2626", font=("Segoe UI", 10, "bold"))
        self.error_label.pack(pady=(0, 5))

        # --- current weather panel ---
        current_frame = ttk.LabelFrame(self, text="Current Weather")
        current_frame.pack(padx=15, pady=8, fill="x")

        self.current_icon_label = tk.Label(current_frame)
        self.current_icon_label.grid(row=0, column=0, rowspan=3, padx=10, pady=8)

        self.city_label = tk.Label(current_frame, text="", font=("Segoe UI", 14, "bold"))
        self.city_label.grid(row=0, column=1, sticky="w")
        self.temp_label = tk.Label(current_frame, text="", font=("Segoe UI", 20))
        self.temp_label.grid(row=1, column=1, sticky="w")
        self.desc_label = tk.Label(current_frame, text="", font=("Segoe UI", 11))
        self.desc_label.grid(row=2, column=1, sticky="w")

        # --- hourly forecast panel (next 6 hours) ---
        hourly_frame = ttk.LabelFrame(self, text="Next 6 Hours")
        hourly_frame.pack(padx=15, pady=8, fill="x")
        self.hourly_slots = []
        for i in range(2):  # free-tier data is in 3-hour steps: 2 steps = 6 hours
            slot = ttk.Frame(hourly_frame)
            slot.pack(side="left", expand=True, padx=15, pady=8)
            icon_lbl = tk.Label(slot)
            icon_lbl.pack()
            time_lbl = tk.Label(slot, font=("Segoe UI", 9, "bold"))
            time_lbl.pack()
            temp_lbl = tk.Label(slot, font=("Segoe UI", 9))
            temp_lbl.pack()
            self.hourly_slots.append((icon_lbl, time_lbl, temp_lbl))

        # --- daily forecast panel (next 5 days) ---
        daily_frame = ttk.LabelFrame(self, text="Next 5 Days")
        daily_frame.pack(padx=15, pady=8, fill="x")
        self.daily_slots = []
        for i in range(5):
            slot = ttk.Frame(daily_frame)
            slot.pack(side="left", expand=True, padx=8, pady=8)
            icon_lbl = tk.Label(slot)
            icon_lbl.pack()
            date_lbl = tk.Label(slot, font=("Segoe UI", 8, "bold"))
            date_lbl.pack()
            temp_lbl = tk.Label(slot, font=("Segoe UI", 8))
            temp_lbl.pack()
            self.daily_slots.append((icon_lbl, date_lbl, temp_lbl))

    def show_error(self, message):
        self.error_label.config(text=message)

    def clear_error(self):
        self.error_label.config(text="")

    def _load_icon(self, icon_code, size=(50, 50)):
        """Download a weather icon and return a PhotoImage, or None on failure."""
        try:
            response = requests.get(icon_url(icon_code), timeout=6)
            image = Image.open(BytesIO(response.content)).resize(size)
            photo = ImageTk.PhotoImage(image)
            self.icon_images.append(photo)  # prevent garbage collection
            return photo
        except Exception:
            return None

    def _format_temp(self, celsius):
        if self.unit == "F":
            return f"{celsius_to_fahrenheit(celsius):.1f}°F"
        return f"{celsius:.1f}°C"

    def on_get_weather(self):
        city = self.city_entry.get().strip()
        if not city or city == "Enter a city name":
            self.show_error("Please enter a city name.")
            return
        self._fetch_and_render(city)

    def on_use_location(self):
        self.clear_error()
        try:
            city = get_location_by_ip()
        except WeatherError as e:
            self.show_error(str(e))
            return
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, city)
        self._fetch_and_render(city)

    def on_toggle_unit(self):
        self.unit = "F" if self.unit == "C" else "C"
        self.unit_button.config(text="Switch to °C" if self.unit == "F" else "Switch to °F")
        if self.current_json and self.forecast_json:
            self._render_all()

    def _fetch_and_render(self, city):
        self.clear_error()

        if API_KEY == "PASTE_YOUR_API_KEY_HERE":
            self.show_error("No API key set. Add one in weather_gui_advanced.py.")
            return

        try:
            self.current_json = fetch_current_weather(city, API_KEY)
            self.forecast_json = fetch_forecast(city, API_KEY)
        except WeatherError as e:
            self.show_error(str(e))
            return

        self._render_all()

    def _render_all(self):
        current = self.current_json
        self.city_label.config(text=current["name"])
        self.temp_label.config(text=self._format_temp(current["main"]["temp"]))
        self.desc_label.config(text=current["weather"][0]["description"].title())
        icon = self._load_icon(current["weather"][0]["icon"], size=(70, 70))
        self.current_icon_label.config(image=icon)

        hourly = parse_hourly(self.forecast_json, count=2)
        for i, (icon_lbl, time_lbl, temp_lbl) in enumerate(self.hourly_slots):
            if i < len(hourly):
                entry = hourly[i]
                icon_lbl.config(image=self._load_icon(entry["icon"]))
                time_lbl.config(text=entry["time"])
                temp_lbl.config(text=self._format_temp(entry["temp"]))

        daily = parse_daily(self.forecast_json, days=5)
        for i, (icon_lbl, date_lbl, temp_lbl) in enumerate(self.daily_slots):
            if i < len(daily):
                entry = daily[i]
                icon_lbl.config(image=self._load_icon(entry["icon"]))
                date_lbl.config(text=entry["date"])
                temp_lbl.config(text=self._format_temp(entry["temp"]))


if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
