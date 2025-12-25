import random
import string
import time
import sys
import tkinter as tk
from tkinter import messagebox

# ---------------------------------------------------------
# 1. Passwort generieren
# ---------------------------------------------------------

def passwort_generieren(laenge=12, buchstaben=True, zahlen=True, sonder=True):
    zeichen = ""
    if buchstaben:
        zeichen += string.ascii_letters
    if zahlen:
        zeichen += string.digits
    if sonder:
        zeichen += string.punctuation

    if not zeichen:
        raise ValueError("Keine Zeichenarten ausgewählt!")

    return ''.join(random.choice(zeichen) for _ in range(laenge))


# ---------------------------------------------------------
# 2. Passwort-Stärke analysieren
# ---------------------------------------------------------

def passwort_staerke(pw):
    laenge = len(pw)
    punkte = 0

    if laenge >= 8:
        punkte += 1
    if laenge >= 12:
        punkte += 1
    if any(c.isdigit() for c in pw):
        punkte += 1
    if any(c.isupper() for c in pw):
        punkte += 1
    if any(c in string.punctuation for c in pw):
        punkte += 1

    if punkte <= 2:
        return "schwach"
    elif punkte <= 4:
        return "mittel"
    else:
        return "stark"


# ---------------------------------------------------------
# 3. Mehrere Passwörter generieren
# ---------------------------------------------------------

def mehrere_passwoerter(anzahl, laenge=12, buchstaben=True, zahlen=True, sonder=True):
    return [
        passwort_generieren(laenge, buchstaben, zahlen, sonder)
        for _ in range(anzahl)
    ]


# ---------------------------------------------------------
# 4. Hacker-Effekt
# ---------------------------------------------------------

def hacker_effect(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print()


# ---------------------------------------------------------
# 5. GUI-Version
# ---------------------------------------------------------

def gui_start():
    def generieren():
        try:
            laenge = int(entry_laenge.get())
            pw = passwort_generieren(laenge)
            ausgabe.delete(0, tk.END)
            ausgabe.insert(0, pw)
        except:
            messagebox.showerror("Fehler", "Ungültige Eingabe!")

    fenster = tk.Tk()
    fenster.title("Passwort-Generator")

    tk.Label(fenster, text="Länge:").pack()
    entry_laenge = tk.Entry(fenster)
    entry_laenge.pack()

    tk.Button(fenster, text="Generieren", command=generieren).pack()

    ausgabe = tk.Entry(fenster, width=40)
    ausgabe.pack()

    fenster.mainloop()


# ---------------------------------------------------------
# 6. Terminal-Programm
# ---------------------------------------------------------

def main():
    hacker_effect("Passwort-Generator gestartet...")

    laenge = input("Passwortlänge (Enter für 12): ")
    laenge = int(laenge) if laenge.strip() else 12

    print("Zeichenarten auswählen:")
    b = input("Buchstaben? (j/n): ").lower() == "j"
    z = input("Zahlen? (j/n): ").lower() == "j"
    s = input("Sonderzeichen? (j/n): ").lower() == "j"

    pw = passwort_generieren(laenge, b, z, s)
    staerke = passwort_staerke(pw)

    hacker_effect("Dein Passwort wurde generiert:")
    print(pw)
    print("Stärke:", staerke)

    if input("Mehrere Passwörter generieren? (j/n): ").lower() == "j":
        anzahl = int(input("Wie viele?: "))
        liste = mehrere_passwoerter(anzahl, laenge, b, z, s)
        print("\n".join(liste))

    if input("GUI starten? (j/n): ").lower() == "j":
        gui_start()


# ---------------------------------------------------------
# 7. Startpunkt
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
