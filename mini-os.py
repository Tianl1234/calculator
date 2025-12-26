import tkinter as tk
import json
import os
import requests

# ==========================
# Themes
# ==========================

LIGHT_THEME = {
    "bg_main": "#F5F5F7",
    "fg_display": "#333333",
    "icon_bg": "#E2E8F0",
    "icon_fg": "#1A202C",
    "window_bg": "#FFFFFF",
    "title_bg": "#CBD5E0",
    "title_fg": "#1A202C",
}

DARK_THEME = {
    "bg_main": "#101820",
    "fg_display": "#E2E8F0",
    "icon_bg": "#2D3748",
    "icon_fg": "#E2E8F0",
    "window_bg": "#1F2933",
    "title_bg": "#2D3748",
    "title_fg": "#E2E8F0",
}


# ==========================
# App-Store App
# ==========================

class AppStoreApp:
    def __init__(self, parent, os_reference):
        self.os = os_reference
        t = self.os.theme_data
        self.frame = tk.Frame(parent, bg=t["window_bg"])

        tk.Label(
            self.frame,
            text="MiniOS App‑Store",
            font=("Helvetica", 18, "bold"),
            bg=t["window_bg"],
            fg=t["fg_display"],
        ).pack(pady=10)

        # Apps laden
        try:
            with open("apps.json", "r", encoding="utf-8") as f:
                self.apps = json.load(f)
        except Exception as e:
            tk.Label(
                self.frame,
                text=f"apps.json nicht gefunden oder fehlerhaft:\n{e}",
                bg=t["window_bg"],
                fg="red",
                font=("Helvetica", 11),
            ).pack(pady=20)
            return

        for app in self.apps:
            self.create_app_entry(app)

    def create_app_entry(self, app):
        t = self.os.theme_data
        box = tk.Frame(self.frame, bg=t["window_bg"])
        box.pack(fill="x", padx=20, pady=10)

        tk.Label(
            box,
            text=f"{app.get('icon', '📱')}  {app['name']}",
            font=("Helvetica", 16, "bold"),
            bg=t["window_bg"],
            fg=t["fg_display"],
        ).pack(anchor="w")

        tk.Label(
            box,
            text=app.get("description", ""),
            font=("Helvetica", 11),
            bg=t["window_bg"],
            fg=t["fg_display"],
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(2, 5))

        tk.Button(
            box,
            text="Installieren",
            command=lambda a=app: self.install_app(a),
            bg="#4CAF50",
            fg="white",
            bd=0,
            font=("Helvetica", 11),
            activebackground="#45A049",
            activeforeground="white",
        ).pack(anchor="e", pady=5)

    def install_app(self, app):
        os.makedirs("apps", exist_ok=True)
        safe_name = app["name"].replace(" ", "_")
        filename = f"apps/{safe_name}.py"

        url = app["github_raw"]
        try:
            code = requests.get(url).text
        except Exception as e:
            self.os.show_error(f"Fehler beim Laden von GitHub:\n{e}")
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)

        self.os.register_app(
            name=app["name"],
            icon=app.get("icon", "📱"),
            filepath=filename,
        )
        self.os.show_message(f"{app['name']} wurde installiert!")

    def get_widget(self):
        return self.frame


# ==========================
# MiniOS
# ==========================

