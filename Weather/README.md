# Task 4 – Basic Weather App (Advanced Tier)

A desktop GUI weather app: enter a city (or auto-detect your location),
see the current conditions with an icon, a 6-hour outlook, and a
5-day forecast — with a one-click °C/°F toggle.

## Project Files

- `weather_gui_advanced.py` — run this one; it opens the window
- `weather_logic.py` — all the API calls and data parsing (no GUI code)
- `requirements.txt` — the extra libraries you need to install

## Concepts Practiced

**Two different OpenWeatherMap endpoints**
- `/weather` gives the **current** conditions for a city.
- `/forecast` gives a **5 day / 3 hour** forecast — a list of weather
  snapshots spaced 3 hours apart, covering the next 5 days.

The free tier doesn't offer a true hour-by-hour forecast, so "next 6
hours" is approximated using the first 2 of those 3-hour steps
(2 × 3 hours = 6 hours) — a good example of working within a real
API's actual limits instead of assuming it does everything you want.

**Reducing a big list down to one entry per day**
`parse_daily()` groups the 3-hour forecast entries by calendar date,
and for each date keeps only the one closest to 12:00 noon — giving a
sensible single "daytime" snapshot per day instead of showing all 8
entries per day.

**Downloading and displaying images with Pillow**
```python
response = requests.get(icon_url, timeout=6)
image = Image.open(BytesIO(response.content)).resize(size)
photo = ImageTk.PhotoImage(image)
```
Weather icons come from OpenWeatherMap as PNG files at a URL.
`requests` downloads the raw bytes, `BytesIO` treats those bytes like a
file so `PIL.Image.open()` can read them without saving to disk, and
`ImageTk.PhotoImage` converts the result into something tkinter can display.

**Why icon images are stored in a list (`self.icon_images`)**
tkinter doesn't keep its own reference to `PhotoImage` objects — if
Python's garbage collector cleans up the only reference, the image
silently disappears from the screen. Keeping every icon in
`self.icon_images` keeps them alive for as long as the app is running.

**Storing raw data separately from the currently-displayed unit**
The app always requests data in Celsius and stores the raw JSON in
`self.current_json` / `self.forecast_json`. Toggling the unit doesn't
re-call the API — it just re-runs `_render_all()`, converting to
Fahrenheit on the fly with `celsius_to_fahrenheit()` only where needed
for display. This avoids unnecessary API calls.

**A custom exception for all weather/location failures (`WeatherError`)**
Every possible failure — timeout, connection error, bad API key, city
not found, IP lookup failure — gets turned into one consistent
`WeatherError` with a clear message. The GUI only needs one
`except WeatherError` block, and shows the message in `self.error_label`
inside the window — never a raw traceback or `print()` statement.

**Auto-location via IP address (`ipinfo.io`)**
`get_location_by_ip()` calls a free IP-geolocation service that looks
up an approximate city based on your public IP address, with no API
key needed for basic use. This is only an approximation — sometimes
accurate to your ISP's city rather than your exact location.

## How to Run It

1. **Get a free OpenWeatherMap API key** at https://openweathermap.org/
   (same as the beginner tier — reuse the same key if you already have one).
2. Add it one of two ways:
   - Open `weather_gui_advanced.py` and replace `"PASTE_YOUR_API_KEY_HERE"`, or
   - Set the environment variable:
     ```
     export OPENWEATHERMAP_API_KEY=your_key_here
     ```
3. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
4. Run the program:
   ```
   python weather_gui_advanced.py
   ```
5. Type a city and click **Get Weather**, or click **Use My Location**
   to auto-detect a city from your IP address.
6. Click **Switch to °F** / **Switch to °C** to toggle units instantly.

## What I Learned

- How to work with two different endpoints of the same API for
  different purposes (current vs. forecast).
- How to reduce a large, evenly-spaced dataset down to one
  representative entry per day.
- How to download an image over HTTP and display it in a tkinter GUI
  using Pillow, and why references to `PhotoImage` objects must be
  kept alive manually.
- How to cache raw API data and re-render it in different display
  units without making redundant network calls.
- How to centralize error handling into one custom exception type so
  the GUI layer stays simple and every failure shows up on-screen
  instead of in a terminal.
- How to use a third-party IP geolocation service for a rough
  "auto-detect my location" feature.
