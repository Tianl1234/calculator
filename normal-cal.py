#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===== Wissenschaftlicher Taschenrechner mit erweiterten Features =====
# - Verlauf (History) anzeigen
# - Tastaturunterstützung
# - Winkelmodus (Deg/Rad/Grad)
# - Komplexe Zahlen (mit cmath)
# - Design anpassbar (Themes)
# - Abgerundete Ecken, weißer Hintergrund, kein Konsolenfenster

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
# I. SICHERER EVALUATOR mit komplexen Zahlen und Winkelmodus
# ============================================================
class SafeEvaluator:
    def __init__(self, last_result=None, angle_mode='deg', use_complex=False):
        self.ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.USub: operator.neg
        }
        self.angle_mode = angle_mode  # 'deg', 'rad', 'grad'
        self.use_complex = use_complex
        self.vars = {"pi": math.pi, "e": math.e, "ans": last_result if last_result else 0}
        self.update_functions()
        
    def update_functions(self):
        # Wähle math oder cmath je nach Modus
        lib = cmath if self.use_complex else math
        
        # Basisfunktionen
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
    
    # Wrapper für trigonometrische Funktionen mit Winkelkonvertierung
    def _to_radians(self, x):
        if self.angle_mode == 'deg':
            return math.radians(x)
        elif self.angle_mode == 'grad':
            return x * math.pi / 200
        else:  # rad
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
            # Ersetzungen für Benutzerfreundlichkeit
            expr = expr.replace("^", "**")
            # Komplexe Zahlen: j wird zu J (Python erwartet J, aber wir lassen j zu)
            # Python kann auch 'j' verstehen
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
            # Für komplexe Zahlen: wenn j, dann 1j
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
# II. GUI mit erweiterten Features
# ============================================================
class UltimateCalculatorGUI:
    def __init__(self):
        self.history = []  # Liste von (ausdruck, ergebnis)
        self.angle_mode = 'deg'  # deg, rad, grad
        self.use_complex = False
        self.theme = 'light'  # light, dark, blue
        
        self.evaluator = SafeEvaluator(angle_mode=self.angle_mode, use_complex=self.use_complex)
        
        # Fenster erstellen
        self.win = RoundWindow(480, 650, "Scientific Pro Calculator",
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
        # Header mit Statusleiste für Modus
        self.header_frame = tk.Frame(self.inner, bg=self.inner.cget('bg'))
        self.header_frame.pack(fill="x", pady=(5,0))
        
        self.mode_label = tk.Label(self.header_frame, text="Deg", font=("Segoe UI", 9),
                                    bg=self.inner.cget('bg'), fg="black")
        self.mode_label.pack(side="left", padx=5)
        
        # Display
        self.display = tk.Entry(self.inner, font=("Helvetica", 32),
                                bg="#f0f0f0", fg="black", bd=1, relief="solid", justify="right")
        self.display.pack(fill="x", padx=20, pady=10)
        
        # History-Button und kurze Anzeige (optional)
        self.history_btn = tk.Button(self.inner, text="📜 History", font=("Segoe UI", 9),
                                      command=self.show_history, bg="#e0e0e0", fg="black",
                                      bd=0, padx=5, pady=2)
        self.history_btn.pack(anchor="ne", padx=20, pady=2)
        
        # Frame für Buttons
        btn_frame = tk.Frame(self.inner, bg=self.inner.cget('bg'))
        btn_frame.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        # Button-Definitionen: (Text, row, col, bg, optional colspan)
        # Wir erweitern um zusätzliche Buttons für Komplex, Modus, Theme
        buttons = [
            # Wissenschaftliche Funktionen
            ('sin', 0, 0, "#e0e0e0"), ('cos', 0, 1, "#e0e0e0"), ('tan', 0, 2, "#e0e0e0"), ('asin', 0, 3, "#e0e0e0"), ('acos', 0, 4, "#e0e0e0"),
            ('atan', 1, 0, "#e0e0e0"), ('sinh', 1, 1, "#e0e0e0"), ('cosh', 1, 2, "#e0e0e0"), ('tanh', 1, 3, "#e0e0e0"), ('log', 1, 4, "#e0e0e0"),
            ('sqrt', 2, 0, "#e0e0e0"), ('^', 2, 1, "#e0e0e0"), ('(', 2, 2, "#d9d9d9"), (')', 2, 3, "#d9d9d9"), ('C', 2, 4, "#FFCDD2"),
            ('←', 3, 0, "#d9d9d9"), ('7', 3, 1, "#ffffff"), ('8', 3, 2, "#ffffff"), ('9', 3, 3, "#ffffff"), ('/', 3, 4, "#FFB74D"),
            ('4', 4, 0, "#ffffff"), ('5', 4, 1, "#ffffff"), ('6', 4, 2, "#ffffff"), ('*', 4, 3, "#FFB74D"), ('-', 4, 4, "#FFB74D"),
            ('1', 5, 0, "#ffffff"), ('2', 5, 1, "#ffffff"), ('3', 5, 2, "#ffffff"), ('+', 5, 3, "#FFB74D"), ('=', 5, 4, "#4CAF50", 2),
            ('0', 6, 0, "#ffffff", 2), ('.', 6, 2, "#ffffff"), ('pi', 6, 3, "#d9d9d9"), ('e', 6, 4, "#d9d9d9"),
            ('ans', 7, 0, "#d9d9d9"), ('j', 7, 1, "#d9d9d9"), ('Modus', 7, 2, "#d9d9d9"), ('Komplex', 7, 3, "#d9d9d9"), ('Theme', 7, 4, "#d9d9d9"),
        ]
        
        # Wir müssen die Liste anders aufbauen, da wir unterschiedliche Spans haben.
        # Besser: Manuell erstellen, aber wir iterieren hier mit Anpassungen.
        # Wir verwenden eine Schleife, aber für '=' und '0' mit Spans müssen wir aufpassen.
        # Einfacher: Wir erstellen die Buttons einzeln, aber das ist lang. Ich mache es in zwei Durchgängen.
        
        # Zuerst normale Buttons
        btn_data = [
            ('sin', 0, 0), ('cos', 0, 1), ('tan', 0, 2), ('asin', 0, 3), ('acos', 0, 4),
            ('atan', 1, 0), ('sinh', 1, 1), ('cosh', 1, 2), ('tanh', 1, 3), ('log', 1, 4),
            ('sqrt', 2, 0), ('^', 2, 1), ('(', 2, 2), (')', 2, 3), ('C', 2, 4),
            ('←', 3, 0), ('7', 3, 1), ('8', 3, 2), ('9', 3, 3), ('/', 3, 4),
            ('4', 4, 0), ('5', 4, 1), ('6', 4, 2), ('*', 4, 3), ('-', 4, 4),
            ('1', 5, 0), ('2', 5, 1), ('3', 5, 2), ('+', 5, 3), 
            ('0', 6, 0), ('.', 6, 2), ('pi', 6, 3), ('e', 6, 4),
            ('ans', 7, 0), ('j', 7, 1), ('Modus', 7, 2), ('Komplex', 7, 3), ('Theme', 7, 4),
        ]
        
        # Farben zuweisen
        def get_color(txt):
            if txt in ['C']:
                return "#FFCDD2"
            elif txt in ['/', '*', '-', '+']:
                return "#FFB74D"
            elif txt == '=':
                return "#4CAF50"
            elif txt in ['sin','cos','tan','asin','acos','atan','sinh','cosh','tanh','log','sqrt','^']:
                return "#e0e0e0"
            elif txt in ['(',')','←','ans','j','Modus','Komplex','Theme','pi','e']:
                return "#d9d9d9"
            else:
                return "#ffffff"
        
        for (txt, r, c) in btn_data:
            clr = get_color(txt)
            btn = tk.Button(btn_frame, text=txt, font=("Helvetica", 11, "bold"),
                            bg=clr, fg="black", bd=0, relief="flat",
                            activebackground="#c0c0c0", activeforeground="black",
                            command=lambda t=txt: self._on_btn(t))
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
        
        # '=' extra mit Spalte 4 und 5
        btn_eq = tk.Button(btn_frame, text='=', font=("Helvetica", 11, "bold"),
                           bg="#4CAF50", fg="white", bd=0, relief="flat",
                           activebackground="#367c39", activeforeground="white",
                           command=lambda: self._on_btn('='))
        btn_eq.grid(row=5, column=4, rowspan=1, columnspan=2, padx=2, pady=2, sticky="nsew")
        
        # '0' mit Spalte 0-1
        btn_0 = tk.Button(btn_frame, text='0', font=("Helvetica", 11, "bold"),
                          bg="#ffffff", fg="black", bd=0, relief="flat",
                          activebackground="#c0c0c0", activeforeground="black",
                          command=lambda: self._on_btn('0'))
        btn_0.grid(row=6, column=0, columnspan=2, padx=2, pady=2, sticky="nsew")
        
        # Spalten konfigurieren
        for i in range(5):
            btn_frame.columnconfigure(i, weight=1)
        # Zeilen 0-7
        for i in range(8):
            btn_frame.rowconfigure(i, weight=1)
    
    def _on_btn(self, char):
        if char == 'C':
            self.display.delete(0, tk.END)
        elif char == '←':
            self.display.delete(len(self.display.get())-1, tk.END)
        elif char == '=':
            self._calc()
        elif char == 'Modus':
            self._cycle_angle_mode()
        elif char == 'Komplex':
            self._toggle_complex()
        elif char == 'Theme':
            self._cycle_theme()
        else:
            self.display.insert(tk.END, char)
    
    def _key_press(self, event):
        # Verhindern, dass bestimmte Tasten das Fenster schließen
        if event.keysym in ('Return', 'Escape', 'BackSpace'):
            return
        # Normale Zeichen einfügen
        char = event.char
        if char and char.isprintable():
            self.display.insert(tk.END, char)
    
    def _calc(self):
        expr = self.display.get()
        res = self.evaluator.evaluate(expr)
        
        # Ergebnis formatieren
        if isinstance(res, float):
            if abs(res) < 1e-10:
                res = 0.0
            res_str = f"{res:.10f}".rstrip('0').rstrip('.') if '.' in f"{res:.10f}" else str(res)
        elif isinstance(res, complex):
            # Komplexe Zahl formatieren
            res_str = f"{res.real:.10f}".rstrip('0').rstrip('.') if abs(res.imag) < 1e-10 else str(res)
        else:
            res_str = str(res)
        
        self.display.delete(0, tk.END)
        self.display.insert(0, res_str)
        
        # History speichern
        self.history.append((expr, res_str))
        
        # ans aktualisieren
        try:
            self.evaluator.vars["ans"] = float(res) if not isinstance(res, complex) else complex(res)
        except:
            pass
    
    def show_history(self):
        if not self.history:
            messagebox.showinfo("History", "Keine Einträge vorhanden.")
            return
        
        # Neues Fenster mit abgerundeten Ecken
        hist_win = RoundWindow(400, 300, "Verlauf", bg_color="#ffffff", title_color="#000000")
        hist_root = hist_win.root
        hist_inner = hist_win.inner_frame
        
        listbox = tk.Listbox(hist_inner, font=("Courier", 10), bg="#f0f0f0", fg="black")
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        for expr, res in self.history[-20:]:  # letzte 20 anzeigen
            listbox.insert(tk.END, f"{expr} = {res}")
        
        scrollbar = tk.Scrollbar(listbox, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=listbox.yview)
        
        tk.Button(hist_inner, text="Schließen", command=hist_root.destroy,
                  bg="#e0e0e0", fg="black", bd=0, padx=10, pady=2).pack(pady=5)
        
        hist_root.mainloop()
    
    def _cycle_angle_mode(self):
        modes = ['deg', 'rad', 'grad']
        idx = modes.index(self.angle_mode)
        self.angle_mode = modes[(idx+1) % 3]
        self.evaluator.angle_mode = self.angle_mode
        self.mode_label.config(text=self.angle_mode.capitalize())
    
    def _toggle_complex(self):
        self.use_complex = not self.use_complex
        self.evaluator.use_complex = self.use_complex
        self.evaluator.update_functions()
        # Button farblich anpassen? Wir ändern den Text
        # Geht nicht direkt, wir suchen den Button 'Komplex' und ändern dessen Farbe
        # Wir könnten das später implementieren, fürs erste nur Statuslabel
        self.mode_label.config(text=f"{self.angle_mode.capitalize()} {'Complex' if self.use_complex else 'Real'}")
    
    def _cycle_theme(self):
        themes = ['light', 'dark', 'blue']
        idx = themes.index(self.theme)
        self.theme = themes[(idx+1) % 3]
        self._apply_theme()
    
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
        
        # Hintergrund des Hauptfensters ändern
        self.root.configure(bg=bg_main)
        self.win.canvas.configure(bg=bg_main)
        self.win.canvas.delete("all")
        self.win.canvas.create_round_rect(5, 5, 475, 645, r=20, fill=bg_main, outline="#cccccc", width=2)
        self.inner.configure(bg=bg_main)
        
        # Header
        self.header_frame.configure(bg=bg_main)
        self.mode_label.configure(bg=bg_main, fg=fg_main)
        
        # Display
        self.display.configure(bg=display_bg, fg=fg_main)
        
        # History-Button
        self.history_btn.configure(bg=special_bg, fg=fg_main)
        
        # Alle Buttons im btn_frame müssen neu konfiguriert werden
        # Das ist aufwändig, wir iterieren über alle Kinder von btn_frame
        btn_frame = self.inner.winfo_children()[3]  # Achtung, Index könnte sich ändern
        if isinstance(btn_frame, tk.Frame):
            for child in btn_frame.winfo_children():
                if isinstance(child, tk.Button):
                    txt = child.cget("text")
                    if txt in ['C']:
                        child.configure(bg="#FFCDD2" if self.theme=='light' else "#d32f2f", fg=fg_main)
                    elif txt in ['/', '*', '-', '+']:
                        child.configure(bg="#FFB74D" if self.theme=='light' else "#f57c00", fg=fg_main)
                    elif txt == '=':
                        child.configure(bg="#4CAF50", fg="white")
                    elif txt in ['sin','cos','tan','asin','acos','atan','sinh','cosh','tanh','log','sqrt','^']:
                        child.configure(bg=special_bg, fg=fg_main)
                    elif txt in ['(',')','←','ans','j','Modus','Komplex','Theme','pi','e']:
                        child.configure(bg=special_bg, fg=fg_main)
                    else:
                        child.configure(bg=btn_bg, fg=fg_main)
        
        # Für '0' und '=' extra
        # '0' ist btn_0, aber wir finden es nicht einzeln; es ist bereits in der Schleife enthalten

# ------------------------------------------------------------
# Hauptprogramm
# ------------------------------------------------------------
if __name__ == "__main__":
    app = UltimateCalculatorGUI()
    app.root.mainloop()
