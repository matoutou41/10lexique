"""
Gestion de la configuration : clés API (Anthropic + Gemini), provider actif,
modèle par provider, raccourcis, préférences.

La config est sauvegardée dans %APPDATA%/10Lexique/config.json
"""
import json
import os
from pathlib import Path

APP_NAME = "10Lexique"

# Sur Windows : %APPDATA%\10Lexique. Sur Linux/Mac (pour dev) : ~/.config/10Lexique
if os.name == "nt":
    CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
else:
    CONFIG_DIR = Path.home() / ".config" / APP_NAME

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    # Multi-provider IA
    "provider": "anthropic",                # "anthropic" ou "gemini"
    "anthropic_api_key": "",
    "gemini_api_key": "",
    "anthropic_model": "claude-haiku-4-5",
    "gemini_model": "gemini-2.5-flash",

    # Raccourcis
    "hotkey_correct": "alt+k",
    "hotkey_translate": "alt+l",
    "hotkey_improve": "alt+m",

    # Préférences
    "translate_target_lang": "english",
    "rephrase_tone": "neutral",
}


def _migrate(cfg: dict) -> dict:
    """
    Migration des configs v1.0 (clé unique 'api_key' + 'model' Anthropic) vers v1.1
    (multi-provider). Préserve les paramètres existants.
    """
    # v1.0 → v1.1 : api_key/model étaient pour Claude
    if "api_key" in cfg and "anthropic_api_key" not in cfg:
        cfg["anthropic_api_key"] = cfg.pop("api_key")
    if "model" in cfg and "anthropic_model" not in cfg:
        old_model = cfg.pop("model")
        # Si le modèle commence par "claude", on le garde dans anthropic_model
        if old_model and old_model.startswith("claude"):
            cfg["anthropic_model"] = old_model
    return cfg


def load_config() -> dict:
    """Charge la config (ou crée le fichier par défaut)."""
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        cfg = _migrate(cfg)
        # Merge avec les valeurs par défaut pour les clés manquantes
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


def has_active_api_key(cfg: dict) -> bool:
    """Renvoie True si la clé API du provider actif est renseignée."""
    provider = cfg.get("provider", "anthropic")
    if provider == "anthropic":
        return bool(cfg.get("anthropic_api_key", "").strip())
    if provider == "gemini":
        return bool(cfg.get("gemini_api_key", "").strip())
    return False


def active_credentials(cfg: dict):
    """Retourne (provider, api_key, model) pour le provider actif."""
    provider = cfg.get("provider", "anthropic")
    if provider == "anthropic":
        return provider, cfg.get("anthropic_api_key", ""), cfg.get("anthropic_model", "claude-haiku-4-5")
    if provider == "gemini":
        return provider, cfg.get("gemini_api_key", ""), cfg.get("gemini_model", "gemini-2.5-flash")
    return provider, "", ""
