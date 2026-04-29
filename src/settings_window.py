"""
Fenêtre de paramétrage style LocalSend (CustomTkinter, sombre arrondi).
"""
import tkinter as tk
import customtkinter as ctk
import webbrowser

from config import load_config, save_config
import theme
import labels as lbl


MODELS = [
    "claude-haiku-4-5",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
]

# Listes pour les menus déroulants : on affiche les libellés français,
# on convertit en clé interne au moment de sauver.
LANG_KEYS = list(lbl.LANG_LABELS.keys())
LANG_DISPLAY = [lbl.LANG_LABELS[k] for k in LANG_KEYS]

TONE_KEYS = list(lbl.TONE_LABELS.keys())
TONE_DISPLAY = [lbl.TONE_LABELS[k] for k in TONE_KEYS]


def open_settings_modal(root, on_save=None, blocking: bool = False):
    cfg = load_config()

    win = ctk.CTkToplevel(root)
    win.title("10Lexique — Paramètres")
    win.geometry("560x620")
    win.resizable(False, False)
    win.configure(fg_color=theme.BG_DARK)
    win.attributes("-topmost", True)
    win.after(150, lambda: win.attributes("-topmost", False))

    # Container avec padding
    container = ctk.CTkScrollableFrame(
        win,
        fg_color=theme.BG_DARK,
        scrollbar_button_color=theme.BG_HOVER,
        scrollbar_button_hover_color=theme.BORDER,
    )
    container.pack(fill="both", expand=True, padx=20, pady=20)

    # Titre
    ctk.CTkLabel(
        container,
        text="Paramètres",
        font=theme.font(theme.FONT_SIZE_TITLE + 2, "bold"),
        text_color=theme.TEXT_PRIMARY,
        anchor="w",
    ).pack(fill="x", pady=(0, 16))

    # ----- Section API -----
    _section_title(container, "Connexion")

    _label(container, "Clé API Anthropic")
    api_var = tk.StringVar(value=cfg.get("api_key", ""))
    api_entry = ctk.CTkEntry(
        container,
        textvariable=api_var,
        show="•",
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        border_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        font=theme.font(theme.FONT_SIZE_BODY),
        placeholder_text="sk-ant-...",
    )
    api_entry.pack(fill="x", pady=(0, 6))

    show_var = tk.BooleanVar(value=False)

    def toggle_show():
        api_entry.configure(show="" if show_var.get() else "•")

    ctk.CTkCheckBox(
        container,
        text="Afficher la clé",
        variable=show_var,
        command=toggle_show,
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_SECONDARY,
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        border_color=theme.BORDER,
        checkmark_color=theme.ACCENT_TEXT,
    ).pack(anchor="w", pady=(0, 4))

    link = ctk.CTkLabel(
        container,
        text="→ Obtenir une clé sur console.anthropic.com",
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.ACCENT,
        cursor="hand2",
        anchor="w",
    )
    link.pack(fill="x", pady=(0, 14))
    link.bind("<Button-1>", lambda e: webbrowser.open("https://console.anthropic.com/settings/keys"))

    _label(container, "Modèle Claude")
    model_var = tk.StringVar(value=cfg.get("model", "claude-haiku-4-5"))
    ctk.CTkOptionMenu(
        container,
        variable=model_var,
        values=MODELS,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        button_color=theme.BG_HOVER,
        button_hover_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        dropdown_fg_color=theme.BG_CARD,
        dropdown_text_color=theme.TEXT_PRIMARY,
        dropdown_hover_color=theme.BG_HOVER,
        font=theme.font(theme.FONT_SIZE_BODY),
    ).pack(fill="x", pady=(0, 14))

    # ----- Section Raccourcis -----
    _section_title(container, "Raccourcis clavier")

    _label(container, "Corriger l'orthographe")
    hk_correct = tk.StringVar(value=cfg.get("hotkey_correct", "alt+k"))
    _entry(container, hk_correct).pack(fill="x", pady=(0, 10))

    _label(container, "Traduire")
    hk_translate = tk.StringVar(value=cfg.get("hotkey_translate", "alt+l"))
    _entry(container, hk_translate).pack(fill="x", pady=(0, 10))

    _label(container, "Améliorer le texte")
    hk_improve = tk.StringVar(value=cfg.get("hotkey_improve", "alt+m"))
    _entry(container, hk_improve).pack(fill="x", pady=(0, 4))

    ctk.CTkLabel(
        container,
        text="Format : alt+k, ctrl+shift+espace, f9…",
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_MUTED,
        anchor="w",
    ).pack(fill="x", pady=(0, 14))

    # ----- Section Traduction & Style -----
    _section_title(container, "Préférences")

    _label(container, "Langue cible (traduction)")
    current_lang_key = cfg.get("translate_target_lang", "english")
    lang_var = tk.StringVar(value=lbl.key_to_label(lbl.LANG_LABELS, current_lang_key))
    ctk.CTkOptionMenu(
        container,
        variable=lang_var,
        values=LANG_DISPLAY,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        button_color=theme.BG_HOVER,
        button_hover_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        dropdown_fg_color=theme.BG_CARD,
        dropdown_text_color=theme.TEXT_PRIMARY,
        dropdown_hover_color=theme.BG_HOVER,
        font=theme.font(theme.FONT_SIZE_BODY),
    ).pack(fill="x", pady=(0, 10))

    _label(container, "Style d'amélioration")
    current_tone_key = cfg.get("rephrase_tone", "neutral")
    tone_var = tk.StringVar(value=lbl.key_to_label(lbl.TONE_LABELS, current_tone_key))
    ctk.CTkOptionMenu(
        container,
        variable=tone_var,
        values=TONE_DISPLAY,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        button_color=theme.BG_HOVER,
        button_hover_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        dropdown_fg_color=theme.BG_CARD,
        dropdown_text_color=theme.TEXT_PRIMARY,
        dropdown_hover_color=theme.BG_HOVER,
        font=theme.font(theme.FONT_SIZE_BODY),
    ).pack(fill="x", pady=(0, 14))

    # ----- Boutons -----
    btn_frame = ctk.CTkFrame(container, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(8, 0))

    status_var = tk.StringVar(value="")
    status_label = ctk.CTkLabel(
        btn_frame,
        textvariable=status_var,
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_MUTED,
    )
    status_label.pack(side="left")

    def on_cancel():
        win.destroy()

    def on_save_click():
        new_cfg = {
            "api_key": api_var.get().strip(),
            "model": model_var.get(),
            "hotkey_correct": hk_correct.get().strip(),
            "hotkey_translate": hk_translate.get().strip(),
            "hotkey_improve": hk_improve.get().strip(),
            "translate_target_lang": lbl.label_to_key(lbl.LANG_LABELS, lang_var.get(), "english"),
            "rephrase_tone": lbl.label_to_key(lbl.TONE_LABELS, tone_var.get(), "neutral"),
        }
        if not new_cfg["api_key"]:
            status_var.set("⚠ Clé API manquante")
            status_label.configure(text_color=theme.DANGER)
            return
        cfg.update(new_cfg)
        save_config(cfg)
        if on_save:
            on_save(cfg)
        status_var.set("✓ Enregistré")
        status_label.configure(text_color=theme.ACCENT)
        win.after(700, win.destroy)

    ctk.CTkButton(
        btn_frame,
        text="Annuler",
        command=on_cancel,
        width=90,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        hover_color=theme.BG_HOVER,
        text_color=theme.TEXT_PRIMARY,
        border_width=1,
        border_color=theme.BORDER,
        font=theme.font(theme.FONT_SIZE_BODY),
    ).pack(side="right", padx=(6, 0))

    ctk.CTkButton(
        btn_frame,
        text="Enregistrer",
        command=on_save_click,
        width=130,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        text_color=theme.ACCENT_TEXT,
        font=theme.font(theme.FONT_SIZE_BODY, "bold"),
    ).pack(side="right", padx=(6, 0))

    api_entry.focus_set()

    if blocking:
        win.grab_set()
        root.wait_window(win)


# ---------- Helpers ----------

def _section_title(parent, text: str):
    ctk.CTkLabel(
        parent,
        text=text.upper(),
        font=theme.font(theme.FONT_SIZE_SMALL, "bold"),
        text_color=theme.ACCENT,
        anchor="w",
    ).pack(fill="x", pady=(8, 8))


def _label(parent, text: str):
    ctk.CTkLabel(
        parent,
        text=text,
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_SECONDARY,
        anchor="w",
    ).pack(fill="x", pady=(0, 4))


def _entry(parent, var):
    return ctk.CTkEntry(
        parent,
        textvariable=var,
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        border_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        font=theme.font(theme.FONT_SIZE_BODY),
    )
