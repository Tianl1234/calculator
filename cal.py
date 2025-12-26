import ast
import operator
import math
import sys
from decimal import Decimal, getcontext, Context, DivisionByZero
from fractions import Fraction

import tkinter as tk
from tkinter import ttk

# -----------------------------
# Dein Evaluator-Code (leicht angepasst: kein readline, keine CLI)
# -----------------------------

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
    # ints und floats
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
    """
    Evaluate an arithmetic expression safely.
    mode: 'float' | 'decimal' | 'fraction'
    precision: number of decimal places (only for decimal mode)
    """

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
                        raise EvalError(
                            "pow mit nicht-ganzzahligem Exponenten im Fraction-Modus nicht erlaubt"
                        )
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
                return (
                    _to_decimal(func(float(args[0])), ctx)
                    if len(args) == 1
                    else _to_decimal(func(*[float(a) for a in args]), ctx)
                )

            # float mode
            return (
                func(*[float(a) for a in args])
                if name in ("sin", "cos", "tan", "log", "ln", "sqrt", "pow")
                else func(*args)
            )

        return wrapper

    def _eval(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return convert_number(node.value)
            raise EvalError("Nur Zahlen als Konstanten erlaubt")
        if sys.version_info < (3, 8) and isinstance(node, ast.Num):
            return convert_number(node.n)

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
                    l = _to_decimal(left, ctx)
                    r = _to_decimal(right, ctx)
                    try:
                        return func(l, r)
                    except Exception:
                        raise EvalError(str(e))
                if mode == "fraction":
                    l = _to_fraction(left)
                    r = _to_fraction(right)
                    try:
                        return func(l, r)
                    except Exception:
                        raise EvalError(str(e))
                raise EvalError(str(e))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in OPS:
                raise EvalError("Nicht unterstützter Unary-Operator")
            val = _eval(node.operand)
            return OPS[op_type](val)

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

    if not isinstance(tree, ast.Expression):
        raise EvalError("Nur Ausdrücke erlaubt")

    return _eval(tree.body)


# -----------------------------
# GUI-Teil
# -----------------------------

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sicherer Taschenrechner")

        # Fenster optisch etwas "handyhaft"
        self.root.resizable(False, False)
        self.root.configure(bg="#202124")

        self.mode_var = tk.StringVar(value="float")
        self.precision = 28

        # Display
        self.display = tk.Entry(
            root,
            font=("SF Pro Text", 24),
            bd=0,
            bg="#000000",
            fg="#00FF7F",
            insertbackground="#00FF7F",
            justify="right",
        )
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=10, sticky="nsew", ipady=10)

        # Buttons definieren
        # text, row, col, colspan (optional), style
        buttons = [
            ("C", 1, 0), ("←", 1, 1), ("(", 1, 2), (")", 1, 3), ("/", 1, 4),
            ("sin", 2, 0), ("cos", 2, 1), ("tan", 2, 2), ("//", 2, 3), ("%", 2, 4),
            ("7", 3, 0), ("8", 3, 1), ("9", 3, 2), ("*", 3, 3), ("^", 3, 4),
            ("4", 4, 0), ("5", 4, 1), ("6", 4, 2), ("-", 4, 3), ("sqrt", 4, 4),
            ("1", 5, 0), ("2", 5, 1), ("3", 5, 2), ("+", 5, 3), ("log", 5, 4),
            ("0", 6, 0), (".", 6, 1), ("pi", 6, 2), ("e", 6, 3), ("=", 6, 4),
        ]

        for (text, r, c) in buttons:
            self._create_button(text, r, c)

        # Modus-Auswahl (float/decimal/fraction)
        mode_frame = tk.Frame(root, bg="#202124")
        mode_frame.grid(row=7, column=0, columnspan=5, pady=(5, 10))

        tk.Label(mode_frame, text="Modus:", fg="white", bg="#202124").pack(side="left")

        for m in ("float", "decimal", "fraction"):
            rb = tk.Radiobutton(
                mode_frame,
                text=m,
                variable=self.mode_var,
                value=m,
                fg="white",
                bg="#202124",
                selectcolor="#202124",
                activebackground="#202124",
                activeforeground="white",
                indicatoron=False,
                width=8,
                relief="ridge",
                bd=1,
                padx=2,
                pady=2,
            )
            rb.pack(side="left", padx=2)

        # Keyboard-Events
        self.root.bind("<Return>", lambda e: self.calculate())
        self.root.bind("<KP_Enter>", lambda e: self.calculate())
        self.root.bind("<BackSpace>", lambda e: self.backspace())

    def _create_button(self, text, row, col):
        cmd = None
        if text == "C":
            cmd = self.clear
            bg = "#8B0000"
        elif text == "←":
            cmd = self.backspace
            bg = "#444444"
        elif text == "=":
            cmd = self.calculate
            bg = "#1E90FF"
        else:
            cmd = lambda t=text: self.insert_text(t)
            bg = "#333333"

        button = tk.Button(
            self.root,
            text=text,
            command=cmd,
            font=("SF Pro Text", 16),
            bg=bg,
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            bd=0,
            relief="flat",
            width=4,
            height=2,
        )
        button.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

    def insert_text(self, text):
        # ^ auf ** mappen, damit dein AST-Pow funktioniert
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
        except DivisionByZero:
            self.display.delete(0, tk.END)
            self.display.insert(0, "Fehler: Division durch Null")
        except ZeroDivisionError:
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
