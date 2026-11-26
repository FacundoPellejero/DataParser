"""Sugerencias con IA para los registros en REVIEW (el modelo propone, una persona decide)."""
from __future__ import annotations

import json
import re
from typing import Callable

from .normalizer import CANONICAL

PROMPT_TEMPLATE = """Sos un asistente que ayuda a unificar códigos de producto.
Formato válido: 2 letras mayúsculas + 3 dígitos (ejemplo: XB111).
Prefijos válidos: {valid_prefixes}.
Ejemplos ya resueltos: {examples}.

Código original: {code}
Descripción: {description}

Respondé solo con JSON: {{"sugerencia": "...", "confianza": 0.0, "motivo": "..."}}.
Si no hay forma de saberlo con seguridad, devolvé "sugerencia": null."""


def parse_suggestion(raw: str, valid_prefixes: set[str]) -> dict | None:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    code = data.get("sugerencia")
    if not isinstance(code, str) or not CANONICAL.match(code):
        return None
    if code[:2] not in valid_prefixes:
        return None
    return {"sugerencia": code,
            "confianza": data.get("confianza"),
            "motivo": data.get("motivo", "")}


def suggest_for_review(
    review_rows: list[dict],
    valid_prefixes: list[str],
    examples: list[tuple[str, str]],
    call_model: Callable[[str], str],
) -> list[dict]:
    """Pide una sugerencia por cada fila en REVIEW y devuelve una lista de resultados."""
    prefixes_text = ", ".join(valid_prefixes)
    examples_text = "; ".join(f"{code}: {desc}" for code, desc in examples)
    valid = set(valid_prefixes)

    results = []
    for row in review_rows:
        code = (row.get("original") or "").strip()
        description = (row.get("description") or "").strip()
        if not code and not description:
            continue  # no hay nada para sugerir

        prompt = PROMPT_TEMPLATE.format(
            valid_prefixes=prefixes_text,
            examples=examples_text,
            code=code,
            description=description,
        )
        raw = call_model(prompt) or ""   # si el modelo devuelve None, usamos texto vacío
        suggestion = parse_suggestion(raw, valid)

        results.append({
            "original": code,
            "description": description,
            "sugerencia": suggestion["sugerencia"] if suggestion else None,
            "confianza": suggestion["confianza"] if suggestion else None,
            "motivo": suggestion["motivo"] if suggestion else "",
            "respuesta_cruda": raw,
            "estado": "SUGERIDO_IA" if suggestion else "SIN_SUGERENCIA",
        })
    return results