"""
nlu.py - Natural Language Understanding for the Advanced Voice Assistant
--------------------------------------------------------------------------
This module parses a free-form spoken sentence into:
  - an "intent" (what the user wants to do)
  - a dictionary of "entities" (the useful details pulled out of the
    sentence, e.g. a city name, an email recipient, a reminder duration)

This is more than simple keyword matching: it uses regular expressions
to pull structured information out of natural sentences, so
"remind me in 10 minutes to check the oven" and "in 10 minutes remind
me to check the oven" both resolve to the same intent + entities.
"""

import re


def parse_intent(text):
    """
    Take a lowercase spoken sentence and return a tuple:
        (intent_name, entities_dict)

    Recognized intents:
      greeting, time_date, weather, send_email, set_reminder,
      web_search, question, exit, unknown
    """
    text = text.strip().lower()

    # --- exit ---
    if re.search(r"\b(exit|quit|stop|goodbye|bye)\b", text):
        return "exit", {}

    # --- email: "send an email to <name> subject <s> saying <body>" ---
    # Checked early because a subject/body can contain words like "hello"
    # or "time" that would otherwise be misread as a different intent.
    if "email" in text or "mail" in text:
        to_match = re.search(r"\bto\s+([a-zA-Z0-9._%+\-@]+)", text)
        subject_match = re.search(
            r"subject\s+(.+?)(?=\s+(?:saying|body|message)\b|$)", text
        )
        body_match = re.search(r"(?:saying|body|message)\s+(.+)$", text)

        entities = {
            "to": to_match.group(1).strip() if to_match else None,
            "subject": subject_match.group(1).strip() if subject_match else None,
            "body": body_match.group(1).strip() if body_match else None,
        }
        return "send_email", entities

    # --- reminder: "remind me in <n> <unit> to <message>" (either order) ---
    if "remind" in text:
        duration_match = re.search(
            r"in\s+(\d+)\s*(second|minute|hour)s?", text
        )
        # Grab whatever comes after "to " as the reminder message
        message_match = re.search(r"to\s+(.+)$", text)

        entities = {}
        if duration_match:
            entities["amount"] = int(duration_match.group(1))
            entities["unit"] = duration_match.group(2)
        if message_match:
            entities["message"] = message_match.group(1).strip()

        return "set_reminder", entities

    # --- weather: "weather in <city>" / "weather for <city>" / "weather" ---
    weather_match = re.search(r"weather\s*(?:in|for|at)?\s*(.*)", text)
    if weather_match is not None:
        city = weather_match.group(1).strip()
        return "weather", {"city": city if city else None}

    # --- web search: "search for <topic>" / "look up <topic>" / "google <topic>" ---
    search_match = re.search(r"(?:search for|search|look up|google)\s+(.+)$", text)
    if search_match:
        return "web_search", {"topic": search_match.group(1).strip()}

    # --- greeting ---
    if re.search(r"\b(hello|hi|hey)\b", text):
        return "greeting", {}

    # --- time / date ---
    if re.search(r"\b(time|date)\b", text):
        return "time_date", {}

    # --- general knowledge question: starts with a question word ---
    if re.match(r"^(what|who|when|where|why|how)\b", text):
        return "question", {"question": text}

    return "unknown", {}
