while (i := input("Rechnung (oder Enter zum Beenden): ")).strip():
    try:
        print(eval(i))
    except Exception:
        print("ungültig")
