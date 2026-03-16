#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ===== Konsole sofort verstecken (für .pyw) =====
import sys
import ctypes

if sys.platform == "win32":
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel32.FreeConsole()

import ast
import operator
import math
import tkinter as tk

# ============================================================
# Hilfsfunktion für abgerundete Rechtecke
# ============================================================
def _create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
    points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1,
              x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2,
              x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2,
              x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
    return self.create_polygon(points, smooth=True, **kwargs)

tk.Canvas.create_round_rect = _create_round_rect

# ============================================================
# Custom Fensterklasse mit abgerundeten Ecken
# ============================================================
class RoundWindow:
    def __init__(self, width, height, title, bg_color="#121212", title_color="#2196F3"):
        self.root = tk.Toplevel() if tk._default_root else tk.Tk()
        self.root.overrideredirect(True)
        self.root.geometry(f"{width}x{height}+300+200")
        self.root.configure(bg=bg_color)

        # Canvas für Hintergrund mit abgerundeten Ecken
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg=bg_color, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_round_rect(5, 5, width-5, height-5, r=20, fill=bg_color, outline="#4a4a4a", width=2)

        # Eigene Titelleiste
        title_bar = tk.Frame(self.root, bg=bg_color, height=30)
        title_bar.place(x=10, y=10, width=width-20)

        title_label = tk.Label(title_bar, text=title, font=("Segoe UI", 10, "bold"),
                               fg=title_color, bg=bg_color)
        title_label.pack(side="left", padx=10)

        close_btn = tk.Button(title_bar, text="✕", font=("Segoe UI", 10, "bold"),
                              fg="white", bg=bg_color, bd=0, activebackground="#c42b1c",
                              activeforeground="white", cursor="hand2",
                              command=self.root.destroy)
        close_btn.pack(side="right", padx=10)

        # Verschieben
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)

        # Innenbereich für Widgets (auf dem Canvas)
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
# I. SICHERHEIT & MATHEMATIK (Der AST-Kern mit Funktionen)
# ============================================================
class SafeEvaluator:
    def __init__(self, last_result=None):
        self.ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.USub: operator.neg
        }
        self.funcs = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log
        }
        self.vars = {"pi": math.pi, "e": math.e, "ans": last_result if last_result else 0}

    def evaluate(self, expr):
        try:
            expr = expr.replace("€", "").replace("%", "/100").replace("^", "**")
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except Exception:
            return "Fehler"

    def _eval_node(self, node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name): return self.vars.get(node.id, 0)
        if isinstance(node, ast.BinOp):
            return self.ops[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            return self.ops[type(node.op)](self._eval_node(node.operand))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.funcs:
                args = [self._eval_node(arg) for arg in node.args]
                return self.funcs[node.func.id](*args)
        raise ValueError("Operation nicht erlaubt")

# ============================================================
# II. HIGH-END GUI (angepasst für RoundWindow)
# ============================================================
class UltimateCalculatorGUI:
    def __init__(self):
        # Abgerundetes Fenster erstellen
        self.win = RoundWindow(450, 550, "🧪 SCIENTIFIC PRO CALCULATOR", bg_color="#121212", title_color="#2196F3")
        self.root = self.win.root
        self.inner = self.win.inner_frame

        self.evaluator = SafeEvaluator()
        self._build_ui()

    def _build_ui(self):
        # Display
        self.display = tk.Entry(self.inner, font=("Helvetica", 32), bg="#121212", fg="white", bd=0, justify="right")
        self.display.pack(fill="x", padx=10, pady=(10, 20))

        # Button-Grid (5 Spalten x 6 Zeilen)
        btn_frame = tk.Frame(self.inner, bg="#121212")
        btn_frame.pack(fill="both", expand=True)

        buttons = [
            ('sin(', 0, 0, "#333333"), ('cos(', 0, 1, "#333333"), ('tan(', 0, 2, "#333333"), ('sqrt(', 0, 3, "#333333"), ('^', 0, 4, "#333333"),
            ('C', 1, 0, "#FF5252"), ('←', 1, 1, "#424242"), ('(', 1, 2, "#424242"), (')', 1, 3, "#424242"), ('/', 1, 4, "#FF9800"),
            ('7', 2, 0, "#2C2C2C"), ('8', 2, 1, "#2C2C2C"), ('9', 2, 2, "#2C2C2C"), ('ans', 2, 3, "#424242"), ('*', 2, 4, "#FF9800"),
            ('4', 3, 0, "#2C2C2C"), ('5', 3, 1, "#2C2C2C"), ('6', 3, 2, "#2C2C2C"), ('pi', 3, 3, "#424242"), ('-', 3, 4, "#FF9800"),
            ('1', 4, 0, "#2C2C2C"), ('2', 4, 1, "#2C2C2C"), ('3', 4, 2, "#2C2C2C"), ('e', 4, 3, "#424242"), ('+', 4, 4, "#FF9800"),
            ('0', 5, 0, "#2C2C2C"), ('.', 5, 1, "#2C2C2C"), ('=', 5, 2, "#4CAF50")
        ]

        for (txt, r, c, clr) in buttons:
            colspan = 3 if txt == '=' else 1
            btn = tk.Button(btn_frame, text=txt.replace('(', ''), font=("Helvetica", 14, "bold"),
                            bg=clr, fg="white", bd=0,
                            command=lambda t=txt: self._on_btn(t))
            btn.grid(row=r, column=c, columnspan=colspan, padx=2, pady=2, sticky="nsew")

        for i in range(5): btn_frame.columnconfigure(i, weight=1)
        for i in range(6): btn_frame.rowconfigure(i, weight=1)

    def _on_btn(self, char):
        if char == 'C':
            self.display.delete(0, tk.END)
        elif char == '←':
            self.display.delete(len(self.display.get())-1)
        elif char == '=':
            self._calc()
        else:
            self.display.insert(tk.END, char)

    def _calc(self):
        res = self.evaluator.evaluate(self.display.get())
        if isinstance(res, float) and abs(res) < 1e-10:
            res = 0.0
        self.display.delete(0, tk.END)
        self.display.insert(0, str(res))
        try:
            self.evaluator.vars["ans"] = float(res)
        except ValueError:
            pass

if __name__ == "__main__":
    app = UltimateCalculatorGUI()
    app.root.mainloop()
