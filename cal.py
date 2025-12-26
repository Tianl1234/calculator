import ast
import operator
import math
import sys
from decimal import Decimal, getcontext, Context, DivisionByZero
from fractions import Fraction

import tkinter as tk
from tkinter import ttk

# ============================================================
#  DEIN SICHERER AST-EVALUATOR (unverändert, nur eingebettet)
# ============================================================

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: lambda x: x,
}

_MATH_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "ln": lambda x: math.log(x),
    "sqrt": math.sqrt,
    "abs": abs,
    "max": max,
    "min": min,
    "pow": math.pow,
}

_CONSTS = {
    "pi": math.pi,
    "e": math.e,
}

class EvalError(ValueError):
    pass

def _to_decimal(value, ctx: Context = None):
    if isinstance(value, Decimal):
        return value
    if isinstance(value, Fraction):
        return Decimal(value.numerator) / Decimal(value.denominator)
    return Decimal(str(value)) if not isinstance(value, float) else Decimal(repr(value))

def _to_fraction(value):
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        tup = value.as_tuple()
        digits = 0
        for d in tup.digits:
            digits = digits * 10 + d
        exp = tup.exponent
        if exp >= 0:
            return Fraction(digits * (10 ** exp))
        else:
            return Fraction(digits, 10 ** (-exp))
    return Fraction(value)

