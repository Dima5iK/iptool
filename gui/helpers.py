# helpers.py
def format_speed(bps: int, multiplier: int = 1) -> str:
    """Форматирование скорости в Гб/с, Мб/с или Кб/с"""
    bps = bps * multiplier
    if bps >= 1_000_000_000:
        return f"{bps/1_000_000_000:.2f} Гбит/с"
    elif bps >= 1_000_000:
        return f"{bps/1_000_000:.2f} Мбит/с"
    elif bps >= 1_000:
        return f"{bps/1_000:.2f} Кбит/с"
    else:
        return f"{bps:.0f} бит/с"

def format_interface_status(status: str) -> str:
    """Возвращает символ для отображения состояния интерфейса"""
    if status == "Up":
        return "▲"
    elif status == "Disconnected":
        return "▼"
    else:  # "Disabled", "Not Present" и т.п.
        return " "