import ast
import operator

# Erlaubte Operatoren
ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def eval_expr(expr):
    """Sicherer mathematischer Ausdrucksparser."""
    def _eval(node):
        if isinstance(node, ast.Num):  # Zahl
            return node.n
        if isinstance(node, ast.BinOp):  # z.B. 2 + 3
            if type(node.op) not in ops:
                raise ValueError
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):  # z.B. -3
            if type(node.op) not in ops:
                raise ValueError
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


# Hauptschleife
while (i := input("Rechnung (oder Enter zum Beenden): ")).strip():
    try:
        print(eval_expr(i))
    except Exception:
        print("ungültig")
