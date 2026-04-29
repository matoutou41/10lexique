"""
Point d'entrée 10Lexique.
"""
import os
import sys
import threading
import traceback

import keyboard
import pyperclip
import customtkinter as ctk

from config import load_config, save_config
from claude_client import ClaudeClient
from text_handler import get_selected_text
from notifier import notify
from popup import CorrectorPopup, TAB_CORRECT, TAB_TRANSLATE, TAB_IMPROVE
from tray import run_tray
from tray_menu import TrayMenu


# ---------- État global ----------
class AppState:
    def __init__(self):
        self.config = load_config()
        self.client = None
        self.busy = False
        self.popup = None
        self.tray_menu = None
        self.root = None

    def rebuild_client(self):
        if not self.config.get("api_key"):
            self.client = None
            return
        try:
            self.client = ClaudeClient(
                api_key=self.config["api_key"],
                model=self.config.get("model", "claude-haiku-4-5"),
            )
        except Exception as e:
            self.client = None
            notify("10Lexique", f"Erreur d'initialisation : {e}")


state = AppState()


# ---------- Capture + déclenchement popup ----------

def _trigger_action(action: str):
    if state.busy:
        return
    if state.client is None:
        notify("10Lexique", "Configurez d'abord votre clé API (clic sur l'icône).")
        return

    state.busy = True

    def worker():
        try:
            selected, old_clip = get_selected_text()
            if not selected.strip():
                notify("10Lexique", "Aucun texte sélectionné.")
                return
            state.popup.show_for_action(action, selected, old_clip)
        finally:
            state.busy = False

    threading.Thread(target=worker, daemon=True).start()


def handle_correct():
    _trigger_action(TAB_CORRECT)


def handle_translate():
    _trigger_action(TAB_TRANSLATE)


def handle_improve():
    _trigger_action(TAB_IMPROVE)


def handle_test_clipboard():
    if state.client is None:
        notify("10Lexique", "Configurez d'abord votre clé API.")
        return
    try:
        text = pyperclip.paste()
        if not text or not text.strip():
            notify("10Lexique", "Le presse-papier est vide.")
            return
        state.popup.show_for_action(TAB_CORRECT, text, "")
    except Exception as e:
        notify("10Lexique", f"Erreur : {e}")


# ---------- Hotkeys ----------

_registered_hotkeys = []


def register_hotkeys():
    global _registered_hotkeys
    for h in _registered_hotkeys:
        try:
            keyboard.remove_hotkey(h)
        except Exception:
            pass
    _registered_hotkeys = []

    cfg = state.config
    bindings = [
        (cfg.get("hotkey_correct", "alt+k"), handle_correct, "correction"),
        (cfg.get("hotkey_translate", "alt+l"), handle_translate, "traduction"),
        (cfg.get("hotkey_improve", "alt+m"), handle_improve, "amélioration"),
    ]
    for hk, fn, label in bindings:
        if not hk:
            continue
        try:
            h = keyboard.add_hotkey(hk, fn, suppress=False)
            _registered_hotkeys.append(h)
            print(f"Raccourci {label} : {hk}")
        except Exception as e:
            print(f"Impossible d'enregistrer {hk} : {e}")


# ---------- Settings ----------

def open_settings_window():
    def _open():
        from settings_window import open_settings_modal
        open_settings_modal(state.root, on_save=on_settings_saved)
    state.root.after(0, _open)


def on_settings_saved(new_cfg):
    state.config = new_cfg
    state.rebuild_client()
    register_hotkeys()
    notify("10Lexique", "Paramètres mis à jour.")


def quit_app():
    print("Arrêt…")
    try:
        keyboard.unhook_all_hotkeys()
    except Exception:
        pass
    try:
        if state.root:
            state.root.after(0, state.root.quit)
    except Exception:
        pass
    os._exit(0)


# ---------- Menu tray custom ----------

def show_tray_menu():
    """Construit la liste des items et affiche le menu custom à la position du curseur."""
    cfg = state.config
    hk = cfg.get("hotkey_correct", "alt+k").upper()

    items = [
        ("title", "10Lexique"),
        (f"✓  Corriger ({hk})", handle_correct),
        ("🌐  Traduire", handle_translate),
        ("✨  Améliorer", handle_improve),
        ("---", None),
        ("📋  Corriger le presse-papier", handle_test_clipboard),
        ("⚙  Paramètres…", open_settings_window),
        ("---", None),
        ("✕  Quitter 10Lexique", quit_app),
    ]

    def _show():
        try:
            x = state.root.winfo_pointerx()
            y = state.root.winfo_pointery()
        except Exception:
            x, y = 1000, 800
        state.tray_menu.show_at(x, y, items)

    state.root.after(0, _show)


# ---------- Bootstrap ----------

def main():
    ctk.set_appearance_mode("dark")

    state.root = ctk.CTk()
    state.root.withdraw()

    # Popup principale + menu tray custom
    state.popup = CorrectorPopup(
        state.root,
        claude_client_provider=lambda: state.client,
        config_provider=lambda: state.config,
    )
    state.tray_menu = TrayMenu(state.root)

    # Premier lancement → paramètres
    if not state.config.get("api_key"):
        from settings_window import open_settings_modal
        notify("10Lexique", "Premier lancement : configurez votre clé API.")
        open_settings_modal(state.root, on_save=on_settings_saved, blocking=True)

    state.rebuild_client()
    register_hotkeys()

    notify(
        "10Lexique",
        f"Actif. Raccourci : {state.config.get('hotkey_correct', 'alt+k').upper()}",
        timeout=3,
    )

    # Tray dans un thread séparé
    threading.Thread(
        target=run_tray,
        args=(show_tray_menu, quit_app),
        daemon=True,
    ).start()

    try:
        state.root.mainloop()
    finally:
        quit_app()


if __name__ == "__main__":
    main()
