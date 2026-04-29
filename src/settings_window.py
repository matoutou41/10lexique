"""
Fenêtre de paramétrage style LocalSend (CustomTkinter, sombre arrondi).
Multi-provider : Anthropic (Claude) ou Google (Gemini).
"""
import tkinter as tk
import customtkinter as ctk
import webbrowser

from config import load_config, save_config
import theme
import labels as lbl
import ai_client


# Listes pour les menus déroulants : on affiche les libellés français,
# on convertit en clé interne au moment de sauver.
LANG_KEYS = list(lbl.LANG_LABELS.keys())
LANG_DISPLAY = [lbl.LANG_LABELS[k] for k in LANG_KEYS]

TONE_KEYS = list(lbl.TONE_LABELS.keys())
TONE_DISPLAY = [lbl.TONE_LABELS[k] for k in TONE_KEYS]


# ---------- Fenêtre principale ----------

def open_settings_modal(root, on_save=None, blocking: bool = False):
    cfg = load_config()

    win = ctk.CTkToplevel(root)
    win.title("10Lexique — Paramètres")
    win.geometry("580x720")
    win.resizable(False, False)
    win.configure(fg_color=theme.BG_DARK)
    win.attributes("-topmost", True)
    win.after(150, lambda: win.attributes("-topmost", False))

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

    # ===== Section IA =====
    _section_title(container, "Fournisseur d'IA")

    _label(container, "Choisissez le service à utiliser")
    provider_var = tk.StringVar(value=cfg.get("provider", "anthropic"))

    # Sélecteur Anthropic / Gemini en boutons segmentés
    seg_frame = ctk.CTkFrame(container, fg_color="transparent")
    seg_frame.pack(fill="x", pady=(0, 14))

    seg = ctk.CTkSegmentedButton(
        seg_frame,
        values=["Anthropic (Claude)", "Google (Gemini)"],
        height=38,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        selected_color=theme.ACCENT,
        selected_hover_color=theme.ACCENT_HOVER,
        unselected_color=theme.BG_CARD,
        unselected_hover_color=theme.BG_HOVER,
        text_color=theme.ACCENT_TEXT,
        font=theme.font(theme.FONT_SIZE_BODY, "bold"),
    )
    seg.pack(fill="x")
    seg.set("Anthropic (Claude)" if provider_var.get() == "anthropic" else "Google (Gemini)")

    # ----- Clé API Anthropic -----
    anthro_frame = ctk.CTkFrame(container, fg_color="transparent")

    _label(anthro_frame, "Clé API Anthropic")
    anthro_key_var = tk.StringVar(value=cfg.get("anthropic_api_key", ""))
    anthro_entry = ctk.CTkEntry(
        anthro_frame,
        textvariable=anthro_key_var,
        show="•",
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        border_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        font=theme.font(theme.FONT_SIZE_BODY),
        placeholder_text="sk-ant-...",
    )
    anthro_entry.pack(fill="x", pady=(0, 6))

    anthro_show = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(
        anthro_frame,
        text="Afficher la clé",
        variable=anthro_show,
        command=lambda: anthro_entry.configure(show="" if anthro_show.get() else "•"),
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_SECONDARY,
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        border_color=theme.BORDER,
        checkmark_color=theme.ACCENT_TEXT,
    ).pack(anchor="w", pady=(0, 4))

    anthro_link = ctk.CTkLabel(
        anthro_frame,
        text="→ Obtenir une clé sur console.anthropic.com",
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.ACCENT,
        cursor="hand2",
        anchor="w",
    )
    anthro_link.pack(fill="x", pady=(0, 10))
    anthro_link.bind("<Button-1>", lambda e: webbrowser.open("https://console.anthropic.com/settings/keys"))

    _label(anthro_frame, "Modèle Claude")
    anthro_models, anthro_labels_map = ai_client.models_for("anthropic")
    anthro_label_to_key = {v: k for k, v in anthro_labels_map.items()}
    current_anthro_model = cfg.get("anthropic_model", "claude-haiku-4-5")
    anthro_model_var = tk.StringVar(value=anthro_labels_map.get(current_anthro_model, anthro_labels_map[anthro_models[0]]))
    ctk.CTkOptionMenu(
        anthro_frame,
        variable=anthro_model_var,
        values=[anthro_labels_map[m] for m in anthro_models],
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
    ).pack(fill="x", pady=(0, 6))

    # ----- Clé API Gemini -----
    gem_frame = ctk.CTkFrame(container, fg_color="transparent")

    _label(gem_frame, "Clé API Google Gemini")
    gem_key_var = tk.StringVar(value=cfg.get("gemini_api_key", ""))
    gem_entry = ctk.CTkEntry(
        gem_frame,
        textvariable=gem_key_var,
        show="•",
        height=36,
        corner_radius=theme.RADIUS_MD,
        fg_color=theme.BG_CARD,
        border_color=theme.BORDER,
        text_color=theme.TEXT_PRIMARY,
        font=theme.font(theme.FONT_SIZE_BODY),
        placeholder_text="AIza...",
    )
    gem_entry.pack(fill="x", pady=(0, 6))

    gem_show = tk.BooleanVar(value=False)
    ctk.CTkCheckBox(
        gem_frame,
        text="Afficher la clé",
        variable=gem_show,
        command=lambda: gem_entry.configure(show="" if gem_show.get() else "•"),
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.TEXT_SECONDARY,
        fg_color=theme.ACCENT,
        hover_color=theme.ACCENT_HOVER,
        border_color=theme.BORDER,
        checkmark_color=theme.ACCENT_TEXT,
    ).pack(anchor="w", pady=(0, 4))

    gem_link = ctk.CTkLabel(
        gem_frame,
        text="→ Obtenir une clé sur aistudio.google.com/apikey (gratuit)",
        font=theme.font(theme.FONT_SIZE_SMALL),
        text_color=theme.ACCENT,
        cursor="hand2",
        anchor="w",
    )
    gem_link.pack(fill="x", pady=(0, 10))
    gem_link.bind("<Button-1>", lambda e: webbrowser.open("https://aistudio.google.com/apikey"))

    _label(gem_frame, "Modèle Gemini")
    gem_models, gem_labels_map = ai_client.models_for("gemini")
    gem_label_to_key = {v: k for k, v in gem_labels_map.items()}
    current_gem_model = cfg.get("gemini_model", "gemini-2.5-flash")
    gem_model_var = tk.StringVar(value=gem_labels_map.get(current_gem_model, gem_labels_map[gem_models[0]]))
    ctk.CTkOptionMenu(
        gem_frame,
        variable=gem_model_var,
        values=[gem_labels_map[m] for m in gem_models],
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
    ).pack(fill="x", pady=(0, 6))

    # Container qui swappe entre les deux frames selon le provider sélectionné
    provider_panel = ctk.CTkFrame(container, fg_color="transparent")
    provider_panel.pack(fill="x", pady=(8, 14))

    # On reparente les frames dans le panel
    anthro_frame.master = provider_panel
    gem_frame.master = provider_panel

    def _show_provider_panel(name: str):
        # Cache les deux puis affiche le bon
        for f in (anthro_frame, gem_frame):
            f.pack_forget()
        if name == "anthropic":
            anthro_frame.pack(in_=provider_panel, fill="x")
        else:
            gem_frame.pack(in_=provider_panel, fill="x")

    def _on_seg_change(value):
        new_provider = "anthropic" if value.startswith("Anthropic") else "gemini"
        provider_var.set(new_provider)
        _show_provider_panel(new_provider)

    seg.configure(command=_on_seg_change)
    _show_provider_panel(provider_var.get())

    # ===== Section Raccourcis =====
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

    # ===== Section Préférences =====
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

    # ===== Boutons =====
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
        active_provider = provider_var.get()
        new_cfg = {
            "provider": active_provider,
            "anthropic_api_key": anthro_key_var.get().strip(),
            "gemini_api_key": gem_key_var.get().strip(),
            "anthropic_model": anthro_label_to_key.get(anthro_model_var.get(), "claude-haiku-4-5"),
            "gemini_model": gem_label_to_key.get(gem_model_var.get(), "gemini-2.5-flash"),
            "hotkey_correct": hk_correct.get().strip(),
            "hotkey_translate": hk_translate.get().strip(),
            "hotkey_improve": hk_improve.get().strip(),
            "translate_target_lang": lbl.label_to_key(lbl.LANG_LABELS, lang_var.get(), "english"),
            "rephrase_tone": lbl.label_to_key(lbl.TONE_LABELS, tone_var.get(), "neutral"),
        }

        # Valide qu'il y a une clé pour le provider actif
        if active_provider == "anthropic" and not new_cfg["anthropic_api_key"]:
            status_var.set("⚠ Clé API Anthropic manquante")
            status_label.configure(text_color=theme.DANGER)
            return
        if active_provider == "gemini" and not new_cfg["gemini_api_key"]:
            status_var.set("⚠ Clé API Gemini manquante")
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

    # Focus sur la bonne clé selon le provider actif
    if provider_var.get() == "anthropic":
        anthro_entry.focus_set()
    else:
        gem_entry.focus_set()

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
