"""
Icône en barre des tâches Windows.
- Clic GAUCHE : ouvre notre menu custom sombre arrondi (TrayMenu)
- Le menu pystray par défaut est minimal (juste un item Quitter de secours,
  au cas où le menu custom ne marcherait pas)
"""
import os
import sys
import threading
from PIL import Image, ImageDraw, ImageFont
import pystray


def _resource_path(*parts) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *parts)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, *parts)


def _load_icon_image() -> Image.Image:
    icon_path = _resource_path("assets", "icon.png")
    if os.path.exists(icon_path):
        try:
            return Image.open(icon_path).convert("RGBA")
        except Exception:
            pass
    # Fallback procédural
    size = 64
    img = Image.new("RGBA", (size, size), (30, 31, 34, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, size - 4, size - 4), radius=12, fill=(30, 31, 34, 255), outline=(98, 224, 200, 255), width=2)
    try:
        font = ImageFont.truetype("arial.ttf", int(size * 0.45))
    except (OSError, IOError):
        font = ImageFont.load_default()
    text = "10L"
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]), text, fill=(98, 224, 200, 255), font=font)
    return img


def run_tray(on_icon_click, on_quit):
    """
    on_icon_click : callable() — appelé sur clic gauche sur l'icône.
                    Doit afficher le menu custom à la position du curseur.
    on_quit : callable() — appelé pour quitter (depuis le menu de secours pystray).
    """
    image = _load_icon_image()

    def left_click_action(icon, item=None):
        # Lance dans le thread principal de l'app (Tk)
        threading.Thread(target=on_icon_click, daemon=True).start()

    def quit_action(icon, item):
        icon.stop()
        on_quit()

    # Menu pystray minimal (secours / accessibilité). default=True = clic gauche.
    menu = pystray.Menu(
        pystray.MenuItem("Ouvrir le menu", left_click_action, default=True),
        pystray.MenuItem("Quitter (urgence)", quit_action),
    )

    icon = pystray.Icon("10lex", image, "10lex — clic pour ouvrir", menu)
    icon.run()
