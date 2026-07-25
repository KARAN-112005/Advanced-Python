"""
bmi_gui_advanced.py - BMI Calculator (Advanced Tier) - GUI Application
---------------------------------------------------------------------------
A tkinter desktop app that calculates BMI, shows colour-coded results,
saves a history per named user in SQLite, and can plot that user's BMI
trend over time with matplotlib.

Run this file directly to open the window.
"""

import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from bmi_logic import calculate_bmi, classify_bmi, category_color
from db import init_db, save_record, get_records, get_all_users, DatabaseError


class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator - Advanced")
        self.geometry("420x420")
        self.resizable(False, False)

        # Set up the database up front; if this fails, tell the user
        # immediately instead of failing later on first save.
        try:
            init_db()
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

        self._build_widgets()

    def _build_widgets(self):
        padding = {"padx": 10, "pady": 6}

        ttk.Label(self, text="BMI Calculator", font=("Segoe UI", 16, "bold")).pack(pady=(15, 5))

        form = ttk.Frame(self)
        form.pack(**padding)

        ttk.Label(form, text="User name:").grid(row=0, column=0, sticky="w", pady=4)
        self.name_entry = ttk.Entry(form, width=22)
        self.name_entry.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=4)
        self.weight_entry = ttk.Entry(form, width=22)
        self.weight_entry.grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Height (m):").grid(row=2, column=0, sticky="w", pady=4)
        self.height_entry = ttk.Entry(form, width=22)
        self.height_entry.grid(row=2, column=1, pady=4)

        ttk.Button(self, text="Calculate", command=self.on_calculate).pack(pady=10)

        # Result area - colour-coded feedback lives here
        self.result_label = tk.Label(self, text="", font=("Segoe UI", 14, "bold"))
        self.result_label.pack(pady=5)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=10)

        ttk.Label(self, text="View trend for user:").pack()
        self.trend_user_entry = ttk.Entry(self, width=22)
        self.trend_user_entry.pack(pady=4)
        ttk.Button(self, text="View Trend Graph", command=self.on_view_trend).pack(pady=5)

        self.status_label = ttk.Label(self, text="", foreground="#666666")
        self.status_label.pack(pady=(10, 0))

    def on_calculate(self):
        name = self.name_entry.get().strip()
        weight_raw = self.weight_entry.get().strip()
        height_raw = self.height_entry.get().strip()

        if not name:
            messagebox.showwarning("Missing name", "Please enter a user name.")
            return

        try:
            weight = float(weight_raw)
            height = float(height_raw)
        except ValueError:
            messagebox.showwarning("Invalid input", "Weight and height must be numbers.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showwarning("Invalid input", "Weight and height must be positive numbers.")
            return

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = category_color(category)

        self.result_label.config(
            text=f"BMI: {round(bmi, 2)}  ({category})", foreground=color
        )

        # Save to the database, with error handling for read/write failures
        try:
            recorded_at = datetime.datetime.now().isoformat(timespec="seconds")
            save_record(name, weight, height, bmi, category, recorded_at)
            self.status_label.config(text=f"Saved record for {name}.")
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Could not save this record.\n\n{e}")

    def on_view_trend(self):
        name = self.trend_user_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Enter a user name to view their trend.")
            return

        try:
            records = get_records(name)
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Could not load records.\n\n{e}")
            return

        if not records:
            known_users = get_all_users()
            hint = f"\n\nKnown users: {', '.join(known_users)}" if known_users else ""
            messagebox.showinfo("No data", f"No records found for '{name}'.{hint}")
            return

        self._show_trend_window(name, records)

    def _show_trend_window(self, name, records):
        dates = [r[0][:16] for r in records]  # trim to "YYYY-MM-DD HH:MM"
        bmis = [r[1] for r in records]

        window = tk.Toplevel(self)
        window.title(f"BMI Trend - {name}")
        window.geometry("560x400")

        figure = Figure(figsize=(5.5, 3.8), dpi=100)
        plot = figure.add_subplot(111)
        plot.plot(range(len(bmis)), bmis, marker="o", color="#2563EB")
        plot.set_xticks(range(len(dates)))
        plot.set_xticklabels(dates, rotation=45, ha="right", fontsize=7)
        plot.set_ylabel("BMI")
        plot.set_title(f"BMI Trend for {name}")
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
