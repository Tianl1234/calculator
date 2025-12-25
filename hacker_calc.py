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
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in ops:
                raise ValueError
            return ops[op_type](_eval(node.left), _eval(node.right))

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in ops:
                raise ValueError
            return ops[op_type](_eval(node.operand))

        raise ValueError

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)


def main():
    while True:
        i = input("Rechnung (oder Enter zum Beenden): ")
        if not i.strip():
            break
        try:
            print(eval_expr(i))
        except Exception:
            print("ungültig")


if __name__ == "__main__":
    main()
