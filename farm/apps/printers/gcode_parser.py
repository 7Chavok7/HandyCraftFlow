# farm/apps/printers/gcode_parser.py
"""Парсер заголовка gcode: вес филамента и время печати.

Слайсеры (Cura, PrusaSlicer, Bambu Studio) пишут в начало файла комментарии:
  ; filament used [g] = 12.40
  ; estimated printing time (normal mode) = 2h 43m 12s
  ; model name = organizer_v2.stl

Возвращает dict: {"weight_g": float | None, "time_min": int | None}.
"""
import re
from pathlib import Path


_RE_WEIGHT = re.compile(
    r"filament used \[g\]\s*=\s*([\d.]+)", re.IGNORECASE,
)
_RE_TIME_HMS = re.compile(
    r"estimated printing time[^=]*=\s*(?:(\d+)d\s*)?(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s)?",
    re.IGNORECASE,
)
# Bambu Studio иногда пишет просто "total estimated time: 2h 43m"
_RE_TIME_SHORT = re.compile(
    r"total estimated time:\s*(?:(\d+)h\s*)?(?:(\d+)m\s*)?(?:(\d+)s)?",
    re.IGNORECASE,
)


def parse_gcode_header(file_path: str | Path) -> dict:
    """Прочитать первые ~200 строк gcode и вытащить вес/время."""
    result = {"weight_g": None, "time_min": None}
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return result

    header_lines = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i >= 200:
                break
            if not line.startswith(";"):
                # заголовок gcode — это комментарии в начале; как только
                # пошли команды (G1, M104...) — дальше не читаем
                if header_lines:
                    break
                continue
            header_lines.append(line)

    text = "".join(header_lines)

    m = _RE_WEIGHT.search(text)
    if m:
        try:
            result["weight_g"] = float(m.group(1))
        except ValueError:
            pass

    m = _RE_TIME_HMS.search(text)
    if m:
        days = int(m.group(1) or 0)
        hours = int(m.group(2) or 0)
        minutes = int(m.group(3) or 0)
        seconds = int(m.group(4) or 0)
        total_min = days * 24 * 60 + hours * 60 + minutes + (1 if seconds >= 30 else 0)
        if total_min > 0:
            result["time_min"] = total_min
    else:
        m = _RE_TIME_SHORT.search(text)
        if m:
            hours = int(m.group(1) or 0)
            minutes = int(m.group(2) or 0)
            seconds = int(m.group(3) or 0)
            total_min = hours * 60 + minutes + (1 if seconds >= 30 else 0)
            if total_min > 0:
                result["time_min"] = total_min

    return result