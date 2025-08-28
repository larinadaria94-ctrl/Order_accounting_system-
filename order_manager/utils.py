from __future__ import annotations
import re
from datetime import datetime
from typing import Any, Callable, List

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email or ""))


def validate_phone(phone: str) -> bool:
    return bool(PHONE_RE.match(phone or ""))


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def merge_sort(items: List[Any], key: Callable[[Any], Any], reverse: bool = False) -> List[Any]:
    n = len(items)
    if n <= 1:
        return items[:]
    mid = n // 2
    left = merge_sort(items[:mid], key=key, reverse=reverse)
    right = merge_sort(items[mid:], key=key, reverse=reverse)

    # слияние
    res = []
    i = j = 0
    cmp = (lambda a, b: key(a) > key(b)) if reverse else (lambda a, b: key(a) < key(b))
    while i < len(left) and j < len(right):
        if cmp(left[i], right[j]):
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res


def now_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")
