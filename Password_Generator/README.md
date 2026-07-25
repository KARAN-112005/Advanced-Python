# Task 3 – Random Password Generator (Advanced Tier)

A desktop GUI version of the password generator, with a length slider,
character type checkboxes, a strength meter, automatic clipboard
copying, and a short session history.

## Project Files

- `password_gui_advanced.py` — run this one; it opens the window
- `password_logic.py` — the actual password generation and strength logic (no GUI code)
- `requirements.txt` — the one extra library you need to install

## Concepts Practiced

**`secrets` instead of `random`**
```python
import secrets
secrets.choice(pool)
secrets.randbelow(n)
```
Python's `random` module is predictable enough that an attacker could
potentially guess future "random" values if they know past ones — fine
for games, unsafe for passwords. `secrets` is built specifically for
security-sensitive randomness, which is why the advanced tier requires it.

**Guaranteeing character variety, not just hoping for it**
Picking every character purely at random from a combined pool could
technically produce a password with zero digits by pure chance.
`generate_password()` avoids this by first choosing one character from
*each* selected type, then filling the rest randomly, then shuffling —
so the required variety is guaranteed, not just likely.

**Fisher-Yates shuffle**
`secure_shuffle()` implements the Fisher-Yates algorithm by hand (swap
each position with a random earlier-or-equal position, working
backwards) using `secrets.randbelow()` instead of `random.shuffle()`,
to keep the whole generation process cryptographically secure end to end.

**Raising and catching custom validation errors**
`generate_password()` raises a `ValueError` with a clear message if no
character types are selected, or if the length is too short to fit one
of each selected type. The GUI catches this with `try`/`except` and
shows a `messagebox` instead of crashing.

**tkinter `Scale` (slider) and `Spinbox` kept in sync**
Both widgets are bound to the same `tk.IntVar`, so dragging the slider
updates the spinbox number and vice versa — they're just two different
ways of viewing and editing the same underlying variable.

**`BooleanVar` for checkboxes**
Each `ttk.Checkbutton` is linked to a `tk.BooleanVar`, so
`self.use_upper.get()` returns `True`/`False` directly reflecting
whether the box is checked — no manual event handling needed.

**Clipboard access with `pyperclip`**
`pyperclip.copy(password)` puts the generated password directly on the
system clipboard, so you can paste it immediately elsewhere without
manually selecting and copying the text.

**Session-only history (a plain Python list, not a file)**
```python
self.history.insert(0, password)
self.history = self.history[:HISTORY_LIMIT]
```
The last 5 passwords are kept in memory in a list, with the newest
first. Deliberately, this is **never written to disk** — closing the
app clears it completely, which is safer for something as sensitive as
a password history.

## How to Run It

1. Install the one extra library:
   ```
   pip install -r requirements.txt
   ```
   > On Linux, `pyperclip` also needs a clipboard tool installed
   > separately, e.g. `sudo apt install xclip`. On Windows and macOS it
   > works out of the box.
2. Run the program:
   ```
   python password_gui_advanced.py
   ```
3. Adjust the length slider/spinbox and tick the character types you want.
4. Click **Generate Password** — the password appears, gets copied to
   your clipboard automatically, and shows a Weak/Medium/Strong rating.
5. Generate a few more to see the history list fill up (max 5, newest first).

## What I Learned

- Why `secrets` is the correct choice over `random` for anything
  security-related, and how to use `secrets.choice()` and
  `secrets.randbelow()`.
- How to guarantee variety in generated output instead of relying on
  probability, using a "pick one of each, then fill, then shuffle" pattern.
- How to implement the Fisher-Yates shuffle algorithm manually.
- How to sync two different tkinter widgets (a slider and a spinbox)
  to the same underlying variable.
- How to copy text to the system clipboard from Python with `pyperclip`.
- Why sensitive session data (like a password history) should sometimes
  deliberately be kept in memory only, and never written to disk.