def eval_expr(expr: str, mode: str = "float", precision: int | None = None):
    if mode not in ("float", "decimal", "fraction"):
        raise EvalError("Unbekannter Modus")

    ctx = None
    if mode == "decimal":
        if precision is None:
            precision = 28
        ctx = getcontext().copy()
        ctx.prec = int(precision)

    def convert_number(n):
        if mode == "float":
            return float(n)
        if mode == "fraction":
            return Fraction(n)
        return _to_decimal(n, ctx)

    def convert_const(name):
        if name not in _CONSTS:
            raise EvalError(f"Unbekannter Name: {name}")
        val = _CONSTS[name]
        if mode == "float":
            return float(val)
        if mode == "fraction":
            return Fraction(val)
        return _to_decimal(val, ctx)

    def make_function(name):
        if name not in _MATH_FUNCS:
            raise EvalError(f"Unbekannte Funktion: {name}")
        func = _MATH_FUNCS[name]

        def wrapper(*args):
            if mode == "fraction":
                if name == "abs":
                    return abs(_to_fraction(args[0]))
                if name == "max":
                    return max(_to_fraction(a) for a in args)
                if name == "min":
                    return min(_to_fraction(a) for a in args)
                if name == "pow":
                    base, exp = (_to_fraction(a) for a in args)
                    if exp.denominator != 1:
                        raise EvalError("pow mit nicht-ganzzahligem Exponenten im Fraction-Modus nicht erlaubt")
                    return base ** int(exp)
                raise EvalError(f"Funktion {name} nicht im Fraction-Modus unterstützt")

            if mode == "decimal":
                if name == "sqrt":
                    try:
                        return ctx.sqrt(args[0])
                    except Exception:
                        return _to_decimal(math.sqrt(float(args[0])), ctx)
                if name in ("log", "ln"):
                    return _to_decimal(math.log(float(args[0])), ctx)
                if name in ("sin", "cos", "tan"):
                    return _to_decimal(func(float(args[0])), ctx)
                if name == "pow":
                    a, b = args
                    if isinstance(b, Decimal) and b == b.to_integral_value():
                        return a ** int(b)
                    return _to_decimal(math.pow(float(a), float(b)), ctx)
                if name in ("max", "min"):
                    return max(args)
                return _to_decimal(func(float(args[0])), ctx)

            return func(*[float(a) for a in args])

        return wrapper

    def _eval(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return convert_number(node.value)
            raise EvalError("Nur Zahlen als Konstanten erlaubt")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in OPS:
                raise EvalError("Nicht unterstützter Operator")
            left = _eval(node.left)
            right = _eval(node.right)
            func = OPS[op_type]
            try:
                return func(left, right)
            except ZeroDivisionError:
                raise
            except Exception as e:
                if mode == "decimal":
                    return func(_to_decimal(left, ctx), _to_decimal(right, ctx))
                if mode == "fraction":
                    return func(_to_fraction(left), _to_fraction(right))
                raise EvalError(str(e))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in OPS:
                raise EvalError("Nicht unterstützter Unary-Operator")
            return OPS[op_type](_eval(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise EvalError("Nur einfache Funktionsaufrufe erlaubt")
            fname = node.func.id
            func = make_function(fname)
            args = tuple(_eval(a) for a in node.args)
            return func(*args)

        if isinstance(node, ast.Name):
            return convert_const(node.id)

        raise EvalError("Ungültiger Ausdruck")

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise EvalError("Syntaxfehler")

    return _eval(tree.body)

# ============================================================
#  MODERNES HANDY-GUI LAYOUT
# ============================================================

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sicherer Taschenrechner")
        self.root.configure(bg="#111111")
        self.root.resizable(False, False)

        self.mode_var = tk.StringVar(value="float")

        # Display
        self.display = tk.Entry(
            root,
            font=("Helvetica", 32),
            bd=0,
            bg="#000000",
            fg="#00FF7F",
            insertbackground="#00FF7F",
            justify="right",
            relief="flat",
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=15, pady=(20, 10), sticky="nsew", ipady=20)

        btn_cfg = {
            "font": ("Helvetica", 22),
            "bd": 0,
            "width": 4,
            "height": 2,
            "relief": "flat",
            "activebackground": "#333333",
            "activeforeground": "white",
        }

        buttons = [
            ("C", 1, 0, "#D32F2F"),
            ("←", 1, 1, "#444444"),
            ("(", 1, 2, "#444444"),
            (")", 1, 3, "#444444"),

            ("7", 2, 0, "#222222"),
            ("8", 2, 1, "#222222"),
            ("9", 2, 2, "#222222"),
            ("/", 2, 3, "#1E88E5"),

            ("4", 3, 0, "#222222"),
            ("5", 3, 1, "#222222"),
            ("6", 3, 2, "#222222"),
            ("*", 3, 3, "#1E88E5"),

            ("1", 4, 0, "#222222"),
            ("2", 4, 1, "#222222"),
            ("3", 4, 2, "#222222"),
            ("-", 4, 3, "#1E88E5"),

            ("0", 5, 0, "#222222"),
            (".", 5, 1, "#222222"),
            ("+", 5, 2, "#1E88E5"),
            ("=", 5, 3, "#43A047"),
        ]

        for (text, r, c, color) in buttons:
            self._create_button(text, r, c, color, btn_cfg)

        # Modus-Auswahl
        mode_frame = tk.Frame(root, bg="#111111")
        mode_frame.grid(row=6, column=0, columnspan=4, pady=10)

        tk.Label(mode_frame, text="Modus:", fg="white", bg="#111111").pack(side="left")

        for m in ("float", "decimal", "fraction"):
            rb = tk.Radiobutton(
                mode_frame,
                text=m,
                variable=self.mode_var,
                value=m,
                fg="white",
                bg="#111111",
                selectcolor="#111111",
                activebackground="#111111",
                activeforeground="white",
                indicatoron=False,
                width=8,
                relief="ridge",
                bd=1,
                padx=2,
                pady=2,
            )
            rb.pack(side="left", padx=4)

        self.root.bind("<Return>", lambda e: self.calculate())
        self.root.bind("<KP_Enter>", lambda e: self.calculate())
        self.root.bind("<BackSpace>", lambda e: self.backspace())

    def _create_button(self, text, row, col, color, cfg):
        if text == "C":
            cmd = self.clear
        elif text == "←":
            cmd = self.backspace
        elif text == "=":
            cmd = self.calculate
        else:
            cmd = lambda t=text: self.insert_text(t)

        btn = tk.Button(self.root, text=text, command=cmd, bg=color, fg="white", **cfg)
        btn.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def insert_text(self, text):
        if text == "^":
            text = "**"
        pos = self.display.index(tk.INSERT)
        self.display.insert(pos, text)

    def clear(self):
        self.display.delete(0, tk.END)

    def backspace(self):
        pos = self.display.index(tk.INSERT)
        if pos > 0:
            self.display.delete(pos - 1)

    def calculate(self):
        expr = self.display.get().strip()
        if not expr:
            return
        mode = self.mode_var.get()
        try:
            res = eval_expr(expr, mode=mode, precision=28)
        except (DivisionByZero, ZeroDivisionError):
            self.display.delete(0, tk.END)
            self.display.insert(0, "Fehler: Division durch Null")
        except EvalError as e:
            self.display.delete(0, tk.END)
            self.display.insert(0, f"ungültig: {e}")
        except Exception:
            self.display.delete(0, tk.END)
            self.display.insert(0, "ungültig")
        else:
            self.display.delete(0, tk.END)
            self.display.insert(0, str(res))

def main():
    root = tk.Tk()
    CalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
