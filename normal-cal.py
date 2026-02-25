import ast, operator, math, re, sqlite3, datetime, json, os, zipfile, shutil
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, getcontext
from fractions import Fraction

# ============================================================
# I. SICHERHEIT & MATHEMATIK (Der AST-Kern)
# ============================================================
class SafeEvaluator:
    def __init__(self, last_result=None):
        self.ops = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.USub: operator.neg
        }
        self.vars = {"pi": math.pi, "e": math.e, "ans": last_result if last_result else 0}

    def evaluate(self, expr):
        try:
            expr = expr.replace("€", "").replace("%", "/100")
            tree = ast.parse(expr, mode="eval")
            return self._eval_node(tree.body)
        except Exception as e:
            return str(e)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name): return self.vars.get(node.id, 0)
        if isinstance(node, ast.BinOp):
            return self.ops[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            return self.ops[type(node.op)](self._eval_node(node.operand))
        raise ValueError("Operation nicht erlaubt")

# ============================================================
# II. DATENBANK & GEDÄCHTNIS
# ============================================================
class AIDatabase:
    def __init__(self, db_name="ultimate_memory.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self._setup()

    def _setup(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS history (ts TEXT, user TEXT, ai TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS facts (key TEXT PRIMARY KEY, val TEXT)")
        self.conn.commit()

    def save_interaction(self, u, a):
        self.conn.cursor().execute("INSERT INTO history VALUES (?,?,?)", (datetime.datetime.now().isoformat(), u, a))
        self.conn.commit()

# ============================================================
# III. KI-LOGIK & ANALYSE
# ============================================================
class SmartAI:
    def __init__(self, db):
        self.db = db
        self.inflation = 2.8
        self.market_return = 7.0

    def think(self, query):
        query = query.lower().replace(",", ".")
        nums = [float(n) for n in re.findall(r"(\d+(?:\.\d+)?)", query)]
        
        # Identifikation von Kapital, Zins, Zeit
        k = next((n for n in nums if n > 100), None)
        p = next((n for n in nums if 0.1 <= n <= 25), 3.5)
        n = next((n for n in nums if 1 <= n <= 50 and n != p), 1.0)

        if not k: return "🤖 Ich erkenne Zahlen, aber kein Kapital. Wie viel € möchtest du berechnen?"

        res = k * (1 + (p/100))**n
        advice = "⚠️ Realverlust durch Inflation!" if p < self.inflation else "✅ Rendite über Inflation."
        
        report = (f"🧠 KI-Analyse:\nBetrag: {k:,.2f}€\nZins: {p}%\nZeit: {n} J.\n"
                  f"Ergebnis: {res:,.2f}€\n{advice}")
        
        self.db.save_interaction(query, report)
        return report

# ============================================================
# IV. HIGH-END GUI (OneUI Style)
# ============================================================
class UltimateCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Finance Station Pro")
        self.root.geometry("420x700")
        self.root.configure(bg="#121212")

        self.db = AIDatabase()
        self.evaluator = SafeEvaluator()
        self.ai = SmartAI(self.db)

        self._build_ui()

    def _build_ui(self):
        # Header
        header = tk.Label(self.root, text="🤖 AI FINANCIAL TERMINAL", bg="#121212", fg="#2196F3", font=("Helvetica", 10, "bold"))
        header.pack(pady=(15, 0))

        # KI-Eingabe (Chat-Stil)
        self.ai_entry = tk.Entry(self.root, font=("Helvetica", 14), bg="#1E1E1E", fg="white", bd=0, insertbackground="white")
        self.ai_entry.pack(fill="x", padx=25, pady=15, ipady=12)
        self.ai_entry.insert(0, "Frag die KI...")

        # Display (Große Zahlen)
        self.display = tk.Entry(self.root, font=("Helvetica", 36), bg="#121212", fg="white", bd=0, justify="right")
        self.display.pack(fill="x", padx=25, pady=10)

        # Plotter (Canvas)
        self.canvas = tk.Canvas(self.root, bg="#1E1E1E", height=120, highlightthickness=0)
        self.canvas.pack(fill="x", padx=25, pady=10)

        # Button-Grid
        btn_frame = tk.Frame(self.root, bg="#121212")
        btn_frame.pack(fill="both", expand=True, padx=20)

        buttons = [
            ('C', 0, 0, "#FF5252"), ('←', 0, 1, "#424242"), ('ans', 0, 2, "#424242"), ('/', 0, 3, "#FF9800"),
            ('7', 1, 0, "#2C2C2C"), ('8', 1, 1, "#2C2C2C"), ('9', 1, 2, "#2C2C2C"), ('*', 1, 3, "#FF9800"),
            ('4', 2, 0, "#2C2C2C"), ('5', 2, 1, "#2C2C2C"), ('6', 2, 2, "#2C2C2C"), ('-', 2, 3, "#FF9800"),
            ('1', 3, 0, "#2C2C2C"), ('2', 3, 1, "#2C2C2C"), ('3', 3, 2, "#2C2C2C"), ('+', 3, 3, "#FF9800"),
            ('0', 4, 0, "#2C2C2C"), ('.', 4, 1, "#2C2C2C"), ('=', 4, 2, "#4CAF50")
        ]

        for (txt, r, c, clr) in buttons:
            btn = tk.Button(btn_frame, text=txt, font=("Helvetica", 12, "bold"), bg=clr, fg="white", bd=0, 
                            command=lambda t=txt: self._on_btn(t))
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            if txt == '=': btn.grid(columnspan=2)

        for i in range(4): btn_frame.columnconfigure(i, weight=1)
        for i in range(5): btn_frame.rowconfigure(i, weight=1)

        # Footer Buttons
        footer = tk.Frame(self.root, bg="#121212")
        footer.pack(fill="x", pady=10)
        tk.Button(footer, text="Backup", bg="#333", fg="gray", bd=0, command=self._backup).pack(side="left", padx=25)
        tk.Button(footer, text="KI Analyse", bg="#2196F3", fg="white", bd=0, command=self._run_ai, padx=10).pack(side="right", padx=25)

    def _on_btn(self, char):
        if char == 'C': self.display.delete(0, tk.END)
        elif char == '←': self.display.delete(len(self.display.get())-1)
        elif char == '=': self._calc()
        else: self.display.insert(tk.END, char)

    def _calc(self):
        res = self.evaluator.evaluate(self.display.get())
        self.display.delete(0, tk.END)
        self.display.insert(0, str(res))

    def _run_ai(self):
        q = self.ai_entry.get()
        ans = self.ai.think(q)
        messagebox.showinfo("AI Analysis", ans)
        self._plot_ai_data(q)

    def _plot_ai_data(self, q):
        # Einfache Plot-Logik für Zinsen
        self.canvas.delete("all")
        self.canvas.create_line(10, 110, 350, 110, fill="gray") # X-Achse
        nums = [float(n) for n in re.findall(r"(\d+(?:\.\d+)?)", q)]
        if len(nums) >= 2:
            k = nums[0]
            p = nums[1] if len(nums)>1 else 3.5
            pts = []
            for x in range(20):
                y = 110 - (k * (1 + p/100)**x / (k*2) * 100)
                pts.append((10 + x*18, y))
            self.canvas.create_line(pts, fill="#4CAF50", width=2, smooth=True)

    def _backup(self):
        b = self.db.db_name
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(b, f"backup_{ts}.db")
        messagebox.showinfo("Backup", "Lokale Datenbank gesichert!")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateCalculatorGUI(root)
    root.mainloop()
