"""
Thème visuel inspiré de LocalSend : sombre, arrondi, accent turquoise/menthe.
Utilisé par toutes les fenêtres pour un rendu cohérent.
"""

# Palette
BG_DARK = "#1E1F22"         # fond principal (un peu plus clair que pur noir)
BG_SIDEBAR = "#17181B"      # sidebar (plus sombre)
BG_CARD = "#26272B"          # cartes / zones de texte
BG_HOVER = "#2E2F34"
BORDER = "#34353A"

ACCENT = "#62E0C8"           # turquoise/menthe LocalSend
ACCENT_HOVER = "#7BEAD3"
ACCENT_TEXT = "#0A1F1A"      # texte sur fond accent (foncé pour contraste)

TEXT_PRIMARY = "#E6E7EA"
TEXT_SECONDARY = "#9CA0A8"
TEXT_MUTED = "#6B6F78"

DANGER = "#E06E6E"
SUCCESS = "#62E0C8"

# Polices (Segoe UI sur Windows par défaut)
FONT_FAMILY = "Segoe UI"
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADING = 13
FONT_SIZE_BODY = 11
FONT_SIZE_SMALL = 10

# Rayons / espacement
RADIUS_LG = 12
RADIUS_MD = 8
RADIUS_SM = 6
PAD_LG = 16
PAD_MD = 10
PAD_SM = 6


def font(size: int = FONT_SIZE_BODY, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)
