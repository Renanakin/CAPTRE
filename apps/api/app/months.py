import re
from datetime import date

MONTH_ALIASES = {
    "january": 1,
    "jan": 1,
    "enero": 1,
    "ene": 1,
    "february": 2,
    "feb": 2,
    "febrero": 2,
    "march": 3,
    "mar": 3,
    "marzo": 3,
    "april": 4,
    "apr": 4,
    "abril": 4,
    "may": 5,
    "mayo": 5,
    "june": 6,
    "jun": 6,
    "junio": 6,
    "july": 7,
    "jul": 7,
    "julio": 7,
    "august": 8,
    "aug": 8,
    "agosto": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "septiembre": 9,
    "october": 10,
    "oct": 10,
    "octubre": 10,
    "november": 11,
    "nov": 11,
    "noviembre": 11,
    "december": 12,
    "dec": 12,
    "diciembre": 12,
    "dic": 12,
}


def _safe_date(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def parse_issue_date(text: str) -> str | None:
    # 1) dd/mm/yyyy or dd-mm-yyyy
    for m in re.finditer(r"\b([0-3]?\d)[/\-]([0-1]?\d)[/\-]((?:19|20)?\d{2})\b", text):
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        if year < 100:
            year += 2000
        parsed = _safe_date(year, month, day)
        if parsed:
            return parsed

    # 2) yyyy-mm-dd
    for m in re.finditer(r"\b((?:19|20)\d{2})\-([0-1]?\d)\-([0-3]?\d)\b", text):
        year = int(m.group(1))
        month = int(m.group(2))
        day = int(m.group(3))
        parsed = _safe_date(year, month, day)
        if parsed:
            return parsed

    # 3) MonthName dd, yyyy
    for m in re.finditer(r"\b([A-Za-zñÑáéíóúÁÉÍÓÚ]{3,12})\s+([0-3]?\d),\s*((?:19|20)\d{2})\b", text):
        month_name = m.group(1).lower()
        if month_name not in MONTH_ALIASES:
            continue
        month = MONTH_ALIASES[month_name]
        day = int(m.group(2))
        year = int(m.group(3))
        parsed = _safe_date(year, month, day)
        if parsed:
            return parsed

    # 4) dd MonthName yyyy
    for m in re.finditer(r"\b([0-3]?\d)\s+([A-Za-zñÑáéíóúÁÉÍÓÚ]{3,12})\s+((?:19|20)\d{2})\b", text):
        day = int(m.group(1))
        month_name = m.group(2).lower()
        if month_name not in MONTH_ALIASES:
            continue
        month = MONTH_ALIASES[month_name]
        year = int(m.group(3))
        parsed = _safe_date(year, month, day)
        if parsed:
            return parsed

    return None


def month_number(issue_date: str | None, period: str | None = None) -> str:
    if issue_date and len(issue_date) >= 7:
        try:
            month = int(issue_date[5:7])
            return str(month)
        except ValueError:
            pass

    if period and re.match(r"^\d{4}\-\d{2}$", period):
        return str(int(period[5:7]))

    return ""
