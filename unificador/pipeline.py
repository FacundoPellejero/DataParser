"""Lee un CSV (code, description), normaliza, detecta duplicados y escribe los reportes."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from .dedupe import exact_duplicates, similar_descriptions
from .normalizer import REVIEW, load_prefix_map, normalize_code


def _write(path: Path, header: list[str], rows: list[list]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def run(input_path: str | Path, prefixes_path: str | Path, out_dir: str | Path,
        use_ai: bool = False, max_ai: int = 10) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    prefix_map = load_prefix_map(prefixes_path)

    rows: list[dict] = []
    with open(input_path, newline="", encoding="utf-8") as f:
        for line in csv.DictReader(f):
            result = normalize_code(line["code"], prefix_map)
            rows.append(
                {
                    "original": result.original,
                    "normalized": result.normalized,
                    "status": result.status,
                    "reason": result.reason,
                    "description": line.get("description", ""),
                }
            )

    # 1) Mapa completo: qué pasó con cada código (auditoría).
    _write(
        out / "mapping.csv",
        ["original", "normalizado", "estado", "motivo", "descripcion"],
        [[r["original"], r["normalized"] or "", r["status"], r["reason"], r["description"]] for r in rows],
    )

    # 2) Lo que requiere decisión humana.
    review = [r for r in rows if r["status"] == REVIEW]
    _write(
        out / "review.csv",
        ["original", "motivo", "descripcion"],
        [[r["original"], r["reason"], r["description"]] for r in review],
    )

    # 3) Duplicados: mismo código normalizado, y descripciones parecidas con códigos distintos.
    dup_rows: list[list] = []
    exact = exact_duplicates(rows)
    for code, items in exact.items():
        for r in items:
            dup_rows.append(["mismo_codigo", code, r["original"], r["description"], ""])
    similar = similar_descriptions(rows)
    for a, b, ratio in similar:
        dup_rows.append(["descripcion_parecida", a["normalized"], a["original"], a["description"], ratio])
        dup_rows.append(["descripcion_parecida", b["normalized"], b["original"], b["description"], ratio])
    _write(
        out / "duplicates.csv",
        ["tipo", "codigo_normalizado", "original", "descripcion", "similitud"],
        dup_rows,
    )

    ai_count = 0
    if use_ai:
        import time
        from .ai_suggest import suggest_for_review
        from .providers import gemini_call

        valid_prefixes = sorted(
            {r["normalized"][:2] for r in rows if r["normalized"]}
            | set(prefix_map.values())
        )
        examples = [(r["normalized"], r["description"]) for r in rows if r["normalized"]][:30]

        def paced_call(prompt):
            time.sleep(1)  # pausa para no pasarse de los límites del nivel gratuito
            return gemini_call(prompt)

        suggestions = suggest_for_review(review[:max_ai], valid_prefixes, examples, paced_call)
        _write(
            out / "suggested.csv",
            ["original", "descripcion", "sugerencia", "confianza", "motivo", "estado"],
            [[s["original"], s["description"], s["sugerencia"] or "", s["confianza"] or "",
              s["motivo"], s["estado"]] for s in suggestions],
        )
        ai_count = sum(1 for s in suggestions if s["estado"] == "SUGERIDO_IA")

    counts = Counter(r["status"] for r in rows)
    return {
        "total": len(rows),
        "ok": counts.get("OK", 0),
        "fixed": counts.get("FIXED", 0),
        "review": counts.get("REVIEW", 0),
        "grupos_mismo_codigo": len(exact),
        "pares_descripcion_parecida": len(similar),
        "sugeridos_ia": ai_count,
    }
