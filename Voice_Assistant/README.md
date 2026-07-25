# Task 1 – Voice Assistant (Advanced Tier)

Everything from the beginner tier, plus: understanding free-form
sentences (not just fixed keywords), sending email by voice, timed
reminders, live weather, answering questions from a knowledge base,
and custom commands you can add without touching the code.

## Project Files

- `voice_assistant_advanced.py` — the main program (all the intent handlers)
- `nlu.py` — the "brain" that turns a sentence into an intent + details
- `config.json` — your settings, custom commands, and knowledge base (editable, no code needed)
- `requirements.txt` — libraries to install

## Concepts Practiced

**Natural language understanding with regular expressions (`re` module)**
Instead of only checking `if "time" in command`, `nlu.py` uses regex
patterns to pull structured details ("entities") out of a full
sentence. For example:
```python
re.search(r"in\s+(\d+)\s*(second|minute|hour)s?", text)
```
This matches "in 10 minutes" and "in 5 hours" alike, and captures the
number and unit separately — so "remind me in 10 minutes to check the
oven" and "in 10 minutes remind me to check the oven" both work, even
though the words are in a different order.

**Intent priority ordering**
Sentences can accidentally contain words that look like other intents —
e.g. an email with the word "hello" in the subject line shouldn't be
treated as a greeting. `nlu.py` checks the most specific intents
(email, reminder, weather) before the more general ones (greeting,
time), so specific matches win.

**Separating "understanding" from "doing"**
`nlu.py` only figures out *what* the user wants (the intent) and the
useful details (entities). `voice_assistant_advanced.py` has a separate
handler function for each intent that actually *does* something. This
separation makes each piece easier to test and reason about
independently — you can test the NLU logic without ever touching a
microphone.

**Sending email with `smtplib` and MIME messages**
```python
msg = MIMEText(body)
msg["Subject"] = subject
server.login(sender, password)
server.sendmail(sender, [to_address], msg.as_string())
```
`MIMEText` builds a properly formatted email message, and `smtplib`
handles the actual connection to the email server, login, and sending.

**Timed alerts with `threading.Timer`**
```python
timer = threading.Timer(delay_seconds, fire_alert)
timer.start()
```
`threading.Timer` schedules a function to run once, after a delay,
without blocking the rest of the program — so the assistant can keep
listening for other commands while a reminder counts down in the
background.

**Reading a JSON config file**
`config.json` holds your API key, email settings, custom commands, and
knowledge base as structured data. `json.load()` reads it into a Python
dictionary at startup, so you can change the assistant's behavior by
editing a text file — no code changes required.

**A simple local knowledge base**
Instead of a paid QA API, general knowledge questions are answered from
a dictionary in `config.json`. `handle_question()` looks for an exact
match first, then a loose "one contains the other" match, so slightly
different phrasing of the same question can still find an answer.

## Setting Up `config.json`

Open `config.json` and fill in:

```json
{
  "openweathermap_api_key": "your key from openweathermap.org",
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_address": "a_test_account_you_control@gmail.com",
    "sender_app_password": "a 16-character Gmail App Password"
  },
  "custom_commands": {
    "your trigger phrase": "what the assistant should say back"
  },
  "knowledge_base": {
    "your question": "the answer to give"
  }
}
```

**Important — use a test/dummy email account for this project.**
Gmail requires an "App Password" (not your normal password) for
programs like this to send mail — search "create Gmail app password"
for instructions. Never commit real passwords to a shared repository.

You can add as many `custom_commands` or `knowledge_base` entries as
you like — the assistant reads them fresh every time it starts.

## How to Run It

1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
2. Fill in `config.json` as described above (at minimum, add a weather
   API key if you want that feature to work).
3. Run the program:
   ```
   python voice_assistant_advanced.py
   ```
4. Try saying things like:
   - "What's the weather in Mumbai?"
   - "Remind me in 10 minutes to check the oven"
   - "Send an email to bob subject hello saying let's meet at 5"
   - "What is Python?"
   - "Tell me a joke" (a custom command)
   - "Exit"

## Privacy Consideration

This assistant sends data to a few external places — it's worth
knowing exactly what goes where:

- **Your voice audio** is sent to Google's speech recognition service
  (via the `speech_recognition` library) to be converted to text. Audio
  is not stored by this program, but it does leave your computer.
- **Weather requests** send the city name you ask about to
  OpenWeatherMap, along with your API key.
- **Emails** send the recipient address, subject, and body to your
  configured SMTP server (e.g. Gmail), along with your login
  credentials from `config.json`. Keep `config.json` private — never
  share it or upload it to a public GitHub repo, since it stores your
  email password in plain text.
- **Knowledge base and custom command answers** are entirely local —
  they never leave your computer, since they come from `config.json`.
- **Web searches** open a URL containing your search topic in your
  default browser (sent to Google, like any normal web search).

## What I Learned

- How to design a lightweight NLU layer using regular expressions to
  extract structured information from free-form sentences.
- Why intent-checking order matters when different intents can share
  overlapping words.
- How to send email programmatically with `smtplib` and `MIMEText`.
- How to schedule a delayed action with `threading.Timer` without
  blocking the rest of the program.
- How to make a program configurable through an external JSON file
  instead of hard-coding values.
- Why it's important to document what data a program sends externally,
  and to whom.
