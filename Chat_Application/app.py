"""
app.py - Chat Application (Advanced Tier) - Flask + Flask-SocketIO
-----------------------------------------------------------------------
A web-based, real-time, multi-room chat app with login, message
history, and emoji shortcodes.

Run this file, then open http://127.0.0.1:5000 in a browser. Open it
in a second browser tab (or incognito window) logged in as a different
user to chat between the two.

See README.md for a full explanation of how data is stored, and an
important note about the lack of encryption.
"""

import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, join_room, emit

import db
from emoji_map import render_emojis

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("CHAT_APP_SECRET_KEY", "dev-secret-change-me")
socketio = SocketIO(app)

db.init_db()


def current_user():
    return session.get("username")


# ---------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are both required.")
            return redirect(url_for("register"))

        try:
            db.create_user(username, password)
        except ValueError as e:
            flash(str(e))
            return redirect(url_for("register"))

        session["username"] = username
        return redirect(url_for("rooms"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if db.verify_user(username, password):
            session["username"] = username
            return redirect(url_for("rooms"))

        flash("Incorrect username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def rooms():
    if not current_user():
        return redirect(url_for("login"))

    if request.method == "POST":
        room_name = request.form.get("room_name", "").strip()
        if room_name:
            db.get_or_create_room(room_name, current_user())
            return redirect(url_for("chat_room", room_name=room_name))

    return render_template("rooms.html", rooms=db.get_all_rooms(), username=current_user())


@app.route("/chat/<room_name>")
def chat_room(room_name):
    if not current_user():
        return redirect(url_for("login"))

    db.get_or_create_room(room_name, current_user())
    history = db.get_recent_messages(room_name, limit=50)
    return render_template(
        "chat.html", room_name=room_name, username=current_user(), history=history
    )


# ---------------------------------------------------------------
# Socket.IO real-time events
# ---------------------------------------------------------------

@socketio.on("join")
def on_join(data):
    room_name = data["room"]
    username = data["username"]
    join_room(room_name)
    emit("system_message", {"text": f"{username} joined the room."}, to=room_name)


@socketio.on("send_message")
def on_send_message(data):
    room_name = data["room"]
    username = data["username"]
    content = render_emojis(data["message"])

    sent_at = db.save_message(room_name, username, content)

    emit("new_message", {
        "username": username,
        "message": content,
        "sent_at": sent_at,
    }, to=room_name)


if __name__ == "__main__":
    socketio.run(app, debug=True)
