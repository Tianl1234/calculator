while (i := input("Rechnung(oder Enter zum Beenden):")): print(eval(i) if i[0].isdigit() or i[0] in "(-"else "ungültig")
