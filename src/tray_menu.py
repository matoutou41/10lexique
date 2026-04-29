"""
Menu contextuel custom (CustomTkinter) qui s'affiche à la position du curseur
quand on clique sur l'icône du tray. Remplace le menu Windows natif par un
menu sombre arrondi cohérent avec le reste de l'app.
"""
import tkinter as tk
import customtkinter as ctk

import theme


class TrayMenu:
    """
    Menu flottant style LocalSend.
    Une seule instance partagée. On l'affiche via show_at(x, y, items).
    """

    def __init__(self, root):
        self.root = root
        self.win = None
        self._build()

    def _build(self):
        self.win = ctk.CTkToplevel(self.root)
        self.win.withdraw()
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(fg_color=theme.BG_DARK)
        self.win.bind("<FocusOut>", lambda e: self.hide())
        self.win.bind("<Escape>", lambda e: self.hide())

        # Container arrondi avec bordure subtile
        self.frame = ctk.CTkFrame(
            self.win,
            fg_color=theme.BG_SIDEBAR,
            corner_radius=theme.RADIUS_MD,
            border_width=1,
            border_color=theme.BORDER,
        )
        self.frame.pack(fill="both", expand=True, padx=2, pady=2)

    # ---------- API publique ----------

    def show_at(self, x: int, y: int, items: list):
        """
        items = liste de tuples : (label, callback) ou ("---", None) pour séparateur,
                ou ("title", label, None) pour un titre désactivé en haut.
        Affiche le menu près de (x, y) en clampant aux bords de l'écran.
        """
        # Vide le contenu précédent
        for child in self.frame.winfo_children():
            child.destroy()

        for entry in items:
            if entry[0] == "---":
                sep = ctk.CTkFrame(
                    self.frame, fg_color=theme.BORDER, height=1, corner_radius=0
                )
                sep.pack(fill="x", padx=10, pady=4)
            elif entry[0] == "title":
                ctk.CTkLabel(
                    self.frame,
                    text=entry[1],
                    font=theme.font(theme.FONT_SIZE_SMALL, "bold"),
                    text_color=theme.TEXT_MUTED,
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(8, 4))
            else:
                label, callback = entry
                self._make_item(label, callback).pack(fill="x", padx=4, pady=1)

        # Affiche
        self.win.update_idletasks()
        w = max(self.win.winfo_reqwidth(), 220)
        h = self.win.winfo_reqheight()

        try:
            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()
        except Exception:
            sw, sh = 1920, 1080

        # Clamp
        margin = 8
        # Le menu apparait au-dessus du clic (typique pour un tray en bas d'écran)
        px = max(margin, min(x - w // 2, sw - w - margin))
        py = y - h - 12
        if py < margin:
            py = y + 20  # bascule en dessous si pas la place

        self.win.geometry(f"{w}x{h}+{px}+{py}")
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

    def hide(self):
        try:
            self.win.withdraw()
        except Exception:
            pass

    # ---------- Helpers ----------

    def _make_item(self, label: str, callback):
        def _click():
            self.hide()
            if callback:
                # Léger délai pour que la fenêtre se cache avant l'action
                self.root.after(50, callback)

        btn = ctk.CTkButton(
            self.frame,
            text=label,
            command=_click,
            anchor="w",
            height=34,
            corner_radius=theme.RADIUS_SM,
            fg_color="transparent",
            hover_color=theme.BG_HOVER,
            text_color=theme.TEXT_PRIMARY,
            font=theme.font(theme.FONT_SIZE_BODY),
        )
        return btn
