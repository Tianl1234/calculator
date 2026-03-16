#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===== Wissenschaftlicher Taschenrechner mit übersichtlichem Layout =====
# Features: Verlauf, Tastatur, Winkelmodus, komplexe Zahlen, Themes,
#           Deutsch/Englisch Umschaltung, abgerundete Ecken, klares Raster.

import sys
import ctypes
import ast
import operator
import math
import cmath
import tkinter as tk
from tkinter import messagebox, ttk

# ------------------------------------------------------------
# Konsole sofort verstecken (für .pyw)
# ------------------------------------------------------------
if sys.platform == "win32":
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.FreeConsole()

# ------------------------------------------------------------
# Hilfsfunktion für abgerundete Rechtecke (Canvas)
# ------------------------------------------------------------
def _create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
    points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
              x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
              x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
              x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_round_rect = _create_round_rect

# ------------------------------------------------------------
# Custom Fensterklasse mit abgerundeten Ecken und Titelleiste
# ------------------------------------------------------------
class RoundWindow:
    def __init__(self, width, height, title, bg_color="#ffffff", title_color="#000000"):
        self.root = tk.Toplevel() if tk._default_root else tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(f"{width}x{height}+300+200")
        self.root.configure(bg=bg_color)
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_round_rect(5, 5, width-5, height-5, r=20, fill=bg_color, outline="#cccccc", width=2)
        
        # Titelleiste
        title_bar = tk.Frame(self.root, bg=bg_color, height=30)
        title_bar.place(x=10, y=10, width=width-20)
        
        title_label = tk.Label(title_bar, text=title, font=("Segoe UI", 10, "bold"),
                               fg=title_color, bg=bg_color)
        title_label.pack(side="left", padx=10)
        
        close_btn = tk.Button(title_bar, text="✕", font=("Segoe UI", 10, "bold"),
                              fg=title_color, bg=bg_color, bd=0, activebackground="#ffcccc",
                              activeforeground="black", cursor="hand2",
                              command=self.root.destroy)
        close_btn.pack(side="right", padx=10)
        
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)
        
        self.inner_frame = tk.Frame(self.root, bg=bg_color)
        self.inner_frame.place(x=15, y=50, width=width-30, height=height-70)
        
    def start_move(self, event):
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()
    
    def do_move(self, event):
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")

# ============================================================
# I. SICHERER EVALUATOR (mit komplexen Zahlen und Winkelmodus)
# ============================================================
class SafeEvaluator:
    def __init__(self, last_result=None, angle_mode='deg', use_complex=False):
        self.ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.USub: operator.neg
        }
        self.angle_mode = angle_mode
        self.use_complex = use_complex
        self.vars = {"pi": math.pi, "e": math.e, "ans": last_result if last_result else 0}
        self.update_functions()
        
    def update_functions(self):
        lib = cmath if self.use_complex else math
        self.funcs = {
            "sin": self._sin_wrapper,
            "cos": self._cos_wrapper,
            "tan": self._tan_wrapper,
            "sqrt": lib.sqrt,
            "log": lib.log,
            "log10": lib.log10,
            "exp": lib.exp,
            "asin": self._asin_wrapper,
            "acos": self._acos_wrapper,
            "atan": self._atan_wrapper,
            "sinh": lib.sinh,
            "cosh": lib.cosh,
            "tanh": lib.tanh,
        }
    
    def _to_radians(self, x):
        if self.angle_mode == 'deg':
            return math.radians(x)
        elif self.angle_mode == 'grad':
            return x * math.pi / 200
        else:
            return x
    
    def _from_radians(self, x):
        if self.angle_mode == 'deg':
            return math.degrees(x)
        elif self.angle_mode == 'grad':
            return x * 200 / math.pi
        else:
            return x
    
    def _sin_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return lib.sin(self._to_radians(x))
    
    def _cos_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return lib.cos(self._to_radians(x))
    
    def _tan_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return lib.tan(self._to_radians(x))
    
    def _asin_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return self._from_radians(lib.asin(x))
    
    def _acos_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return self._from_radians(lib.acos(x))
    
    def _atan_wrapper(self, x):
        lib = cmath if self.use_complex else math
        return self._from_radians(lib.atan(x))
    
    def evaluate(self, expr):
        try:
            expr = expr.replace("^", "**")
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except Exception as e:
            return f"Fehler: {e}"
    
    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.vars:
                return self.vars[node.id]
            if node.id == 'j':
                return 1j
            return 0
        if isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            return self.ops[type(node.op)](self._eval_node(node.operand))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.funcs:
                args = [self._eval_node(arg) for arg in node.args]
                return self.funcs[node.func.id](*args)
        raise ValueError("Operation nicht erlaubt")

