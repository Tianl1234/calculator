import ast, operator, math
import tkinter as tk

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
        # NEU: Erlaubte mathematische Funktionen
        self.funcs = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log
        }
        self.vars = {"pi": math.pi, "e": math.e, "ans": last_result if last_result else 0}

    def evaluate(self, expr):
        try:
            # ^ wird zu ** (Python-Syntax für Hochrechnen)
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
        # NEU: Funktionsaufrufe verarbeiten (z.B. sin(90))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.funcs:
                args = [self._eval_node(arg) for arg in node.args]
                return self.funcs[node.func.id](*args)
        raise ValueError("Operation nicht erlaubt")

# ============================================================
# II. HIGH-END GUI (Wissenschaftlich erweitert)
# ============================================================
class UltimateCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Calculator")
        self.root.geometry("450x550") # Etwas breiter für 5 Spalten
        self.root.configure(bg="#121212")

        self.evaluator = SafeEvaluator()
        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Label(self.root, text="🧪 SCIENTIFIC PRO CALCULATOR", bg="#121212", fg="#2196F3", font=("Helvetica", 10, "bold"))
        header.pack(pady=(15, 0))

        # Display
        self.display = tk.Entry(self.root, font=("Helvetica", 32), bg="#121212", fg="white", bd=0, justify="right")
        self.display.pack(fill="x", padx=20, pady=20)

        # Button-Grid (5 Spalten x 6 Zeilen)
        btn_frame = tk.Frame(self.root, bg="#121212")
        btn_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        buttons = [
            ('sin(', 0, 0, "#333333"), ('cos(', 0, 1, "#333333"), ('tan(', 0, 2, "#333333"), ('sqrt(', 0, 3, "#333333"), ('^', 0, 4, "#333333"),
            ('C', 1, 0, "#FF5252"), ('←', 1, 1, "#424242"), ('(', 1, 2, "#424242"), (')', 1, 3, "#424242"), ('/', 1, 4, "#FF9800"),
            ('7', 2, 0, "#2C2C2C"), ('8', 2, 1, "#2C2C2C"), ('9', 2, 2, "#2C2C2C"), ('ans', 2, 3, "#424242"), ('*', 2, 4, "#FF9800"),
            ('4', 3, 0, "#2C2C2C"), ('5', 3, 1, "#2C2C2C"), ('6', 3, 2, "#2C2C2C"), ('pi', 3, 3, "#424242"), ('-', 3, 4, "#FF9800"),
            ('1', 4, 0, "#2C2C2C"), ('2', 4, 1, "#2C2C2C"), ('3', 4, 2, "#2C2C2C"), ('e', 4, 3, "#424242"), ('+', 4, 4, "#FF9800"),
            ('0', 5, 0, "#2C2C2C"), ('.', 5, 1, "#2C2C2C"), ('=', 5, 2, "#4CAF50")
        ]

        for (txt, r, c, clr) in buttons:
            # Das '=' Zeichen wird breiter gemacht (spannt über 3 Spalten)
            colspan = 3 if txt == '=' else 1
            
            btn = tk.Button(btn_frame, text=txt.replace('(', ''), font=("Helvetica", 14, "bold"), bg=clr, fg="white", bd=0, 
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
        
        # Rundung bei minimalen Float-Fehlern (z.B. sin(pi) sollte 0 sein, nicht 1.22e-16)
        if isinstance(res, float) and abs(res) < 1e-10:
            res = 0.0
            
        self.display.delete(0, tk.END)
        self.display.insert(0, str(res))
        
        try:
            self.evaluator.vars["ans"] = float(res)
        except ValueError:
            pass 

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateCalculatorGUI(root)
    root.mainloop()
