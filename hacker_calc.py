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
    def _eval(node):
        if isinstance(node, ast.Num):  # Zahl
            return node.n
        if isinstance(node, ast.BinOp):  # z.B. 2 + 3
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):  # z.B. -3
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError("Ungültiger Ausdruck")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


while (i := input("Rechnung (oder Enter zum Beenden): ")).strip():
    try:
        print(eval_expr(i))
    except Exception:
        print("ungültig")
