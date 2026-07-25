"""
emoji_map.py - Converts emoji shortcodes like :smile: into real emoji
characters like 😄, for messages typed in the chat app.
"""

import re

SHORTCODES = {
    ":smile:": "😄",
    ":laughing:": "😆",
    ":heart:": "❤️",
    ":thumbsup:": "👍",
    ":thumbsdown:": "👎",
    ":fire:": "🔥",
    ":cry:": "😢",
    ":wink:": "😉",
    ":100:": "💯",
    ":tada:": "🎉",
    ":wave:": "👋",
    ":eyes:": "👀",
    ":thinking:": "🤔",
    ":rocket:": "🚀",
}

# Matches any :word: pattern so we only need one regex substitution pass
_SHORTCODE_PATTERN = re.compile(r":[a-zA-Z0-9_+\-]+:")


def render_emojis(text):
    """Replace every recognized :shortcode: in the text with its emoji."""
    def replace(match):
        code = match.group(0)
        return SHORTCODES.get(code, code)  # leave unknown shortcodes untouched

    return _SHORTCODE_PATTERN.sub(replace, text)
