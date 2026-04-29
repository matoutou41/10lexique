"""
Popup flottante style LocalSend.
- Sidebar gauche avec 3 onglets : Corriger / Traduire / Améliorer
- Zone principale : original (lecture seule) + résultat (modifiable)
- Boutons : Appliquer / Copier
- Se ferme automatiquement quand on clique en dehors
- Se positionne à côté du curseur sans recouvrir la zone d'édition
"""
import threading
import time
import tkinter as tk
import customtkinter as ctk

import pyperclip

from text_handler import replace_selection
import theme
import labels as lbl


# Mode global CustomTkinter — light pour s'accorder à la palette violet/cream
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")  # on override avec nos couleurs


# Onglets disponibles
TAB_CORRECT = "correct"
TAB_TRANSLATE = "translate"
TAB_IMPROVE = "improve"


class CorrectorPopup:
    """
    Popup unique persistante. Cachée par défaut.
    show_for_action(action, text, old_clipboard) lance le flux.
    """

    def __init__(self, root: ctk.CTk, claude_client_provider, config_provider):
        """
        claude_client_provider : callable -> ClaudeClient (peut renvoyer None si pas configuré)
        config_provider : callable -> dict de config courante
        """
        self.root = root
        self._get_client = claude_client_provider
        self._get_config = config_provider

        self._current_action = TAB_CORRECT
        self._original = ""
        self._old_clipboard = ""
        self._result = ""
        self._busy = False

        # Toplevel sans bordure (look flottant)
        self.win = ctk.CTkToplevel(root)
        self.win.withdraw()
        self.win.overrideredirect(True)  # supprime barre titre Windows
        self.win.attributes("-topmost", True)
        self.win.configure(fg_color=theme.BG_DARK)

        # Fermeture sur perte de focus / clic extérieur
        self.win.bind("<FocusOut>", self._on_focus_out)
        self.win.bind("<Escape>", lambda e: self.hide())
        # Entrée applique (sauf quand on édite la zone de texte)
        self.win.bind("<Return>", self._on_enter_key)

        # Taille raisonnable
        self.WIN_W = 720
        self.WIN_H = 420

        self._build_ui()

    # ---------- UI ----------

    def _build_ui(self):
        # Container racine arrondi
        outer = ctk.CTkFrame(
            self.win,
            fg_color=theme.BG_DARK,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.BORDER,
        )
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        # Layout : sidebar | content
        outer.grid_columnconfigure(1, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        # === SIDEBAR ===
        sidebar = ctk.CTkFrame(
            outer,
            fg_color=theme.BG_SIDEBAR,
            corner_radius=theme.RADIUS_LG,
            width=180,
        )
        sidebar.grid(row=0, column=0, sticky="nswe", padx=(6, 0), pady=6)
        sidebar.grid_propagate(False)

        # Titre app — "10lex" (matche la landing)
        title = ctk.CTkLabel(
            sidebar,
            text="10lex.",
            font=theme.font_display(28, "bold"),
            text_color=theme.TEXT_ON_DARK,
            anchor="w",
            justify="left",
        )
        title.pack(fill="x", padx=18, pady=(22, 6))

        subtitle = ctk.CTkLabel(
            sidebar,
            text="la correction\npour les nuls",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_ON_DARK_MUTED,
            anchor="w",
            justify="left",
        )
        subtitle.pack(fill="x", padx=18, pady=(0, 22))

        # Onglets
        self._tab_buttons = {}
        for key, label, icon in [
            (TAB_CORRECT, "Corriger", "✓"),
            (TAB_TRANSLATE, "Traduire", "🌐"),
            (TAB_IMPROVE, "Améliorer", "✨"),
        ]:
            btn = self._make_tab_button(sidebar, key, label, icon)
            btn.pack(fill="x", padx=10, pady=3)
            self._tab_buttons[key] = btn

        # Footer sidebar : raccourci affiché
        footer = ctk.CTkLabel(
            sidebar,
            text="",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_ON_DARK_MUTED,
            anchor="w",
            justify="left",
        )
        footer.pack(side="bottom", fill="x", padx=18, pady=14)
        self._footer_label = footer

        # === CONTENT ===
        content = ctk.CTkFrame(outer, fg_color=theme.BG_DARK, corner_radius=0)
        content.grid(row=0, column=1, sticky="nswe", padx=(8, 6), pady=6)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        # Header : titre de l'action + statut
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(8, 6))
        header.grid_columnconfigure(0, weight=1)

        self._action_title = ctk.CTkLabel(
            header,
            text="Correction",
            font=theme.font_display(theme.FONT_SIZE_TITLE, "bold"),
            text_color=theme.TEXT_ON_DARK,
            anchor="w",
        )
        self._action_title.grid(row=0, column=0, sticky="w")

        self._status = ctk.CTkLabel(
            header,
            text="",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_ON_DARK_MUTED,
            anchor="e",
        )
        self._status.grid(row=0, column=1, sticky="e")

        # Sous-titre dynamique (langue cible / ton)
        self._action_subtitle = ctk.CTkLabel(
            content,
            text="",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_ON_DARK_MUTED,
            anchor="w",
        )
        self._action_subtitle.grid(row=1, column=0, sticky="w", padx=4)

        # Zone de texte original (compact, lecture seule)
        original_frame = ctk.CTkFrame(
            content,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_MD,
            border_width=1,
            border_color=theme.BORDER,
            height=80,
        )
        # On utilise pack à l'intérieur, donc on met dans une row à part
        # mais on doit grid sur content :
        original_frame.grid(row=2, column=0, sticky="ew", pady=(8, 6), padx=4)
        original_frame.grid_propagate(False)

        ctk.CTkLabel(
            original_frame,
            text="Original",
            font=theme.font(theme.FONT_SIZE_SMALL, "bold"),
            text_color=theme.TEXT_SECONDARY,
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))

        self._original_box = ctk.CTkTextbox(
            original_frame,
            fg_color=theme.BG_CARD,
            text_color=theme.TEXT_SECONDARY,
            border_width=0,
            font=theme.font(theme.FONT_SIZE_BODY),
            wrap="word",
            height=50,
        )
        self._original_box.pack(fill="both", expand=True, padx=8, pady=(2, 6))

        # On change la grille pour donner de l'espace au résultat
        content.grid_rowconfigure(2, weight=0)
        content.grid_rowconfigure(3, weight=1)

        # Zone de résultat (modifiable, plus grande)
        result_frame = ctk.CTkFrame(
            content,
            fg_color=theme.BG_CARD,
            corner_radius=theme.RADIUS_MD,
            border_width=1,
            border_color=theme.BORDER,
        )
        result_frame.grid(row=3, column=0, sticky="nswe", pady=(0, 8), padx=4)

        result_header = ctk.CTkFrame(result_frame, fg_color="transparent")
        result_header.pack(fill="x", padx=10, pady=(6, 0))

        self._result_label = ctk.CTkLabel(
            result_header,
            text="Résultat",
            font=theme.font(theme.FONT_SIZE_SMALL, "bold"),
            text_color=theme.ACCENT,
            anchor="w",
        )
        self._RESULT_DEFAULT_COLOR = theme.ACCENT
        self._result_label.pack(side="left")

        ctk.CTkLabel(
            result_header,
            text="modifiable",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_MUTED,
        ).pack(side="right", padx=(0, 4))

        self._result_box = ctk.CTkTextbox(
            result_frame,
            fg_color=theme.BG_CARD,
            text_color=theme.TEXT_PRIMARY,
            border_width=0,
            font=theme.font(theme.FONT_SIZE_BODY),
            wrap="word",
        )
        self._result_box.pack(fill="both", expand=True, padx=8, pady=(2, 8))

        # Footer : boutons
        footer = ctk.CTkFrame(content, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=4, pady=(0, 6))

        self._copy_btn = ctk.CTkButton(
            footer,
            text="Copier",
            command=self._on_copy,
            width=90,
            height=38,
            corner_radius=999,
            fg_color=theme.BG_CARD,
            hover_color=theme.BG_HOVER,
            text_color=theme.TEXT_PRIMARY,
            border_width=2,
            border_color=theme.BORDER,
            font=theme.font(theme.FONT_SIZE_BODY, "bold"),
        )
        self._copy_btn.pack(side="right", padx=(6, 0))

        self._apply_btn = ctk.CTkButton(
            footer,
            text="Appliquer",
            command=self._on_apply,
            width=130,
            height=38,
            corner_radius=999,
            fg_color=theme.ACCENT,
            hover_color=theme.ACCENT_HOVER,
            text_color=theme.ACCENT_TEXT,
            font=theme.font(theme.FONT_SIZE_BODY, "bold"),
        )
        self._apply_btn.pack(side="right", padx=(6, 0))

        # Hint texte gauche
        self._hint = ctk.CTkLabel(
            footer,
            text="Entrée : appliquer  ·  Échap : fermer",
            font=theme.font(theme.FONT_SIZE_SMALL),
            text_color=theme.TEXT_ON_DARK_MUTED,
        )
        self._hint.pack(side="left")

    def _make_tab_button(self, parent, key, label, icon):
        btn = ctk.CTkButton(
            parent,
            text=f"  {icon}   {label}",
            anchor="w",
            command=lambda k=key: self._switch_tab(k),
            height=42,
            corner_radius=999,
            fg_color="transparent",
            hover_color=theme.ACCENT,
            text_color=theme.TEXT_ON_DARK,
            font=theme.font(theme.FONT_SIZE_BODY, "bold"),
        )
        return btn

    def _refresh_tab_styles(self):
        for key, btn in self._tab_buttons.items():
            if key == self._current_action:
                btn.configure(
                    fg_color=theme.BG_CARD,
                    text_color=theme.TEXT_PRIMARY,
                    hover_color=theme.BG_HOVER,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.TEXT_ON_DARK,
                    hover_color=theme.ACCENT,
                )

    # ---------- API publique (thread-safe) ----------

    def show_for_action(self, action: str, original: str, old_clipboard: str = ""):
        """Lance le flux : affiche la popup + appelle Claude pour `action`."""
        self.root.after(0, lambda: self._show_for_action_ui(action, original, old_clipboard))

    def hide(self):
        self.root.after(0, self._hide_ui)

    # ---------- Implémentation Tk ----------

    def _show_for_action_ui(self, action: str, original: str, old_clipboard: str):
        self._current_action = action
        self._original = original
        self._old_clipboard = old_clipboard
        self._refresh_tab_styles()
        self._update_action_header(action)

        # Affiche original
        self._original_box.configure(state="normal")
        self._original_box.delete("1.0", "end")
        self._original_box.insert("1.0", original)
        self._original_box.configure(state="disabled")

        # État de chargement
        self._set_loading()

        # Position + affichage
        self._position_window()
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()
        # Force focus sur la fenêtre pour activer le binding FocusOut
        self.win.after(50, lambda: self.win.focus_force())

        # Lance l'appel API
        threading.Thread(target=self._run_action, daemon=True).start()

    def _update_action_header(self, action: str):
        cfg = self._get_config()
        if action == TAB_CORRECT:
            self._action_title.configure(text="Correction")
            self._action_subtitle.configure(text="Orthographe et grammaire")
            self._apply_btn.configure(text="Appliquer")
        elif action == TAB_TRANSLATE:
            target_key = cfg.get("translate_target_lang", "english")
            target_label = lbl.key_to_label(lbl.LANG_LABELS, target_key)
            self._action_title.configure(text="Traduction")
            self._action_subtitle.configure(text=f"Vers {target_label.lower()}")
            self._apply_btn.configure(text="Remplacer")
        elif action == TAB_IMPROVE:
            tone_key = cfg.get("rephrase_tone", "neutral")
            self._action_title.configure(text="Amélioration")
            self._action_subtitle.configure(text=lbl.TONE_DESCRIPTIONS.get(tone_key, tone_key))
            self._apply_btn.configure(text="Remplacer")

        # Footer raccourci
        hk = cfg.get("hotkey_correct", "alt+k")
        self._footer_label.configure(text=f"Raccourci : {hk.upper()}")

    def _set_loading(self):
        self._busy = True
        self._status.configure(text="Génération en cours…", text_color=theme.TEXT_SECONDARY)
        self._result_box.configure(state="normal")
        self._result_box.delete("1.0", "end")
        self._result_box.insert("1.0", "")
        self._apply_btn.configure(state="disabled")
        self._copy_btn.configure(state="disabled")

    def _set_result(self, text: str):
        self._busy = False
        self._result = text
        self._result_box.configure(state="normal")
        self._result_box.delete("1.0", "end")
        self._result_box.insert("1.0", text)
        self._status.configure(text="✓ Prêt — Entrée pour appliquer", text_color=theme.ACCENT)
        self._apply_btn.configure(state="normal")
        self._copy_btn.configure(state="normal")
        # Focus sur le bouton Appliquer pour qu'Entrée l'active directement
        self._apply_btn.focus_set()

    def _set_error(self, msg: str):
        self._busy = False
        self._result_box.configure(state="normal")
        self._result_box.delete("1.0", "end")
        self._result_box.insert("1.0", f"Erreur : {msg}")
        self._status.configure(text="⚠ Erreur", text_color=theme.DANGER)
        self._apply_btn.configure(state="disabled")
        self._copy_btn.configure(state="disabled")

    def _hide_ui(self):
        self.win.withdraw()

    # ---------- Position intelligente ----------

    def _position_window(self):
        """
        Positionne la fenêtre de manière à NE PAS recouvrir la zone d'édition :
        - On essaie de la placer sous le curseur souris
        - Si pas de place en bas, on la met au-dessus
        - On clamp aux bords de l'écran
        """
        self.win.update_idletasks()
        try:
            x_root = self.win.winfo_pointerx()
            y_root = self.win.winfo_pointery()
            sw = self.win.winfo_screenwidth()
            sh = self.win.winfo_screenheight()
        except Exception:
            x_root, y_root, sw, sh = 200, 200, 1920, 1080

        margin = 20
        w, h = self.WIN_W, self.WIN_H

        # Position horizontale : centrée sur le curseur, décalée de w/2
        x = x_root - w // 2
        x = max(margin, min(x, sw - w - margin))

        # Position verticale : sous le curseur si possible, sinon au-dessus
        if y_root + h + 30 < sh - margin:
            y = y_root + 30  # sous le curseur
        elif y_root - h - 20 > margin:
            y = y_root - h - 20  # au-dessus
        else:
            y = max(margin, (sh - h) // 2)  # centré en dernier recours

        self.win.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- Switch d'onglet (re-déclenche l'action) ----------

    def _switch_tab(self, action: str):
        if self._busy:
            return
        if action == self._current_action and self._result:
            return  # rien à faire
        self._current_action = action
        self._refresh_tab_styles()
        self._update_action_header(action)
        self._set_loading()
        threading.Thread(target=self._run_action, daemon=True).start()

    # ---------- Appel à Claude (thread API) ----------

    def _run_action(self):
        client = self._get_client()
        if client is None:
            self.root.after(0, lambda: self._set_error("Clé API non configurée."))
            return

        cfg = self._get_config()
        text = self._original

        try:
            if self._current_action == TAB_CORRECT:
                result = client.correct(text)
            elif self._current_action == TAB_TRANSLATE:
                target = cfg.get("translate_target_lang", "english")
                result = client.translate(text, target)
            elif self._current_action == TAB_IMPROVE:
                tone = cfg.get("rephrase_tone", "neutral")
                result = client.rephrase(text, tone)
            else:
                result = text
            result = result if result else text
            # Sécurité : si l'action a changé entre temps, on n'écrase pas
            self.root.after(0, lambda r=result: self._set_result(r))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self._set_error(m))

    # ---------- Actions boutons ----------

    def _current_result(self) -> str:
        return self._result_box.get("1.0", "end-1c")

    def _on_enter_key(self, event):
        """
        Entrée générale dans la fenêtre :
        - Si on est dans la zone de texte du résultat → saut de ligne normal
        - Sinon → applique (clic sur Appliquer)
        """
        if self._busy:
            return "break"
        focused = self.win.focus_get()
        # Si l'utilisateur édite le texte du résultat, on laisse Entrée insérer un saut de ligne
        try:
            # Le widget interne du CTkTextbox est un tk.Text
            inner = getattr(self._result_box, "_textbox", None)
            if focused is inner:
                return  # comportement par défaut
        except Exception:
            pass
        # Sinon : applique
        if str(self._apply_btn.cget("state")) == "normal":
            self._on_apply()
        return "break"

    def _on_apply(self):
        text = self._current_result()
        if not text:
            return
        old_clip = self._old_clipboard
        self.win.withdraw()

        def paste_after_focus():
            time.sleep(0.3)  # laisse Windows redonner le focus à la fenêtre précédente
            replace_selection(text, old_clip)

        threading.Thread(target=paste_after_focus, daemon=True).start()

    def _on_copy(self):
        text = self._current_result()
        if text:
            try:
                pyperclip.copy(text)
                self._status.configure(text="✓ Copié", text_color=theme.ACCENT)
            except Exception:
                self._status.configure(text="⚠ Copie impossible", text_color=theme.DANGER)

    # ---------- Fermeture au clic extérieur ----------

    def _on_focus_out(self, event=None):
        # FocusOut peut être déclenché par un clic dans un widget interne
        # On vérifie que le focus n'est plus dans la fenêtre via after()
        self.win.after(150, self._check_focus_lost)

    def _check_focus_lost(self):
        try:
            focused = self.win.focus_get()
        except Exception:
            focused = None
        if focused is None:
            self.hide()
        else:
            # Vérifie que le focus est bien dans notre fenêtre
            try:
                w = focused
                while w is not None:
                    if w == self.win:
                        return
                    w = w.master
                self.hide()
            except Exception:
                pass
