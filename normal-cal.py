import ast
import operator
import math
import re
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, getcontext, DivisionByZero
from fractions import Fraction

# ============================================================
#  KONFIGURATION & DESIGN
# ============================================================

THEME = {
    "bg_main": "#121212",
    "bg_display": "#1e1e1e",
    "fg_display": "#ffffff",
    "btn_bg": "#2c2c2c",
    "btn_fg": "#ffffff",
    "btn_op_bg": "#ff9800",
    "btn_op_fg": "#000000",
    "btn_eq_bg": "#4caf50",
    "btn_eq_fg": "#ffffff",
    "btn_sci_bg": "#2196f3",
    "btn_sci_fg": "#ffffff",
    "highlight_bracket": "#3d3d3d"
}

# ============================================================
#  SICHERER AST-EVALUATOR
# ============================================================

class SafeEvaluator:
    OPS = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
        ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.UAdd: lambda x: x,
    }

    _MATH_FUNCS = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log, "ln": math.log, "sqrt": math.sqrt,
        "abs": abs, "pow": math.pow,
    }

    _CONSTS = {"pi": math.pi, "e": math.e}

    def __init__(self, mode="float", precision=28, last_result=None):
        self.mode = mode
        getcontext().prec = precision
        self.last_result = last_result

    def _preprocess(self, expr):
        expr = expr.replace("π", "pi").replace("^", "**")
        # Implizite Multiplikation (z.B. 2ans -> 2*ans, 2(3) -> 2*(3))
        expr = re.sub(r'(\d)\s*(ans|pi|e|sin|cos|tan|log|ln|sqrt|\()', r'\1*\2', expr)
        expr = re.sub(r'(ans|pi|e|\))\s*(\d|\()', r'\1*\2', expr)
        return expr

    def evaluate(self, expr):
        expr = self._preprocess(expr)
        if not expr.strip(): return None
        try:
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except SyntaxError:
            raise ValueError("Syntaxfehler")

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return self._convert(node.value)
        if isinstance(node, ast.Name):
            if node.id == "ans":
                if self.last_result is None: raise ValueError("Kein 'ans' verfügbar")
                return self.last_result
            if node.id in self._CONSTS: return self._convert(self._CONSTS[node.id])
            raise ValueError(f"Unbekannt: {node.id}")
        if isinstance(node, ast.BinOp):
            left, right = self._eval_node(node.left), self._eval_node(node.right)
            return self.OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp):
            return self.OPS[type(node.op)](self._eval_node(node.operand))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name): raise ValueError("Fehler")
            args = [float(self._eval_node(a)) for a in node.args]
            res = self._MATH_FUNCS[node.func.id](*args)
            return self._convert(res)
        raise ValueError("Struktur nicht unterstützt")

    def _convert(self, val):
        if self.mode == "decimal": return Decimal(str(val)) if not isinstance(val, float) else Decimal(repr(val))
        if self.mode == "fraction": return Fraction(val).limit_denominator()
        return float(val)

