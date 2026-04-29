"""
Notifications Windows (toast).
Fallback silencieux si plyer indisponible.
"""
try:
    from plyer import notification
    _HAS_PLYER = True
except ImportError:
    _HAS_PLYER = False


def notify(title: str, message: str, timeout: int = 3) -> None:
    if not _HAS_PLYER:
        print(f"[{title}] {message}")
        return
    try:
        notification.notify(
            title=title,
            message=message[:240],
            app_name="10lex",
            timeout=timeout,
        )
    except Exception:
        # Certaines machines Windows refusent les toasts ; on continue silencieusement
        print(f"[{title}] {message}")
