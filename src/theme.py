"""
Thème visuel 10lex — DA cartoon violette, en cohérence avec la landing.
Palette tirée du PSD de référence + favicon.
"""

# === Palette violette claire (style landing 10lex) ===
BG_DARK = "#B47BFF"          # fond principal (violet/lavande de la landing)
BG_SIDEBAR = "#9B61F0"       # sidebar — violet plus saturé
BG_CARD = "#EFDDF9"          # cartes / zones de texte = cream pill
BG_HOVER = "#E1C8F2"         # hover sur cream
BORDER = "#0E0814"           # contour noir cartoon (épais)

ACCENT = "#402C90"           # violet sombre (= splash) — CTA / focus
ACCENT_HOVER = "#5237B5"
ACCENT_TEXT = "#FFFFFF"      # texte blanc sur accent sombre

TEXT_PRIMARY = "#0E0814"     # noir cartoon sur cream
TEXT_SECONDARY = "#3A1B6E"   # violet foncé pour secondary
TEXT_MUTED = "#7A5FB5"       # violet doux pour muted

# Pour le texte sur fond violet (sidebar / fond principal)
TEXT_ON_DARK = "#FFFFFF"
TEXT_ON_DARK_MUTED = "#EFDDF9"

DANGER = "#FF4FA0"           # hot pink (rappel de la langue du dino)
SUCCESS = "#402C90"

# Polices
# Coming Soon n'existe pas en système — on utilise Comic Sans MS qui est natif
# sur Windows et donne un rendu cartoon manuscrit. Sniglet/Bagel Fat One ne sont
# pas dispo non plus, on prend une bold display approchante.
FONT_FAMILY = "Comic Sans MS"        # body cartoon manuscrit
FONT_FAMILY_DISPLAY = "Bahnschrift"  # display lourd condensé natif Win
FONT_SIZE_TITLE = 18
FONT_SIZE_HEADING = 14
FONT_SIZE_BODY = 12
FONT_SIZE_SMALL = 10

# Rayons / espacement (généreux, look pill cartoon)
RADIUS_LG = 22
RADIUS_MD = 16
RADIUS_SM = 10
PAD_LG = 18
PAD_MD = 12
PAD_SM = 8


def font(size: int = FONT_SIZE_BODY, weight: str = "normal") -> tuple:
    return (FONT_FAMILY, size, weight)


def font_display(size: int = FONT_SIZE_TITLE, weight: str = "bold") -> tuple:
    return (FONT_FAMILY_DISPLAY, size, weight)
