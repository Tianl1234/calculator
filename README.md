# 🧮 Scientific Calculator with GUI

A fully‑featured scientific calculator built with Python and `tkinter`.  
It offers a clean, modern interface with rounded corners, multiple themes, language switching, and an **unbeatable evaluation engine** based on Python’s AST – so it’s safe and fast.

---

## ✨ Features

- **Safe evaluation** – uses Python’s `ast` module; no `eval()` risks.  
- **Trigonometrical functions** (sin, cos, tan, asin, acos, atan) with **Deg / Rad / Grad** mode.  
- **Hyperbolic functions** (sinh, cosh, tanh).  
- **Logarithms** (log, log10) and **exponential** (exp).  
- **Square root** and **power** (^).  
- **Complex number support** – toggle with the “Complex” button (uses `cmath`).  
- **Constants**: π (pi), e, and Ans (last result).  
- **History** – view your last 20 calculations.  
- **Keyboard support** – type numbers and operators directly.  
- **Theme switcher** – Light, Dark, and Blue.  
- **Language** – Deutsch / English toggle.  
- **Rounded corners** and a custom title bar – you can drag the window.  
- **No console window** – the script hides it automatically (even without `.pyw`).

---

## 📦 Requirements

- **Python 3.6 or higher** (tested with 3.10–3.13).  
- **tkinter** – included with Python on all major platforms.  
- No additional libraries needed.

---

## 🚀 How to Run

1. Save the script as `calculator.py` (or any name you like).  
2. Double‑click the file – the calculator window opens immediately.  
   - If you prefer the terminal, you can run `python calculator.py` – the console window will still be hidden after a moment.

That’s it! No extra steps, no package installation.

---

## 🎮 Usage

### Main Display
- Shows your current expression and result.  
- You can type directly into it (keyboard support).  

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
Click the **“Verlauf”** (or **“History”**) button in the top‑right corner. A new window shows the last 20 calculations. Double‑clicking an entry is not supported, but you can copy the expression manually.

---

## 🛠️ Customisation

### Themes
The **Theme** button cycles through three colour schemes:
- **Light** – clean white background, grey buttons.  
- **Dark** – dark grey background, light text.  
- **Blue** – light blue background, blue accents.  

### Language
The **Sprache/Language** button toggles between German and English. All button labels, headers, and messages are translated instantly.

### Window
The window has a custom title bar. You can **drag** it by clicking and holding the title text or the bar itself. The close button (✕) ends the program.

---

## ❓ Troubleshooting

| Problem | Solution |
|--------|----------|
| **Nothing happens when I double‑click** | Make sure Python is installed correctly. Open a terminal and run `python --version`. If that works, try running the script from the terminal with `python your_script.py` to see error messages. |
| **The window appears but looks wrong** | The script was designed for a screen resolution of at least 1280×720. If parts are cut off, increase the window size by editing the `RoundWindow` dimensions in the code. |
| **Complex mode gives unexpected results** | Remember that in complex mode, functions like `sqrt(-1)` return complex numbers. The display shows them as `(0+1j)` etc. |
| **History window is blank** | You haven’t performed any calculations yet – history is stored only after pressing `=`. |
| **I want even more functions** | The `SafeEvaluator` can be extended easily. Add new functions to `self.funcs` in the `__init__` method. |

---

## 📄 License

This project is based on the AST‑evaluation idea and is provided under the **GNU General Public License (GPL)**.  
Feel free to modify and share it.

---

Enjoy calculating! 😊
