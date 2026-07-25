# Task 5 – Chat Application (Advanced Tier)

A full web-based chat app built with Flask and Flask-SocketIO: user
accounts, multiple named rooms, real-time messaging, message history,
emoji shortcodes, and desktop notifications for messages that arrive
while you're looking at another tab.

## Project Files

- `app.py` — the Flask + Socket.IO server (routes and real-time events)
- `db.py` — all the SQLite database code (users, rooms, messages)
- `emoji_map.py` — converts `:smile:`-style shortcodes into real emoji
- `templates/` — the HTML pages (`register.html`, `login.html`, `rooms.html`, `chat.html`)
- `requirements.txt` — libraries to install

## Concepts Practiced

**Flask routes and Jinja2 templates**
Each `@app.route(...)` function handles one URL. `render_template()`
fills in an HTML file from `templates/` with Python data — e.g.
`{{ username }}` in `rooms.html` gets replaced with the real logged-in
username.

**Sessions for staying logged in**
```python
session["username"] = username
```
Flask's `session` stores small pieces of data in a signed cookie in
the user's browser. Since it's signed with `SECRET_KEY`, the browser
can't tamper with it — this is how the app remembers who's logged in
between page loads without a database lookup every time.

**Password hashing with Werkzeug**
```python
generate_password_hash(password)
check_password_hash(stored_hash, password)
```
Passwords are never stored as plain text — only a one-way hash is
saved. Even if the database were leaked, the original passwords
couldn't be recovered from it directly.

**Real-time communication with Flask-SocketIO**
Regular HTTP requests are "ask once, get one answer" — not great for a
live chat. Socket.IO keeps a persistent connection open between
browser and server, so the server can `emit()` a new message to
everyone in a room the instant it happens, with no page reload.

**Socket.IO rooms**
```python
join_room(room_name)
emit("new_message", data, to=room_name)
```
Socket.IO has its own concept of "rooms" (separate from our database
rooms table) — a way to group connected clients so a message only
broadcasts to people actually viewing that chat room, not everyone
connected to the server.

**Message history loaded on join**
When you open a room, `get_recent_messages()` pulls the last 50
messages from SQLite and the template renders them directly into the
page — so you see the conversation that already happened, not just
new messages from that point forward.

**Emoji shortcode substitution with regex**
```python
_SHORTCODE_PATTERN = re.compile(r":[a-zA-Z0-9_+\-]+:")
_SHORTCODE_PATTERN.sub(replace, text)
```
One regex finds anything shaped like `:word:` in a message, and a
lookup dictionary swaps recognized codes for the matching emoji —
unrecognized codes like `:notarealthing:` are left as-is.

**Browser desktop notifications**
```javascript
new Notification(`${data.username} in #${roomName}`, { body: data.message });
```
The chat page asks for notification permission on load, and shows a
native OS notification when a new message arrives while
`document.hidden` is true (i.e. you've switched to another tab).

**Escaping user input in the browser**
`escapeHtml()` runs incoming messages through the browser's own text
escaping before inserting them into the page, to prevent a message
containing HTML/script tags from being executed as code.

## How to Run It

1. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
2. Run the server:
   ```
   python app.py
   ```
3. Open **http://127.0.0.1:5000** in your browser and register an account.
4. Open a **second browser window** (or an incognito/private window) and
   register a second, different account.
5. In both windows, create or join the same room name (e.g. `general`).
6. Type messages in either window — they should appear in both
   instantly. Try `:smile:`, `:fire:`, or `:heart:` to see emoji rendering.
7. Switch to a different tab/app while the other user sends a message —
   you should get a desktop notification (allow notifications when
   your browser asks).

A `chat_app.db` SQLite file is created automatically the first time you
run the app — delete it to start completely fresh (this removes all
accounts, rooms, and message history).

## Security & Privacy — Please Read

**Passwords** are hashed (not stored as plain text) using Werkzeug's
`generate_password_hash`, which uses a strong, salted hashing algorithm.

**Messages are NOT encrypted.** This is important to understand:

- Messages are sent over a plain (unencrypted) local connection in
  this development setup — running this over the public internet
  without adding HTTPS would let anyone on the network read the
  traffic.
- Messages are stored in the `chat_app.db` SQLite file as **plain,
  readable text** — anyone with access to that file (or to the server
  it's running on) can read every message ever sent, in any room.
- There is no end-to-end encryption. The server itself can read every
  message, since it's the one saving and forwarding them.

This project is meant for learning real-time app development, not for
sending anything genuinely private. A production chat app would need
HTTPS (and WSS for the socket connection) at minimum, and true
end-to-end encryption if message privacy from the server itself
matters.

## What I Learned

- How to build a multi-page web app with Flask routes, sessions, and
  Jinja2 templates.
- How to hash and verify passwords safely instead of storing them as
  plain text.
- How Socket.IO enables real-time, two-way communication that plain
  HTTP requests can't do on their own.
- How Socket.IO "rooms" let you broadcast messages to a specific group
  of connected users instead of everyone.
- How to load and display historical data (past messages) alongside
  live incoming data in the same view.
- How to use regex-based find-and-replace for a simple text
  transformation like emoji shortcodes.
- How to trigger browser desktop notifications from JavaScript.
- Why it's important to be upfront about what a system does and
  doesn't protect — especially that "chat app" doesn't automatically
  mean "encrypted" or "private."
