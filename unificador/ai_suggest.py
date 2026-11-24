"""PASO 2 (a completar): sugerencias con IA para los registros en REVIEW.

La idea: las reglas resuelven lo seguro; para lo ambiguo (ej.: el prefijo 'A' no tiene
equivalencia única) se le pide a un modelo una SUGERENCIA, nunca una decisión.

Diseño propuesto:
  - Entrada: filas de review.csv (código original, descripción) + lista de prefijos válidos
    + algunos ejemplos ya resueltos (los FIXED) como contexto.
  - Pedir al modelo una respuesta en JSON: {"sugerencia": "AB333", "confianza": 0-1, "motivo": "..."}.
  - Validar SIEMPRE la respuesta con el mismo formato canónico (normalizer.CANONICAL).
  - Guardar el resultado como 'SUGERIDO_IA' en un archivo aparte, para aprobación humana.
  - Probar con una función falsa (mock) en los tests, sin llamar a ninguna API.
"""
from __future__ import annotations

from typing import Callable

PROMPT_TEMPLATE = """Sos un asistente que ayuda a unificar códigos de producto.
Formato válido: 2 letras mayúsculas + 3 dígitos (ejemplo: XB111).
Prefijos válidos: {valid_prefixes}.
Ejemplos ya resueltos: {examples}.

Código original: {code}
Descripción: {description}

Respondé solo con JSON: {{"sugerencia": "...", "confianza": 0.0, "motivo": "..."}}.
Si no hay forma de saberlo con seguridad, devolvé "sugerencia": null."""


def suggest_for_review(
    review_rows: list[dict],
    valid_prefixes: list[str],
    examples: list[tuple[str, str]],
    call_model: Callable[[str], str],
) -> list[dict]:
    """TODO: armar el prompt por fila, llamar a call_model, parsear el JSON y validar la sugerencia."""
    raise NotImplementedError("Completar este paso: es la parte de IA del proyecto.")
