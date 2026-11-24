"""Reglas para llevar un código de producto al formato canónico.

Formato canónico: 2 letras mayúsculas + 3 dígitos, sin separadores (ej.: XB111).

Principio de diseño: la herramienta nunca adivina. Si una regla no alcanza para
llegar a un código válido con seguridad, el registro queda en REVIEW para que
lo resuelva una persona.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

CANONICAL = re.compile(r"^[A-Z]{2}\d{3}$")
LETTERS_DIGITS = re.compile(r"^([A-Z]+)(\d+)$")
SEPARATORS = re.compile(r"[\s\-_./]+")

OK = "OK"          # ya estaba en formato canónico, sin cambios
FIXED = "FIXED"    # se corrigió aplicando reglas
REVIEW = "REVIEW"  # no se pudo resolver con seguridad: revisión manual


@dataclass(frozen=True)
class Result:
    original: str
    normalized: str | None
    status: str
    reason: str


def load_prefix_map(path: str | Path) -> dict[str, str]:
    """Carga la tabla de equivalencias de prefijos viejos (ej.: X -> XB)."""
    with open(path, newline="", encoding="utf-8") as f:
        return {
            row["legacy"].strip().upper(): row["canonical"].strip().upper()
            for row in csv.DictReader(f)
        }


def normalize_code(raw: str | None, prefix_map: dict[str, str]) -> Result:
    original = raw if raw is not None else ""

    # Regla 1: sacar separadores y espacios, pasar a mayúsculas.
    cleaned = SEPARATORS.sub("", original).upper()
    if not cleaned:
        return Result(original, None, REVIEW, "código vacío")

    # Si con solo limpiar ya es válido, listo.
    if CANONICAL.match(cleaned):
        if cleaned == original:
            return Result(original, cleaned, OK, "ya tenía el formato correcto")
        return Result(original, cleaned, FIXED, "se corrigieron mayúsculas, espacios o separadores")

    parts = LETTERS_DIGITS.match(cleaned)
    if not parts:
        return Result(original, None, REVIEW, "formato no reconocido (se esperan letras y luego números)")
    letters, digits = parts.groups()

    # Regla 2: no inventamos dígitos (ej.: no completamos con ceros).
    if len(digits) != 3:
        return Result(original, None, REVIEW, f"se esperaban 3 dígitos y hay {len(digits)}")

    # Regla 3: prefijo de una letra -> se completa con la tabla de equivalencias.
    if len(letters) == 1:
        canonical_prefix = prefix_map.get(letters)
        if canonical_prefix is None:
            return Result(original, None, REVIEW, f"el prefijo '{letters}' no tiene equivalencia definida")
        return Result(
            original,
            canonical_prefix + digits,
            FIXED,
            f"prefijo {letters} -> {canonical_prefix} (tabla de equivalencias)",
        )

    return Result(original, None, REVIEW, f"prefijo '{letters}' no válido")
