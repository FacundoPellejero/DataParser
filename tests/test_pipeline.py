import csv

from unificador.pipeline import run


def test_pipeline_genera_reportes(tmp_path):
    stats = run("data/sample_products.csv", "data/legacy_prefixes.csv", tmp_path)
    assert stats["total"] == 22
    assert stats["review"] > 0
    for name in ("mapping.csv", "review.csv", "duplicates.csv"):
        assert (tmp_path / name).exists()
    with open(tmp_path / "mapping.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == stats["total"]
