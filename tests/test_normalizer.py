import pytest

from unificador.normalizer import FIXED, OK, REVIEW, normalize_code

PREFIXES = {"X": "XB", "Y": "YC"}


@pytest.mark.parametrize(
    "raw, expected, status",
    [
        ("XB111", "XB111", OK),
        ("xb111", "XB111", FIXED),
        ("xb-111", "XB111", FIXED),
        ("  XB 111 ", "XB111", FIXED),
        ("xb_111", "XB111", FIXED),
        ("x111", "XB111", FIXED),   # prefijo viejo -> tabla de equivalencias
        ("Y222", "YC222", FIXED),
    ],
)
def test_codigos_que_se_pueden_resolver(raw, expected, status):
    result = normalize_code(raw, PREFIXES)
    assert result.normalized == expected
    assert result.status == status


@pytest.mark.parametrize(
    "raw",
    [
        "",             # vacío
        None,           # sin dato
        "A333",         # prefijo sin equivalencia definida
        "q9",           # pocos dígitos: no se inventan ceros
        "x11",          # idem
        "ZZZ100",       # prefijo no válido
        "1234",         # sin letras
        "XB11A",        # formato raro
    ],
)
def test_casos_que_van_a_revision(raw):
    result = normalize_code(raw, PREFIXES)
    assert result.status == REVIEW
    assert result.normalized is None