# ============================================================
#  GUI KLASSE
# ============================================================

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro-Calculator 2026")
        self.last_result = None
        self.history = []
        self.scientific_visible = False

        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        self.root.configure(bg=THEME["bg_main"])
        
        # Obere Status-Leiste
        top_bar = tk.Frame(self.root, bg=THEME["bg_main"])
        top_bar.pack(fill="x", padx=10, pady=(10, 0))
        
        self.mode_label = tk.Label(top_bar, text="Modus: Auto", bg=THEME["bg_main"], fg="#888", font=("Arial", 9))
        self.mode_label.pack(side="left")

        history_btn = tk.Button(top_bar, text="📜 Verlauf", bg=THEME["bg_main"], fg="#888", bd=0, 
                                cursor="hand2", command=self.show_history)
        history_btn.pack(side="right")

        # Display
        self.display = tk.Entry(self.root, font=("Segoe UI", 32), bd=0, justify="right",
                                bg=THEME["bg_display"], fg=THEME["fg_display"], 
                                insertbackground="white", highlightthickness=0)
        self.display.pack(fill="x", padx=10, pady=10, ipady=10)

        # Button Container
        self.container = tk.Frame(self.root, bg=THEME["bg_main"])
        self.container.pack(fill="both", expand=True, padx=5, pady=5)

        self.main_frame = tk.Frame(self.container, bg=THEME["bg_main"])
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.sci_frame = tk.Frame(self.container, bg=THEME["bg_main"])

        self._create_main_grid()
        self._create_sci_grid()

    def _create_main_grid(self):
        btns = [
            ('C', 0, 0, THEME["btn_op_bg"]), ('←', 0, 1, THEME["btn_op_bg"]), ('(', 0, 2, THEME["btn_op_bg"]), (')', 0, 3, THEME["btn_op_bg"]),
            ('7', 1, 0, THEME["btn_bg"]), ('8', 1, 1, THEME["btn_bg"]), ('9', 1, 2, THEME["btn_bg"]), ('/', 1, 3, THEME["btn_op_bg"]),
            ('4', 2, 0, THEME["btn_bg"]), ('5', 2, 1, THEME["btn_bg"]), ('6', 2, 2, THEME["btn_bg"]), ('*', 2, 3, THEME["btn_op_bg"]),
            ('1', 3, 0, THEME["btn_bg"]), ('2', 3, 1, THEME["btn_bg"]), ('3', 3, 2, THEME["btn_bg"]), ('-', 3, 3, THEME["btn_op_bg"]),
            ('0', 4, 0, THEME["btn_bg"]), ('.', 4, 1, THEME["btn_bg"]), ('ans', 4, 2, THEME["btn_bg"]), ('+', 4, 3, THEME["btn_op_bg"]),
            ('=', 5, 0, THEME["btn_eq_bg"]), ('Sci', 5, 3, THEME["btn_sci_bg"])
        ]
        for (text, r, c, color) in btns:
            if text == '=':
                cmd = self.calculate
                b = tk.Button(self.main_frame, text=text, font=("Arial", 14, "bold"), bg=color, fg="white", bd=0, command=cmd)
                b.grid(row=r, column=c, columnspan=3, padx=2, pady=2, sticky="nsew")
            else:
                cmd = self.toggle_sci if text == 'Sci' else lambda t=text: self._handle_btn(t)
                b = tk.Button(self.main_frame, text=text, width=5, height=2, font=("Arial", 12), bg=color, fg="white", bd=0, command=cmd)
                b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        for i in range(4): self.main_frame.columnconfigure(i, weight=1)
        for i in range(6): self.main_frame.rowconfigure(i, weight=1)

    def _create_sci_grid(self):
        sci_btns = [('sin', 0, 0), ('cos', 0, 1), ('tan', 1, 0), ('sqrt', 1, 1),
                    ('log', 2, 0), ('ln', 2, 1), ('pi', 3, 0), ('e', 3, 1)]
        for (text, r, c) in sci_btns:
            b = tk.Button(self.sci_frame, text=text, width=6, height=2, font=("Arial", 11),
                          bg=THEME["btn_sci_bg"], fg="white", bd=0, 
                          command=lambda t=text: self.display.insert(tk.INSERT, t+"("))
            b.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

    def _handle_btn(self, text):
        if text == 'C': self.display.delete(0, tk.END)
        elif text == '←': self.display.delete(self.display.index(tk.INSERT)-1)
        else: self.display.insert(tk.INSERT, text)
        self._highlight_brackets()

    def toggle_sci(self):
        if self.scientific_visible:
            self.sci_frame.pack_forget()
        else:
            self.sci_frame.pack(side="right", padx=5, pady=5, fill="both")
        self.scientific_visible = not self.scientific_visible

    def calculate(self):
        expr = self.display.get()
        if not expr: return
        mode = "decimal" if any(x in expr for x in ".(sinπcoslogsqrt") else "fraction"
        self.mode_label.config(text=f"Modus: {mode.capitalize()}")
        
        eval_engine = SafeEvaluator(mode=mode, last_result=self.last_result)
        try:
            res = eval_engine.evaluate(expr)
            if isinstance(res, Fraction): out = f"{res.numerator}/{res.denominator}"
            elif isinstance(res, Decimal): out = format(res.normalize(), "g")
            else: out = f"{res:.10g}"
            
            self.history.append(f"{expr} = {out}")
            self.last_result = res
            self.display.delete(0, tk.END)
            self.display.insert(0, out)
        except Exception as e:
            messagebox.showerror("Mathematik-Fehler", str(e))

    # ================== ZUSATZFUNKTIONEN ==================

    def _bind_events(self):
        self.display.bind("<KeyRelease>", self._highlight_brackets)
        self.root.bind("<Return>", lambda e: self.calculate())

    def _highlight_brackets(self, event=None):
        text = self.display.get()
        pos = self.display.index(tk.INSERT)
        self.display.config(bg=THEME["bg_display"])
        
        if pos > 0 and pos <= len(text):
            char = text[pos-1]
            match_pos = None
            if char == ")": match_pos = self._find_match(text, pos-1, -1, "(", ")")
            elif char == "(": match_pos = self._find_match(text, pos-1, 1, ")", "(")
            
            if match_pos is not None:
                self.display.config(bg=THEME["highlight_bracket"])
                self.root.after(250, lambda: self.display.config(bg=THEME["bg_display"]))

    def _find_match(self, text, start, step, target, other):
        count = 0
        for i in range(start, -1 if step == -1 else len(text), step):
            if text[i] == other: count += 1
            elif text[i] == target: count -= 1
            if count == 0: return i
        return None

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("Letzte Rechnungen")
        win.geometry("300x400")
        win.configure(bg=THEME["bg_main"])
        
        lb = tk.Listbox(win, bg=THEME["bg_display"], fg="white", bd=0, font=("Arial", 11))
        lb.pack(fill="both", expand=True, padx=10, pady=10)
        
        for item in reversed(self.history): lb.insert(tk.END, item)
        
        def pick(e):
            if not lb.curselection(): return
            val = lb.get(lb.curselection()).split(" = ")[1]
            self.display.insert(tk.INSERT, val)
            win.destroy()
        
        lb.bind("<Double-Button-1>", pick)

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(350, 500)
    app = CalculatorGUI(root)
    root.mainloop()
