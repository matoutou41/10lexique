"""
Libellés français pour les options de l'app.
Les CLÉS internes restent en anglais (utilisées par ai_client.py),
seules les LIBELLÉS affichés sont traduits.
"""

# Tons de reformulation
TONE_LABELS = {
    "neutral": "Neutre",
    "formal": "Formel",
    "casual": "Décontracté",
    "shorter": "Plus court",
    "longer": "Plus long",
}

TONE_DESCRIPTIONS = {
    "neutral": "Style neutre et clair",
    "formal": "Style formel et professionnel",
    "casual": "Style décontracté et naturel",
    "shorter": "Plus concis (longueur réduite)",
    "longer": "Plus développé et détaillé",
}

# Langues
LANG_LABELS = {
    "english": "Anglais",
    "french": "Français",
    "japanese": "Japonais",
    "spanish": "Espagnol",
    "german": "Allemand",
    "italian": "Italien",
    "chinese": "Chinois",
    "korean": "Coréen",
    "portuguese": "Portugais",
    "dutch": "Néerlandais",
    "russian": "Russe",
    "arabic": "Arabe",
}


def label_to_key(mapping: dict, label: str, default: str) -> str:
    """Retrouve la clé interne à partir du libellé affiché."""
    for k, v in mapping.items():
        if v == label:
            return k
    return default


def key_to_label(mapping: dict, key: str) -> str:
    return mapping.get(key, key)
