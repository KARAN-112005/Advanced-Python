# Task 2 – BMI Calculator (Advanced Tier)

A desktop GUI version of the BMI calculator. Enter a name, weight, and
height, hit Calculate, and get a colour-coded result. Every calculation
is saved per user, and you can view a graph of how someone's BMI has
changed over time.

## Project Files

- `bmi_gui_advanced.py` — run this one; it opens the window
- `bmi_logic.py` — the BMI math and category logic (no GUI code)
- `db.py` — all the SQLite database code (saving/reading records)
- `requirements.txt` — the one extra library you need to install

## Concepts Practiced

**Separating logic, data, and interface into different files**
Instead of one giant file, this project splits into three responsibilities:
`bmi_logic.py` (pure math), `db.py` (storage), and `bmi_gui_advanced.py`
(what you see and click). Each file can be understood, tested, and
reused on its own — this pattern is called "separation of concerns."

**Building a window with `tkinter`**
`tkinter` is Python's built-in GUI toolkit. A window is a class that
inherits from `tk.Tk`, and widgets (labels, entry boxes, buttons) are
created and placed inside it with `.pack()` or `.grid()`.
```python
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator - Advanced")
```

**`ttk` themed widgets vs plain `tk` widgets**
`ttk.Entry`, `ttk.Button`, and `ttk.Label` look more like native OS
controls than the plain `tk` versions. The result label uses plain
`tk.Label` instead, specifically because it needs its text *color* to
change dynamically (`foreground=color`), which is simpler with `tk`.

**Connecting buttons to functions with `command=`**
```python
ttk.Button(self, text="Calculate", command=self.on_calculate)
```
`command=self.on_calculate` tells tkinter to call that method every
time the button is clicked — this is how user actions trigger code.

**Color-coded feedback**
`category_color()` maps each BMI category to a hex color (green for
Normal, red for Obese, etc.), and the result label's `foreground` is
set to that color — giving instant visual feedback beyond just text.

**SQLite for persistent storage (`sqlite3` module, built into Python)**
Every BMI calculation gets saved as a row in a local `bmi_records.db`
file, tagged with the user's name and a timestamp. This means the data
survives after you close the program — unlike variables in memory,
which disappear when the program ends.

**Multi-user support via a `user_name` column**
Records aren't just dumped in one big list — each row is tagged with
`user_name`, so `get_records("Karan")` only returns Karan's history,
letting multiple people share the same database file.

**A custom exception for error handling (`DatabaseError`)**
```python
class DatabaseError(Exception):
    pass
```
Every database function catches `sqlite3.Error` internally and
re-raises it as a friendlier `DatabaseError`. The GUI only has to catch
one exception type and show a message box — it doesn't need to know
the details of how SQLite fails.

**Embedding a matplotlib chart inside a tkinter window**
```python
canvas = FigureCanvasTkAgg(figure, master=window)
canvas.get_tk_widget().pack(fill="both", expand=True)
```
`FigureCanvasTkAgg` is a bridge that lets a matplotlib chart be drawn
directly inside a tkinter widget, instead of opening in a separate
pop-up plot window.

**A secondary window with `tk.Toplevel`**
The trend graph opens in its own window (`tk.Toplevel`) rather than
replacing the main window, so you can compare it side-by-side or close
it independently.

## How to Run It

1. Install the one extra library needed (tkinter and sqlite3 both come
   built into Python already):
   ```
   pip install -r requirements.txt
   ```
2. Run the program:
   ```
   python bmi_gui_advanced.py
   ```
3. Enter a user name, weight (kg), and height (m), then click
   **Calculate**. The result appears color-coded, and is saved
   automatically.
4. Calculate a few more times (same name, different weight) to build
   up some history.
5. Enter that same name under "View trend for user" and click
   **View Trend Graph** to see a line chart of their BMI over time.

The database file `bmi_records.db` is created automatically in this
folder the first time you run the program — delete it any time to
start fresh.

## What I Learned

- How to structure a project by splitting math, storage, and interface
  into separate, independently testable files.
- How to build a working desktop GUI with `tkinter`, including entry
  fields, buttons, and dynamic label styling.
- How to persist data across program runs using SQLite, and how to
  filter records per user.
- How to wrap low-level errors (like `sqlite3.Error`) in a custom
  exception so the rest of the program only has to handle one type of
  failure.
- How to embed a matplotlib chart inside a tkinter window instead of
  opening it separately.
