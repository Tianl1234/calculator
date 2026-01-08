import random
import string
import time
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# ---------------------------------------------------------
# Globale Konfiguration / Konstanten
# ---------------------------------------------------------

HISTORY_DATEI = "passwort_history.txt"

COMMON_PASSWORDS = {
    "123456", "password", "123456789", "12345", "qwerty",
    "111111", "12345678", "abc123", "123123", "000000",
    "passwort", "hallo123", "iloveyou"
}

PROFILE_CONFIGS = {
    "1": {"name": "Ultra-Sicher", "laenge": 20, "buchstaben": True, "zahlen": True, "sonder": True},
    "2": {"name": "Einfach zu merken", "laenge": 12, "buchstaben": True, "zahlen": True, "sonder": False},
    "3": {"name": "Nur Zahlen", "laenge": 8, "buchstaben": False, "zahlen": True, "sonder": False},
    "4": {"name": "Gaming-Passwort", "laenge": 16, "buchstaben": True, "zahlen": True, "sonder": False},
}


# ---------------------------------------------------------
# 1. Passwort generieren
# ---------------------------------------------------------

def passwort_generieren(laenge=12, buchstaben=True, zahlen=True, sonder=True, custom_zeichen=""):
    zeichen = ""

    if buchstaben:
        zeichen += string.ascii_letters
    if zahlen:
        zeichen += string.digits
    if sonder:
        zeichen += string.punctuation

    if custom_zeichen:
        zeichen += custom_zeichen

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


def staerke_farbe(level):
    if level == "schwach":
        return "red"
    elif level == "mittel":
        return "orange"
    else:
        return "green"


# ---------------------------------------------------------
# 3. Mehrere Passwörter generieren
# ---------------------------------------------------------

def mehrere_passwoerter(anzahl, laenge=12, buchstaben=True, zahlen=True, sonder=True, custom_zeichen=""):
    return [
        passwort_generieren(laenge, buchstaben, zahlen, sonder, custom_zeichen)
        for _ in range(anzahl)
    ]


# ---------------------------------------------------------
# 4. Hacker-Effekt (verbessert)
# ---------------------------------------------------------

def hacker_effect(text):
    """Klassischer Tipp-Effekt für Text."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print()


def hacker_effect_passwort(pw, dauer_pro_char=0.03, loops=8):
    """Zeigt erst zufällige Zeichen, die sich nach und nach in das echte Passwort verwandeln."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    pw_list = list(pw)
    aktuell = [" " for _ in pw_list]

    for _ in range(loops):
        for i in range(len(pw_list)):
            if aktuell[i] != pw_list[i]:
                aktuell[i] = random.choice(alphabet)
        sys.stdout.write("\r" + "".join(aktuell))
        sys.stdout.flush()
        time.sleep(dauer_pro_char)

    sys.stdout.write("\r" + pw + "\n")
    sys.stdout.flush()


# ---------------------------------------------------------
# 5. Passwort-History
# ---------------------------------------------------------

def history_speichern(pw, laenge, buchstaben, zahlen, sonder, custom_zeichen):
    zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    flags = f"Buchstaben={buchstaben}, Zahlen={zahlen}, Sonder={sonder}, Custom='{custom_zeichen}'"
    eintrag = f"[{zeit}] Länge={laenge}, {flags}, Passwort={pw}\n"
    try:
        with open(HISTORY_DATEI, "a", encoding="utf-8") as f:
            f.write(eintrag)
    except Exception as e:
        print("Konnte History nicht speichern:", e)


# ---------------------------------------------------------
# 6. GUI-Version (mit neuen Features)
# ---------------------------------------------------------