class MiniOS:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniOS")
        self.root.geometry("900x600")

        self.theme = "light"
        self.theme_data = LIGHT_THEME

        # installierte Apps (Name -> {icon, file})
        self.installed_apps = {}

        self.desktop = tk.Frame(self.root, bg=self.theme_data["bg_main"])
        self.desktop.pack(fill="both", expand=True)

        self.build_desktop()

    # ------------- Theme -------------

    def set_theme(self, mode):
        self.theme = mode
        self.theme_data = DARK_THEME if mode == "dark" else LIGHT_THEME
        self.apply_theme()

    def apply_theme(self):
        self.desktop.configure(bg=self.theme_data["bg_main"])
        for child in self.desktop.winfo_children():
            child.destroy()
        self.build_desktop()

    # ------------- Desktop -------------

    def build_desktop(self):
        # Feste Icons (z.B. App‑Store, Einstellungen)
        fixed_apps = [
            ("App‑Store", "🛒", self.open_appstore),
            ("Theme Hell", "☀", lambda: self.set_theme("light")),
            ("Theme Dunkel", "🌙", lambda: self.set_theme("dark")),
        ]

        # Feste Apps zuerst
        row = 0
        col = 0
        for name, icon, cb in fixed_apps:
            self.create_icon(name, icon, row, col, cb)
            row += 1

        # Installierte Apps (aus App‑Store)
        for name, data in self.installed_apps.items():
            self.create_icon(
                name,
                data["icon"],
                row,
                0,
                lambda n=name: self.launch_app(
                    self.installed_apps[n]["file"], n
                ),
            )
            row += 1

    def create_icon(self, name, icon, row, col, callback):
        t = self.theme_data
        frame = tk.Frame(self.desktop, bg=t["bg_main"])
        frame.grid(row=row, column=col, padx=40, pady=20)

        btn = tk.Button(
            frame,
            text=icon,
            font=("Helvetica", 38),
            bg=t["icon_bg"],
            fg=t["icon_fg"],
            bd=0,
            command=callback,
            activebackground=t["icon_bg"],
            activeforeground=t["icon_fg"],
            width=3,
            height=1,
        )
        btn.pack()

        tk.Label(
            frame,
            text=name,
            bg=t["bg_main"],
            fg=t["fg_display"],
            font=("Helvetica", 11),
        ).pack(pady=(5, 0))

    # ------------- Fenster -------------

    def open_window(self, title):
        t = self.theme_data
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("450x550")
        win.configure(bg=t["window_bg"])

        titlebar = tk.Frame(win, bg=t["title_bg"], height=40)
        titlebar.pack(fill="x")

        label = tk.Label(
            titlebar,
            text=title,
            bg=t["title_bg"],
            fg=t["title_fg"],
            font=("Helvetica", 12, "bold"),
        )
        label.pack(side="left", padx=10)

        btn_close = tk.Button(
            titlebar,
            text="✖",
            bg=t["title_bg"],
            fg=t["title_fg"],
            bd=0,
            command=win.destroy,
        )
        btn_close.pack(side="right", padx=10)

        def start_move(event):
            win._drag_start_x = event.x
            win._drag_start_y = event.y

        def do_move(event):
            dx = event.x - win._drag_start_x
            dy = event.y - win._drag_start_y
            x = win.winfo_x() + dx
            y = win.winfo_y() + dy
            win.geometry(f"+{x}+{y}")

        titlebar.bind("<Button-1>", start_move)
        titlebar.bind("<B1-Motion>", do_move)

        content = tk.Frame(win, bg=t["window_bg"])
        content.pack(fill="both", expand=True)

        return content

    # ------------- Apps -------------

    def open_appstore(self):
        content = self.open_window("App‑Store")
        app = AppStoreApp(content, self)
        app.get_widget().pack(fill="both", expand=True)

    def register_app(self, name, icon, filepath):
        self.installed_apps[name] = {
            "icon": icon,
            "file": filepath,
        }
        self.apply_theme()  # Desktop neu aufbauen

    def launch_app(self, filepath, title):
        content = self.open_window(title)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            self.show_error(f"App‑Datei nicht lesbar:\n{e}")
            return

        local_env = {"parent": content}
        try:
            exec(code, {}, local_env)
        except Exception as e:
            self.show_error(f"Fehler in App:\n{e}")

    # ------------- Meldungen -------------

    def show_error(self, msg):
        win = tk.Toplevel(self.root)
        win.title("Fehler")
        win.geometry("350x200")
        tk.Label(win, text=msg, fg="red", wraplength=320, justify="left").pack(padx=15, pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)

    def show_message(self, msg):
        win = tk.Toplevel(self.root)
        win.title("Info")
        win.geometry("300x150")
        tk.Label(win, text=msg, wraplength=260, justify="left").pack(padx=15, pady=20)
        tk.Button(win, text="OK", command=win.destroy).pack(pady=10)


def main():
    root = tk.Tk()
    MiniOS(root)
    root.mainloop()


if __name__ == "__main__":
    main()
