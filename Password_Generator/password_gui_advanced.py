"""
password_gui_advanced.py - Random Password Generator (Advanced Tier) - GUI
-----------------------------------------------------------------------------
A tkinter desktop app with sliders/spinboxes for length, checkboxes for
character types, a strength meter, one-click clipboard copy, and a
session-only history of the last 5 generated passwords.

Run this file directly to open the window.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyperclip

from password_logic import generate_password, password_strength

STRENGTH_COLORS = {
    "Weak": "#ef4444",    # red
    "Medium": "#f59e0b",  # amber
    "Strong": "#22c55e",  # green
}

HISTORY_LIMIT = 5


class PasswordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator - Advanced")
        self.geometry("460x520")
        self.resizable(False, False)

        # Session-only history - lives in memory, never written to disk,
        # so past passwords disappear once the app is closed.
        self.history = []

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        self.length_var = tk.IntVar(value=12)

        self._build_widgets()

    def _build_widgets(self):
        ttk.Label(self, text="Password Generator", font=("Segoe UI", 16, "bold")).pack(pady=(15, 10))

        # --- Length control: slider + spinbox kept in sync ---
        length_frame = ttk.Frame(self)
        length_frame.pack(pady=5)
        ttk.Label(length_frame, text="Length:").grid(row=0, column=0, padx=5)
        ttk.Scale(
            length_frame, from_=8, to=64, orient="horizontal",
            variable=self.length_var, length=220,
            command=lambda v: self.length_var.set(round(float(v))),
        ).grid(row=0, column=1, padx=5)
        ttk.Spinbox(
            length_frame, from_=8, to=64, width=5, textvariable=self.length_var
        ).grid(row=0, column=2, padx=5)

        # --- Character type checkboxes ---
        types_frame = ttk.LabelFrame(self, text="Character types")
        types_frame.pack(pady=10, padx=20, fill="x")
        ttk.Checkbutton(types_frame, text="Uppercase (A-Z)", variable=self.use_upper).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(types_frame, text="Lowercase (a-z)", variable=self.use_lower).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(types_frame, text="Numbers (0-9)", variable=self.use_digits).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(types_frame, text="Symbols (!@#$...)", variable=self.use_symbols).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(
            types_frame, text="Exclude ambiguous characters (0, O, 1, l, I)",
            variable=self.exclude_ambiguous
        ).pack(anchor="w", padx=10, pady=2)

        ttk.Button(self, text="Generate Password", command=self.on_generate).pack(pady=12)

        # --- Result + strength ---
        self.result_var = tk.StringVar(value="")
        result_entry = ttk.Entry(self, textvariable=self.result_var, font=("Consolas", 13), justify="center", state="readonly")
        result_entry.pack(pady=5, padx=20, fill="x")

        self.strength_label = tk.Label(self, text="", font=("Segoe UI", 11, "bold"))
        self.strength_label.pack(pady=5)

        self.copy_status = ttk.Label(self, text="", foreground="#666666")
        self.copy_status.pack()

        # --- History ---
        ttk.Label(self, text="History (this session only, last 5):").pack(pady=(15, 2))
        self.history_listbox = tk.Listbox(self, height=5, font=("Consolas", 10))
        self.history_listbox.pack(padx=20, fill="x")

    def on_generate(self):
        length = self.length_var.get()

        try:
            password = generate_password(
                length,
                self.use_upper.get(),
                self.use_lower.get(),
                self.use_digits.get(),
                self.use_symbols.get(),
                self.exclude_ambiguous.get(),
            )
        except ValueError as e:
            messagebox.showwarning("Can't generate password", str(e))
            return

        self.result_var.set(password)

        num_types = sum([
            self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get(),
        ])
        strength = password_strength(length, num_types)
        self.strength_label.config(text=f"Strength: {strength}", fg=STRENGTH_COLORS[strength])

        # Copy to clipboard automatically
        try:
            pyperclip.copy(password)
            self.copy_status.config(text="Copied to clipboard!")
        except pyperclip.PyperclipException:
            self.copy_status.config(text="Couldn't access the clipboard on this system.")

        # Update session history (keep only the most recent 5)
        self.history.insert(0, password)
        self.history = self.history[:HISTORY_LIMIT]
        self.history_listbox.delete(0, tk.END)
        for pw in self.history:
            self.history_listbox.insert(tk.END, pw)


if __name__ == "__main__":
    app = PasswordApp()
    app.mainloop()
