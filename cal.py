import ast
import operator
import math
import argparse
import sys
from decimal import Decimal, getcontext, Context, DivisionByZero
from fractions import Fraction

# Allowed operators mapping
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

# Whitelisted functions (names -> callable)
# Note: Some functions behave differently depending on numeric mode.
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

# Named constants
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
    # ints and floats
    return Decimal(str(value)) if not isinstance(value, float) else Decimal(repr(value))


def _to_fraction(value):
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        # Convert Decimal to Fraction using as_tuple and exponent
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
        # n is an int or float
        if mode == "float":
            return float(n)
        if mode == "fraction":
            # Fraction accepts ints or floats
            return Fraction(n)
        # decimal
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
            # Validate/convert args based on mode
            if mode == "fraction":
                # Only a small safe subset works in fraction mode
                if name in ("abs", "max", "min", "pow"):
                    fargs = tuple(_to_fraction(a) for a in args)
                    # pow: if exponent is not integer, raise
                    if name == "pow":
                        base, exp = fargs
                        if exp.denominator != 1:
                            raise EvalError("pow mit nicht-ganzzahligem Exponenten in Fraction-Modus nicht erlaubt")
                        return base ** int(exp)
                    return getattr(__builtins__, name)(*fargs) if name in ("max", "min") else eval(name)(*fargs)
                # other functions not supported in fraction mode
                raise EvalError(f"Funktion {name} nicht im Fraction-Modus unterstützt")

            if mode == "decimal":
                # For Decimal mode: use Decimal-aware sqrt and pow where possible
                if name == "sqrt":
                    # use context sqrt
                    try:
                        return ctx.sqrt(args[0])
                    except Exception:
                        # fallback to float
                        return _to_decimal(math.sqrt(float(args[0])), ctx)
                if name in ("log", "ln"):
                    return _to_decimal(math.log(float(args[0])), ctx)
                if name in ("sin", "cos", "tan"):
                    return _to_decimal(func(float(args[0])), ctx)
                if name == "pow":
                    # Decimal pow may fail for non-integer exponents
                    a, b = args
                    # if exponent is integer, use **
                    if isinstance(b, Decimal) and b == b.to_integral_value():
                        return a ** int(b)
                    # fallback via float
                    return _to_decimal(math.pow(float(a), float(b)), ctx)
                if name in ("max", "min"):
                    return type(args[0])(max(*[float(a) for a in args])) if False else max(args)
                # default: call via float and convert
                return _to_decimal(func(float(args[0])), ctx) if len(args) == 1 else _to_decimal(func(*[float(a) for a in args]), ctx)

            # float mode
            return func(*[float(a) for a in args]) if name in ("sin", "cos", "tan", "log", "ln", "sqrt", "pow") else func(*args)

        return wrapper

    def _eval(node):
        # Constants (py3.8+: ast.Constant, older: ast.Num)
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
                # Handle mixing types for Decimal/Fraction
                if mode == "decimal":
                    # try converting operands to Decimal
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
            # Only allow simple function calls like fname(arg, ...)
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


def main():
    parser = argparse.ArgumentParser(description="Sicherer Taschenrechner (AST-basiert)")
    parser.add_argument("--mode", choices=("float", "decimal", "fraction"), default="float", help="numeric mode")
    parser.add_argument("--precision", type=int, default=28, help="decimal precision (only for decimal mode)")
    args = parser.parse_args()

    mode = args.mode
    precision = args.precision if mode == "decimal" else None

    try:
        import readline  # optional: improves interactive input
    except Exception:
        pass

    while True:
        try:
            i = input(f"[{mode}] Rechnung (oder Enter zum Beenden): ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not i.strip():
            break
        try:
            res = eval_expr(i, mode=mode, precision=precision)
        except DivisionByZero:
            print("Fehler: Division durch Null")
        except ZeroDivisionError:
            print("Fehler: Division durch Null")
        except EvalError as e:
            print(f"ungültig: {e}")
        except Exception:
            print("ungültig")
        else:
            print(res)


if __name__ == "__main__":
    main()
