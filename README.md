# 🧪 Scientific Calculator – Modern GUI with Advanced Features

A fully featured scientific calculator built with Python and `tkinter`.  
It offers a clean, responsive interface with **rounded corners**, **light/dark/blue themes**, **complex number support**, **angle unit selection**, **calculation history**, and **bilingual interface** (German/English).  
The evaluation engine uses Python’s `ast` module for safe expression parsing – no risky `eval()` calls.

---

## ✨ Features

- **Safe evaluation** – uses Python’s `ast` to parse and evaluate mathematical expressions.
- **Trigonometric functions** – `sin`, `cos`, `tan`, `asin`, `acos`, `atan` with **Deg / Rad / Grad** mode.
- **Hyperbolic functions** – `sinh`, `cosh`, `tanh`.
- **Logarithms & powers** – `log`, `log10`, `exp`, `sqrt`, `^` (power).
- **Complex numbers** – toggle with the **Complex** button; functions from `cmath` are used.
- **Constants** – `π` (pi), `e`, and `Ans` (last result).
- **History** – view your last 20 calculations in a separate window.
- **Keyboard support** – type numbers and operators directly, use **Enter** to calculate, **Escape** to clear, **Backspace** to delete last character.
- **Themes** – switch between **Light**, **Dark**, and **Blue** themes on the fly.
- **Language toggle** – switch between **German** and **English** instantly.
- **Modern window** – rounded corners, custom title bar, draggable.
- **No console window** – the terminal is hidden automatically (even without `.pyw`).

---

## 📦 Requirements

- **Python 3.6 or higher** (tested with 3.10–3.13).  
- **tkinter** – included with Python on all major platforms.  
- No additional libraries needed.

---

## 🚀 How to Run

1. **Save the script** as `calculator.py` (or any name you like).  
2. **Double‑click** the file – the calculator window opens immediately.  
3. Start typing or click the buttons.  
4. Use the **Mode** button to change angle units, **Complex** to enable/disable complex arithmetic, **Theme** to change colors, and **Sprache / Language** to switch between German and English.

> 💡 The console window is hidden automatically, so the calculator runs quietly in the background.

---

## 🎮 Usage

### Main Display
- Shows your current expression and result.  
- You can type directly into the entry field (keyboard support).

### Buttons
- **C** – clear everything.  
- **←** – delete last character.  
- **=** – calculate the expression.  
- **sin, cos, tan, asin, acos, atan** – trigonometric functions (angle unit depends on current mode).  
- **sinh, cosh, tanh** – hyperbolic functions.  
- **log** – natural logarithm (base e).  
- **√** – square root.  
- **^** – power (e.g. `2^3` = 8).  
- **π** – inserts pi (3.14159…).  
- **e** – inserts Euler’s number.  
- **Ans** – inserts the last calculated result.  
- **j** – imaginary unit (for complex numbers).  
- **( )** – parentheses.  
- **0–9, ., +, -, *, /** – basic arithmetic.

### Mode Buttons (bottom row)
- **Modus / Mode** – cycles through **Deg** (degrees), **Rad** (radians), **Grad** (gons).  
- **Komplex / Complex** – toggles complex‑number mode (uses `cmath`).  
- **Theme / Design** – cycles through Light, Dark, and Blue themes.  
- **Sprache / Language** – switches between German and English.

### Keyboard Shortcuts
- **Numbers and operators** – type directly.  
- **Enter** – calculate (same as `=`).  
- **Escape** – clear all (same as `C`).  
- **Backspace** – delete last character (same as `←`).

### History
Click the **History** button (top‑right corner). A new window shows the last 20 calculations. You can scroll through them, but entries are read‑only.

---

## ⚙️ Configuration

All settings are accessible through the GUI buttons; no configuration file is required.  
The theme, language, angle mode, and complex mode are applied immediately and persist only for the current session.

---

## 🐛 Troubleshooting

| Problem | Solution |
|--------|----------|
| **Nothing happens when I double‑click** | Make sure Python is installed. Open a terminal and run `python --version`. If that works, run the script from the terminal with `python calculator.py` to see error messages. |
| **The window appears but has no title bar** | The custom title bar is part of the design – you can still drag the window by clicking the title text or the bar itself. |
| **Complex numbers give strange results** | In complex mode, functions like `sqrt(-1)` return `1j`. If you don’t need complex numbers, keep the **Complex** button off. |
| **History window is empty** | You haven’t performed any calculations yet – history is stored only after pressing `=`. |
| **I want more functions** | The `SafeEvaluator` can be extended easily. Add new functions to the `funcs` dictionary in the `__init__` method. |

---

## 📄 License

This project is open‑source and free to use. No warranty.

---

Enjoy calculating! 🎉
