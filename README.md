# 🧮 Scientific Pro Calculator

A secure, local, and modern scientific calculator with a graphical user interface (GUI), written in Python. 

This tool deliberately avoids the insecure Python `eval()` function. Instead, it utilizes the Abstract Syntax Tree (`ast`) to parse and evaluate mathematical expressions with absolute security and precision.

## ✨ Features

* **Maximum Security:** Uses Python's `ast.parse` for expression evaluation. Execution of malicious code is strictly impossible.
* **Scientific Functions:** Supports advanced mathematical operations such as `sin()`, `cos()`, `tan()`, `sqrt()`, and exponentiation (`^`).
* **Mathematical Constants:** Built-in support for `pi` and `e`.
* **Smart Memory (`ans`):** Automatically stores the last valid result, allowing you to seamlessly continue your calculations.
* **Floating-Point Correction:** Smooths out typical floating-point inaccuracies (e.g., `sin(pi)` correctly evaluates to `0` instead of `1.22e-16`).
* **Modern UI:** Sleek and highly focused Dark Mode design built with `tkinter`.

## 🛠️ Installation

This project has **no external dependencies**. All you need is a standard Python installation!
