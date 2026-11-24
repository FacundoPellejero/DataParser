"""Detección de posibles duplicados: por código exacto y por descripción parecida."""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher

NUMBER = re.compile(r"\d+(?:[.,]\d+)?")


def normalize_text(text: str) -> str:
    """Minúsculas, sin tildes ni signos; '5 mm' y '5mm' quedan iguales."""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9\s.,]", " ", text)
    text = re.sub(r"(\d)\s+([a-z]+)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def numbers_in(text: str) -> tuple[str, ...]:
    return tuple(NUMBER.findall(text))


def exact_duplicates(rows: list[dict]) -> dict[str, list[dict]]:
    """Agrupa filas que quedaron con el mismo código normalizado."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["normalized"]:
            groups[row["normalized"]].append(row)
    return {code: items for code, items in groups.items() if len(items) > 1}


def similar_descriptions(rows: list[dict], threshold: float = 0.88) -> list[tuple[dict, dict, float]]:
    """Pares con códigos distintos y descripciones muy parecidas.

    Si los números difieren (ej.: '5 mm' vs '6 mm'), NO se consideran duplicados:
    una descripción casi igual pero con otra medida es otro producto.
    """
    candidates = [r for r in rows if r["normalized"] and r["description"].strip()]
    prepared = [(r, normalize_text(r["description"])) for r in candidates]
    pairs: list[tuple[dict, dict, float]] = []
    for i in range(len(prepared)):
        for j in range(i + 1, len(prepared)):
            (a, ta), (b, tb) = prepared[i], prepared[j]
            if a["normalized"] == b["normalized"]:
                continue  # ya lo cubre exact_duplicates
            if numbers_in(ta) != numbers_in(tb):
                continue
            ratio = SequenceMatcher(None, ta, tb).ratio()
            if ratio >= threshold:
                pairs.append((a, b, round(ratio, 2)))
    return pairs
