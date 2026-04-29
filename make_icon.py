"""
Génère assets/icon.ico (icône Windows multi-résolution) pour 10lex.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _font(size_px: int):
    for name in ("seguibl.ttf", "seguisb.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size_px)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def make_icon_image(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Carré arrondi sombre avec bordure menthe
    pad = max(1, size // 16)
    radius = size // 5
    border = max(1, size // 32)
    d.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=radius,
        fill=(30, 31, 34, 255),
        outline=(98, 224, 200, 255),
        width=border,
    )

    # Texte "10L" centré
    text = "10L"
    # Taille adaptative pour tenir
    font_size = int(size * 0.42)
    font = _font(font_size)
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Réduit si trop large
    while tw > size - 2 * pad - 4 * border and font_size > 8:
        font_size -= 2
        font = _font(font_size)
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1] - size * 0.02
    d.text((x, y), text, fill=(98, 224, 200, 255), font=font)
    return img


def main():
    out_dir = Path(__file__).parent / "assets"
    out_dir.mkdir(exist_ok=True)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [make_icon_image(s) for s in sizes]
    ico_path = out_dir / "icon.ico"
    images[0].save(ico_path, format="ICO", sizes=[(s, s) for s in sizes], append_images=images[1:])
    print(f"Icône générée : {ico_path}")

    png_path = out_dir / "icon.png"
    make_icon_image(256).save(png_path)
    print(f"PNG : {png_path}")


if __name__ == "__main__":
    main()
