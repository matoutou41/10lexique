"""
Gestion de la configuration : clé API Claude, raccourcis, modèle.
La config est sauvegardée dans %APPDATA%/ClaudeCorrecteur/config.json
"""
import json
import os
from pathlib import Path

APP_NAME = "10Lexique"

# Sur Windows : %APPDATA%\ClaudeCorrecteur. Sur Linux/Mac (pour dev) : ~/.config/ClaudeCorrecteur
if os.name == "nt":
    CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    CONFIG_DIR = Path.home() / ".config" / APP_NAME

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_key": "",
    "model": "claude-haiku-4-5",
    "hotkey_correct": "alt+k",
    "hotkey_translate": "alt+l",
    "hotkey_improve": "alt+m",
    "translate_target_lang": "english",
    "rephrase_tone": "neutral",
}


def load_config() -> dict:
    """Charge la config (ou crée le fichier par défaut)."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # Merge avec les valeurs par défaut pour les clés manquantes (futures versions)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    """Sauvegarde la config sur disque."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def update_config(**kwargs) -> dict:
    cfg = load_config()
    cfg.update(kwargs)
    save_config(cfg)
    return cfg
