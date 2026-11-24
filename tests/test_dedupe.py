from unificador.dedupe import exact_duplicates, normalize_text, similar_descriptions


def row(code, desc):
    return {"original": code, "normalized": code, "description": desc}


def test_normalize_text_ignora_mayusculas_y_espacios_en_unidades():
    assert normalize_text("TORNILLO Hexagonal 5 MM") == normalize_text("tornillo hexagonal 5mm")


def test_mismo_codigo_se_agrupa():
    rows = [row("XB111", "a"), row("XB111", "b"), row("XB112", "c")]
    assert list(exact_duplicates(rows)) == ["XB111"]


def test_descripcion_parecida_con_codigo_distinto_se_detecta():
    rows = [row("XB115", "Tornillo allen 5 mm"), row("XB116", "Tornillo Allen 5mm")]
    assert len(similar_descriptions(rows)) == 1


def test_medidas_distintas_no_son_duplicados():
    rows = [row("XB111", "Tornillo hexagonal 5 mm"), row("XB112", "Tornillo hexagonal 6 mm")]
    assert similar_descriptions(rows) == []