def gui_start():
    fenster = tk.Tk()
    fenster.title("Passwort-Generator")
    fenster.geometry("420x340")

    # Dark-Style
    fenster.configure(bg="#1e1e1e")
    style = ttk.Style(fenster)
    try:
        style.theme_use("clam")
    except:
        pass
    style.configure("TLabel", background="#1e1e1e", foreground="white")
    style.configure("TButton", background="#333333", foreground="white")
    style.configure("TCheckbutton", background="#1e1e1e", foreground="white")

    # Variablen
    var_laenge = tk.IntVar(value=12)
    var_buchstaben = tk.BooleanVar(value=True)
    var_zahlen = tk.BooleanVar(value=True)
    var_sonder = tk.BooleanVar(value=True)
    var_custom = tk.StringVar()
    var_staerke = tk.StringVar(value="Stärke: -")

    # Funktionen im GUI
    def aktualisiere_staerke_preview():
        try:
            laenge = var_laenge.get()
            # Dummy-Passwort für Stärke-Vorschau
            dummy = "A" * max(1, laenge)
            level = passwort_staerke(dummy)
            var_staerke.set(f"Stärke (ca.): {level}")
            label_staerke.config(fg=staerke_farbe(level))
        except Exception:
            var_staerke.set("Stärke: -")
            label_staerke.config(fg="white")

    def generieren():
        try:
            laenge = var_laenge.get()
            custom_zeichen = var_custom.get()
            pw = passwort_generieren(
                laenge,
                var_buchstaben.get(),
                var_zahlen.get(),
                var_sonder.get(),
                custom_zeichen
            )
            ausgabe.delete(0, tk.END)
            ausgabe.insert(0, pw)

            level = passwort_staerke(pw)
            var_staerke.set(f"Stärke: {level}")
            label_staerke.config(fg=staerke_farbe(level))

            # History speichern
            history_speichern(
                pw, laenge,
                var_buchstaben.get(),
                var_zahlen.get(),
                var_sonder.get(),
                custom_zeichen
            )

            # Leak-Warnung
            if pw in COMMON_PASSWORDS:
                messagebox.showwarning("Warnung", "Dieses Passwort ist sehr häufig und unsicher!")

        except Exception as e:
            messagebox.showerror("Fehler", f"Ungültige Eingabe!\n{e}")

    def in_zwischenablage():
        pw = ausgabe.get()
        if not pw:
            messagebox.showinfo("Info", "Kein Passwort zum Kopieren vorhanden.")
            return
        fenster.clipboard_clear()
        fenster.clipboard_append(pw)
        fenster.update()
        messagebox.showinfo("Kopiert", "Passwort wurde in die Zwischenablage kopiert.")

    def profil_auswaehlen(event=None):
        profil_name = combo_profile.get()
        for key, cfg in PROFILE_CONFIGS.items():
            if cfg["name"] == profil_name:
                var_laenge.set(cfg["laenge"])
                var_buchstaben.set(cfg["buchstaben"])
                var_zahlen.set(cfg["zahlen"])
                var_sonder.set(cfg["sonder"])
                aktualisiere_staerke_preview()
                break

    # Widgets
    ttk.Label(fenster, text="Profil:").pack(pady=(10, 0))
    combo_profile = ttk.Combobox(
        fenster,
        values=[cfg["name"] for cfg in PROFILE_CONFIGS.values()],
        state="readonly"
    )
    combo_profile.pack()
    combo_profile.bind("<<ComboboxSelected>>", profil_auswaehlen)

    ttk.Label(fenster, text="Länge:").pack(pady=(10, 0))
    spin_laenge = tk.Spinbox(
        fenster, from_=4, to=64,
        textvariable=var_laenge,
        command=aktualisiere_staerke_preview,
        bg="#2b2b2b", fg="white", insertbackground="white"
    )
    spin_laenge.pack()

    frame_checks = tk.Frame(fenster, bg="#1e1e1e")
    frame_checks.pack(pady=5)

    tk.Checkbutton(frame_checks, text="Buchstaben", variable=var_buchstaben, bg="#1e1e1e", fg="white",
                   activebackground="#1e1e1e", activeforeground="white",
                   command=aktualisiere_staerke_preview).grid(row=0, column=0, padx=5)
    tk.Checkbutton(frame_checks, text="Zahlen", variable=var_zahlen, bg="#1e1e1e", fg="white",
                   activebackground="#1e1e1e", activeforeground="white",
                   command=aktualisiere_staerke_preview).grid(row=0, column=1, padx=5)
    tk.Checkbutton(frame_checks, text="Sonderzeichen", variable=var_sonder, bg="#1e1e1e", fg="white",
                   activebackground="#1e1e1e", activeforeground="white",
                   command=aktualisiere_staerke_preview).grid(row=0, column=2, padx=5)

    ttk.Label(fenster, text="Eigene Zeichen (optional):").pack(pady=(5, 0))
    entry_custom = tk.Entry(fenster, textvariable=var_custom, bg="#2b2b2b", fg="white", insertbackground="white")
    entry_custom.pack()

    label_staerke = tk.Label(fenster, textvariable=var_staerke, bg="#1e1e1e", fg="white")
    label_staerke.pack(pady=5)

    btn_generieren = tk.Button(fenster, text="Generieren", command=generieren, bg="#3c3c3c", fg="white")
    btn_generieren.pack(pady=5)

    ausgabe = tk.Entry(fenster, width=40, bg="#2b2b2b", fg="white", insertbackground="white")
    ausgabe.pack(pady=(5, 0))

    btn_clipboard = tk.Button(fenster, text="In Zwischenablage kopieren", command=in_zwischenablage,
                              bg="#3c3c3c", fg="white")
    btn_clipboard.pack(pady=5)

    aktualisiere_staerke_preview()

    fenster.mainloop()


