"""
Voice Assistant - Advanced Tier
--------------------------------
Builds on the beginner tier by adding:
- Natural language understanding (intent + entity parsing, not just
  keyword matching) via nlu.py
- Sending an email by voice command (smtplib)
- Timed reminders with an audible + spoken alert
- Live weather lookups (OpenWeatherMap API)
- Answering general knowledge questions from a local knowledge base
- Custom commands loaded from config.json (editable without touching code)

See README.md for the required config.json setup and a privacy note on
what data this program sends where.
"""

import datetime
import json
import os
import smtplib
import threading
import webbrowser
from email.mime.text import MIMEText

import speech_recognition as sr
import pyttsx3
import requests

from nlu import parse_intent

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

engine = pyttsx3.init()
engine.setProperty("rate", 175)


def load_config():
    """Load settings, custom commands, and the knowledge base from config.json."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def listen():
    """Capture one spoken command and return it as lowercase text, or None."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (speak now)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Please try again.")
            return None

    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you please repeat?")
        return None
    except sr.RequestError:
        speak("I'm having trouble reaching the speech recognition service.")
        return None


# ---------------------------------------------------------------
# Intent handlers - one function per thing the assistant can do
# ---------------------------------------------------------------

def handle_time_date():
    now = datetime.datetime.now()
    speak(f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %d %B %Y')}.")


def handle_weather(city, config):
    if not city:
        speak("Which city would you like the weather for?")
        return

    api_key = config.get("openweathermap_api_key", "")
    if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
        speak("No weather API key is set up in config.json yet.")
        return

    params = {"q": city, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(WEATHER_URL, params=params, timeout=8)
    except requests.exceptions.RequestException:
        speak("I couldn't reach the weather service. Check your internet connection.")
        return

    if response.status_code == 404:
        speak(f"I couldn't find a city called {city}.")
        return
    if response.status_code == 401:
        speak("The weather API key looks invalid.")
        return
    if response.status_code != 200:
        speak("Something went wrong fetching the weather.")
        return

    data = response.json()
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    speak(f"It's {temp:.1f} degrees Celsius and {description} in {city}.")


def handle_reminder(entities):
    amount = entities.get("amount")
    unit = entities.get("unit")
    message = entities.get("message") or "your reminder"

    if amount is None or unit is None:
        speak("Please tell me the reminder like: remind me in 10 minutes to check the oven.")
        return

    seconds_per_unit = {"second": 1, "minute": 60, "hour": 3600}
    delay_seconds = amount * seconds_per_unit[unit]

    def fire_alert():
        # The audible alert: a bell character plus a spoken message
        print("\a")  # terminal bell
        speak(f"Reminder: {message}")

    timer = threading.Timer(delay_seconds, fire_alert)
    timer.daemon = True
    timer.start()

    speak(f"Okay, I'll remind you to {message} in {amount} {unit}{'s' if amount != 1 else ''}.")


def handle_email(entities, config):
    to_address = entities.get("to")
    subject = entities.get("subject") or "(no subject)"
    body = entities.get("body") or ""

    if not to_address:
        speak("Who should I send the email to?")
        return

    email_config = config.get("email", {})
    sender = email_config.get("sender_address", "")
    password = email_config.get("sender_app_password", "")

    if not sender or password == "PASTE_YOUR_APP_PASSWORD_HERE":
        speak("Email isn't configured yet. Add your test account details to config.json.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_address

    try:
        with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [to_address], msg.as_string())
        speak(f"Email sent to {to_address}.")
    except smtplib.SMTPAuthenticationError:
        speak("Email login failed. Check the sender address and app password.")
    except Exception:
        speak("I couldn't send the email. Check your internet connection and settings.")


def handle_question(question, config):
    """Answer from the local knowledge base in config.json, if we have it."""
    knowledge_base = config.get("knowledge_base", {})

    # Try an exact match first, then a loose "contains" match
    if question in knowledge_base:
        speak(knowledge_base[question])
        return

    for key, answer in knowledge_base.items():
        if key in question or question in key:
            speak(answer)
            return

    speak("I don't have an answer for that in my knowledge base yet.")


def handle_web_search(topic):
    if not topic:
        speak("What would you like me to search for?")
        return
    speak(f"Searching the web for {topic}")
    webbrowser.open(f"https://www.google.com/search?q={topic.replace(' ', '+')}")


def handle_custom_command(command, config):
    """Check config.json's custom_commands for a matching trigger phrase."""
    for trigger, response in config.get("custom_commands", {}).items():
        if trigger in command:
            speak(response)
            return True
    return False


def handle_command(command, config):
    if command is None:
        return True

    # Custom commands (from config.json) get first priority, so users
    # can override or add behaviors without touching the code.
    if handle_custom_command(command, config):
        return True

    intent, entities = parse_intent(command)

    if intent == "exit":
        speak("Goodbye! Have a great day.")
        return False
    elif intent == "greeting":
        speak("Hello! How can I help you today?")
    elif intent == "time_date":
        handle_time_date()
    elif intent == "weather":
        handle_weather(entities.get("city"), config)
    elif intent == "set_reminder":
        handle_reminder(entities)
    elif intent == "send_email":
        handle_email(entities, config)
    elif intent == "question":
        handle_question(entities.get("question"), config)
    elif intent == "web_search":
        handle_web_search(entities.get("topic"))
    else:
        speak("I'm not sure how to help with that yet.")

    return True


def main():
    config = load_config()
    speak("Advanced voice assistant is ready. Ask me for the time, weather, "
          "to send an email, set a reminder, answer a question, search the "
          "web, or say 'exit' to quit.")

    running = True
    while running:
        command = listen()
        running = handle_command(command, config)


if __name__ == "__main__":
    main()