# ============================================================
# II. GUI mit übersichtlichem Layout
# ============================================================
class UltimateCalculatorGUI:
    def __init__(self):
        self.history = []
        self.angle_mode = 'deg'
        self.use_complex = False
        self.theme = 'light'
        self.lang = 'de'
        
        self.evaluator = SafeEvaluator(angle_mode=self.angle_mode, use_complex=self.use_complex)
        
        # Sprachdaten
        self.lang_data = {
            'de': {
                'window_title': 'Wissenschaftlicher Taschenrechner',
                'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'asin': 'asin', 'acos': 'acos', 'atan': 'atan',
                'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh', 'log': 'log', 'sqrt': '√', '^': '^',
                'C': 'C', '←': '←', '(': '(', ')': ')', 'ans': 'Ans', 'j': 'j',
                '7': '7', '8': '8', '9': '9', '/': '/', '4': '4', '5': '5', '6': '6',
                '*': '*', '1': '1', '2': '2', '3': '3', '-': '-', '0': '0', '.': '.',
                'pi': 'π', 'e': 'e', '+': '+', '=': '=',
                'Modus': 'Modus', 'Komplex': 'Komplex', 'Theme': 'Design', 'Sprache': 'Sprache',
                'History': 'Verlauf', 'Deg': 'Grad', 'Rad': 'Rad', 'Grad': 'Gon',
                'header': '🧪 WISSENSCHAFTLICHER TASCHENRECHNER'
            },
            'en': {
                'window_title': 'Scientific Calculator',
                'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'asin': 'asin', 'acos': 'acos', 'atan': 'atan',
                'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh', 'log': 'log', 'sqrt': '√', '^': '^',
                'C': 'C', '←': '←', '(': '(', ')': ')', 'ans': 'Ans', 'j': 'j',
                '7': '7', '8': '8', '9': '9', '/': '/', '4': '4', '5': '5', '6': '6',
                '*': '*', '1': '1', '2': '2', '3': '3', '-': '-', '0': '0', '.': '.',
                'pi': 'π', 'e': 'e', '+': '+', '=': '=',
                'Modus': 'Mode', 'Komplex': 'Complex', 'Theme': 'Theme', 'Sprache': 'Language',
                'History': 'History', 'Deg': 'Deg', 'Rad': 'Rad', 'Grad': 'Grad',
                'header': '🧪 SCIENTIFIC CALCULATOR'
            }
        }
        
        # Fenstergröße: 580x720 für 6 Spalten und 7 Zeilen + Kopf
        self.win = RoundWindow(580, 720, self.lang_data[self.lang]['window_title'],
                               bg_color="#ffffff", title_color="#000000")
        self.root = self.win.root
        self.inner = self.win.inner_frame
        
        # Tastatur-Shortcuts
        self.root.bind("<Key>", self._key_press)
        self.root.bind("<Return>", lambda e: self._on_btn('='))
        self.root.bind("<Escape>", lambda e: self._on_btn('C'))
        self.root.bind("<BackSpace>", lambda e: self._on_btn('←'))
        
        self._build_ui()
        self._apply_theme()
    
    def _build_ui(self):
        # Header mit Statusleiste
        self.header_frame = tk.Frame(self.inner, bg=self.inner.cget('bg'))
        self.header_frame.pack(fill="x", pady=(5,0))
        
        self.mode_label = tk.Label(self.header_frame, text=self.lang_data[self.lang]['Deg'],
                                    font=("Segoe UI", 9), bg=self.inner.cget('bg'), fg="black")
        self.mode_label.pack(side="left", padx=5)
        
        self.header_label = tk.Label(self.header_frame, text=self.lang_data[self.lang]['header'],
                                      font=("Segoe UI", 9, "bold"), bg=self.inner.cget('bg'), fg="#2196F3")
        self.header_label.pack(side="right", padx=5)
        
        # Display
        self.display = tk.Entry(self.inner, font=("Helvetica", 32),
                                bg="#f0f0f0", fg="black", bd=1, relief="solid", justify="right")
        self.display.pack(fill="x", padx=20, pady=10)
        
        # History-Button
        self.history_btn = tk.Button(self.inner, text=self.lang_data[self.lang]['History'],
                                      font=("Segoe UI", 9), command=self.show_history,
                                      bg="#e0e0e0", fg="black", bd=0, padx=5, pady=2)
        self.history_btn.pack(anchor="ne", padx=20, pady=2)
        
        # Frame für Buttons (6 Spalten x 7 Zeilen)
        self.btn_frame = tk.Frame(self.inner, bg=self.inner.cget('bg'))
        self.btn_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        # Button-Definitionen: (Schlüssel, row, col)
        # Ordnung: Wissenschaftliche Funktionen, Steuerung, Zahlen, Operatoren, Modi
        btn_keys = [
            # Zeile 0: trigonometrische Grundfunktionen
            ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('asin', 0, 3), ('acos', 0, 4), ('atan', 0, 5),
            # Zeile 1: weitere Funktionen
            ('sinh', 1, 0), ('cosh', 1, 1), ('tanh', 1, 2), ('log', 1, 3), ('sqrt', 1, 4), ('^', 1, 5),
            # Zeile 2: Steuerung und Sonderzeichen
            ('C', 2, 0), ('←', 2, 1), ('(', 2, 2), (')', 2, 3), ('ans', 2, 4), ('j', 2, 5),
            # Zeile 3: Zahlen 7-9 und Operatoren
            ('7', 3, 0), ('8', 3, 1), ('9', 3, 2), ('/', 3, 3), ('4', 3, 4), ('5', 3, 5),
            # Zeile 4: Zahlen 6,*,1,2,3,-
            ('6', 4, 0), ('*', 4, 1), ('1', 4, 2), ('2', 4, 3), ('3', 4, 4), ('-', 4, 5),
            # Zeile 5: 0,.,π,e,+,=
            ('0', 5, 0), ('.', 5, 1), ('pi', 5, 2), ('e', 5, 3), ('+', 5, 4), ('=', 5, 5),
            # Zeile 6: Modus-Umschalter (leere Felder am Ende)
            ('Modus', 6, 0), ('Komplex', 6, 1), ('Theme', 6, 2), ('Sprache', 6, 3), ('', 6, 4), ('', 6, 5)
        ]
        
        # Farbzuordnung
        def get_bg(key):
            if key == 'C':
                return "#FFCDD2"
            elif key in ['/', '*', '-', '+']:
                return "#FFB74D"
            elif key == '=':
                return "#4CAF50"
            elif key in ['sin','cos','tan','asin','acos','atan','sinh','cosh','tanh','log','sqrt','^']:
                return "#e0e0e0"
            elif key in ['(',')','←','ans','j','Modus','Komplex','Theme','Sprache','pi','e']:
                return "#d9d9d9"
            else:
                return "#ffffff"
        
        self.buttons = {}
        for (key, r, c) in btn_keys:
            if not key:
                continue  # leeres Feld überspringen
            bg = get_bg(key)
            text = self.lang_data[self.lang].get(key, key)
            btn = tk.Button(self.btn_frame, text=text, font=("Helvetica", 11, "bold"),
                            bg=bg, fg="black", bd=0, relief="flat",
                            activebackground="#c0c0c0", activeforeground="black",
                            command=lambda k=key: self._on_btn(k))
            btn.key = key
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            self.buttons[key] = btn
        
        # Spalten konfigurieren (6 Spalten)
        for i in range(6):
            self.btn_frame.columnconfigure(i, weight=1)
        for i in range(7):
            self.btn_frame.rowconfigure(i, weight=1)
    
    def _on_btn(self, key):
        if key == 'C':
            self.display.delete(0, tk.END)
        elif key == '←':
            self.display.delete(len(self.display.get())-1, tk.END)
        elif key == '=':
            self._calc()
        elif key == 'Modus':
            self._cycle_angle_mode()
        elif key == 'Komplex':
            self._toggle_complex()
        elif key == 'Theme':
            self._cycle_theme()
        elif key == 'Sprache':
            self._toggle_language()
        else:
            self.display.insert(tk.END, key)
    
    def _key_press(self, event):
        if event.keysym in ('Return', 'Escape', 'BackSpace'):
            return
        char = event.char
        if char and char.isprintable():
            self.display.insert(tk.END, char)
    
    def _calc(self):
        expr = self.display.get()
        res = self.evaluator.evaluate(expr)
        
        if isinstance(res, float):
            if abs(res) < 1e-10:
                res = 0.0
            res_str = f"{res:.10f}".rstrip('0').rstrip('.') if '.' in f"{res:.10f}" else str(res)
        elif isinstance(res, complex):
            res_str = f"{res.real:.10f}".rstrip('0').rstrip('.') if abs(res.imag) < 1e-10 else str(res)
        else:
            res_str = str(res)
        
        self.display.delete(0, tk.END)
        self.display.insert(0, res_str)
        self.history.append((expr, res_str))
        
        try:
            self.evaluator.vars["ans"] = float(res) if not isinstance(res, complex) else complex(res)
        except:
            pass
    
    def show_history(self):
        if not self.history:
            messagebox.showinfo(self.lang_data[self.lang]['History'],
                                "Keine Einträge vorhanden." if self.lang=='de' else "No entries.")
            return
        
        hist_win = RoundWindow(400, 300, self.lang_data[self.lang]['History'],
                               bg_color="#ffffff", title_color="#000000")
        hist_root = hist_win.root
        hist_inner = hist_win.inner_frame
        
        listbox = tk.Listbox(hist_inner, font=("Courier", 10), bg="#f0f0f0", fg="black")
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for expr, res in self.history[-20:]:
            listbox.insert(tk.END, f"{expr} = {res}")
        
        scrollbar = tk.Scrollbar(listbox, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        close_text = "Schließen" if self.lang=='de' else "Close"
        tk.Button(hist_inner, text=close_text, command=hist_root.destroy,
                  bg="#e0e0e0", fg="black", bd=0, padx=10, pady=2).pack(pady=5)
        
        hist_root.mainloop()
    
    def _cycle_angle_mode(self):
        modes = ['deg', 'rad', 'grad']
        idx = modes.index(self.angle_mode)
        self.angle_mode = modes[(idx+1) % 3]
        self.evaluator.angle_mode = self.angle_mode
        mode_name = self.lang_data[self.lang][self.angle_mode.capitalize()]
        self.mode_label.config(text=mode_name)
    
    def _toggle_complex(self):
        self.use_complex = not self.use_complex
        self.evaluator.use_complex = self.use_complex
        self.evaluator.update_functions()
        mode_text = self.lang_data[self.lang][self.angle_mode.capitalize()]
        if self.use_complex:
            mode_text += " C" if self.lang=='en' else " K"
        self.mode_label.config(text=mode_text)
    
    def _cycle_theme(self):
        themes = ['light', 'dark', 'blue']
        idx = themes.index(self.theme)
        self.theme = themes[(idx+1) % 3]
        self._apply_theme()
    
    def _toggle_language(self):
        self.lang = 'en' if self.lang == 'de' else 'de'
        # Fenstertitel aktualisieren (Canvas-Text ändern)
        # Wir müssen den Canvas-Text ändern: Die Titelleiste ist im RoundWindow separat,
        # wir haben dort title_label. Zugriff über self.win.
        # Im RoundWindow ist title_label ein Attribut? Wir haben es nicht gespeichert.
        # Einfacher: Wir aktualisieren den Header-Label und Buttons, den Fenstertitel lassen wir.
        # Fenstertitel ist im Canvas als Text? Nein, in der Titelleiste.
        # Um es einfach zu halten, lassen wir den Fenstertitel unverändert oder setzen ihn neu.
        # Wir können den Titel im RoundWindow ändern, indem wir auf das Label zugreifen.
        # Aber das ist kompliziert. Wir ignorieren es oder setzen den Fenstertitel später neu.
        # Für dieses Beispiel lassen wir den Fenstertitel unverändert.
        
        self.header_label.config(text=self.lang_data[self.lang]['header'])
        self.history_btn.config(text=self.lang_data[self.lang]['History'])
        for key, btn in self.buttons.items():
            btn.config(text=self.lang_data[self.lang].get(key, key))
        mode_name = self.lang_data[self.lang][self.angle_mode.capitalize()]
        if self.use_complex:
            mode_name += " C" if self.lang=='en' else " K"
        self.mode_label.config(text=mode_name)
    
    def _apply_theme(self):
        if self.theme == 'light':
            bg_main = "#ffffff"
            fg_main = "#000000"
            btn_bg = "#f0f0f0"
            display_bg = "#f0f0f0"
            special_bg = "#e0e0e0"
        elif self.theme == 'dark':
            bg_main = "#2d2d2d"
            fg_main = "#ffffff"
            btn_bg = "#3c3c3c"
            display_bg = "#1e1e1e"
            special_bg = "#4a4a4a"
        else:  # blue
            bg_main = "#e3f2fd"
            fg_main = "#000000"
            btn_bg = "#bbdefb"
            display_bg = "#ffffff"
            special_bg = "#90caf9"
        
        # Hauptfenster
        self.root.configure(bg=bg_main)
        self.win.canvas.configure(bg=bg_main)
        self.win.canvas.delete("all")
        self.win.canvas.create_round_rect(5, 5, 575, 715, r=20, fill=bg_main, outline="#cccccc", width=2)
        self.inner.configure(bg=bg_main)
        
        # Header
        self.header_frame.configure(bg=bg_main)
        self.mode_label.configure(bg=bg_main, fg=fg_main)
        self.header_label.configure(bg=bg_main, fg="#2196F3")
        
        # Display
        self.display.configure(bg=display_bg, fg=fg_main)
        
        # History-Button
        self.history_btn.configure(bg=special_bg, fg=fg_main)
        
        # Buttons
        for key, btn in self.buttons.items():
            if key == 'C':
                btn.configure(bg="#FFCDD2" if self.theme=='light' else "#d32f2f", fg=fg_main)
            elif key in ['/', '*', '-', '+']:
                btn.configure(bg="#FFB74D" if self.theme=='light' else "#f57c00", fg=fg_main)
            elif key == '=':
                btn.configure(bg="#4CAF50", fg="white")
            elif key in ['sin','cos','tan','asin','acos','atan','sinh','cosh','tanh','log','sqrt','^']:
                btn.configure(bg=special_bg, fg=fg_main)
            elif key in ['(',')','←','ans','j','Modus','Komplex','Theme','Sprache','pi','e']:
                btn.configure(bg=special_bg, fg=fg_main)
            else:
                btn.configure(bg=btn_bg, fg=fg_main)

# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------
if __name__ == "__main__":
    app = UltimateCalculatorGUI()
    app.root.mainloop()