# ---------------------------------------------------------
# 7. Terminal-Programm (mit Profilen, Export, Custom-Zeichen)
# ---------------------------------------------------------

def profile_auswaehlen():
    print("\nProfile:")
    for key, cfg in PROFILE_CONFIGS.items():
        print(f"{key}: {cfg['name']} (Länge={cfg['laenge']}, Buchstaben={cfg['buchstaben']}, "
              f"Zahlen={cfg['zahlen']}, Sonder={cfg['sonder']})")
    print("0: Kein Profil (manuelle Auswahl)")

    wahl = input("Profil wählen (Nummer, Enter für 0): ").strip()
    if wahl in PROFILE_CONFIGS:
        cfg = PROFILE_CONFIGS[wahl]
        print(f"Profil '{cfg['name']}' ausgewählt.\n")
        return cfg["laenge"], cfg["buchstaben"], cfg["zahlen"], cfg["sonder"]
    else:
        print("Kein Profil oder ungültige Eingabe, manuelle Auswahl.\n")
        return None, None, None, None


def main():
    hacker_effect("Passwort-Generator gestartet...")

    # Profil-Auswahl
    laenge, b, z, s = profile_auswaehlen()

    # Manuelle Eingabe, falls kein Profil
    if laenge is None:
        laenge_eingabe = input("Passwortlänge (Enter für 12): ")
        laenge = int(laenge_eingabe) if laenge_eingabe.strip() else 12

        print("Zeichenarten auswählen:")
        b = input("Buchstaben? (j/n): ").lower() == "j"
        z = input("Zahlen? (j/n): ").lower() == "j"
        s = input("Sonderzeichen? (j/n): ").lower() == "j"

    custom_zeichen = input("Eigene Zeichen hinzufügen (oder Enter für keine): ")

    pw = passwort_generieren(laenge, b, z, s, custom_zeichen)
    staerke = passwort_staerke(pw)

    hacker_effect("Dein Passwort wurde generiert:")
    hacker_effect_passwort(pw)

    print("Stärke:", staerke)

    # Leak-Warnung
    if pw in COMMON_PASSWORDS:
        print("WARNUNG: Dieses Passwort ist eines der häufigsten und sehr unsicher!")

    # History speichern
    history_speichern(pw, laenge, b, z, s, custom_zeichen)

    if input("Mehrere Passwörter generieren? (j/n): ").lower() == "j":
        anzahl = int(input("Wie viele?: "))
        liste = mehrere_passwoerter(anzahl, laenge, b, z, s, custom_zeichen)
        print("\nGenerierte Passwörter:")
        print("\n".join(liste))

        # Export als TXT
        if input("Als Datei speichern? (j/n): ").lower() == "j":
            dateiname = input("Dateiname (Enter für 'passwoerter.txt'): ").strip()
            if not dateiname:
                dateiname = "passwoerter.txt"
            try:
                with open(dateiname, "w", encoding="utf-8") as f:
                    for pw_item in liste:
                        f.write(pw_item + "\n")
                print(f"Passwörter in '{dateiname}' gespeichert.")
            except Exception as e:
                print("Fehler beim Speichern:", e)

    if input("GUI starten? (j/n): ").lower() == "j":
        gui_start()


# ---------------------------------------------------------
# 8. Startpunkt
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
