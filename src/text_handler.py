"""
Capture du texte sélectionné et remplacement via le presse-papier.
Plus robuste que la v1 :
- Utilise un sentinel unique pour détecter quand le presse-papier a vraiment été mis à jour
- Plus long timeout pour les navigateurs lents
- Plusieurs tentatives Ctrl+C
"""
import time
import uuid
import keyboard
import pyperclip


def _safe_paste() -> str:
    try:
        return pyperclip.paste() or ""
    except Exception:
        return ""


def _safe_copy(value: str) -> bool:
    try:
        pyperclip.copy(value)
        return True
    except Exception:
        return False


def get_selected_text(timeout: float = 1.2) -> tuple[str, str]:
    """
    Récupère le texte actuellement sélectionné dans n'importe quelle application.
    Retourne (texte_sélectionné, ancien_presse_papier).

    Méthode :
    1. Sauvegarde le presse-papier
    2. Met un sentinel unique dans le presse-papier
    3. Envoie Ctrl+C (l'app copie sa sélection par dessus le sentinel)
    4. Attend que le presse-papier change ET ne soit plus le sentinel
    5. Renvoie le résultat
    """
    old_clipboard = _safe_paste()

    sentinel = f"__CCSEN_{uuid.uuid4().hex}__"
    if not _safe_copy(sentinel):
        # Si le presse-papier est inaccessible, on essaie quand même Ctrl+C direct
        keyboard.send("ctrl+c")
        time.sleep(0.2)
        return _safe_paste(), old_clipboard

    # Petit délai pour que le sentinel soit bien posé
    time.sleep(0.08)

    # Envoie Ctrl+C — on essaie deux fois espacées pour les apps lentes
    keyboard.send("ctrl+c")

    deadline = time.time() + timeout
    second_try_done = False
    selected = ""

    while time.time() < deadline:
        time.sleep(0.05)
        current = _safe_paste()
        if current and current != sentinel:
            selected = current
            break
        # Mi-parcours : on retente une fois
        if not second_try_done and time.time() > deadline - timeout / 2:
            keyboard.send("ctrl+c")
            second_try_done = True

    # Nettoyage : si on a juste le sentinel ou rien, on n'a rien sélectionné
    if not selected or selected == sentinel:
        # Restaure et renvoie vide
        if old_clipboard:
            _safe_copy(old_clipboard)
        else:
            _safe_copy("")
        return "", old_clipboard

    return selected, old_clipboard


def replace_selection(new_text: str, old_clipboard: str = "") -> None:
    """
    Remplace la sélection courante par new_text via copier-coller.
    Restaure ensuite l'ancien presse-papier.
    """
    if not _safe_copy(new_text):
        return
    time.sleep(0.1)
    keyboard.send("ctrl+v")
    time.sleep(0.35)
    if old_clipboard:
        _safe_copy(old_clipboard)


def looks_like_url_only(text: str) -> bool:
    """
    Détecte si le texte ne contient qu'une URL (cas typique du bug navigateur :
    Ctrl+C copie l'URL au lieu du texte sélectionné).
    """
    t = text.strip()
    if not t or "\n" in t:
        return False
    if " " in t:
        return False
    if t.startswith(("http://", "https://", "ftp://", "www.")):
        return True
    return False
