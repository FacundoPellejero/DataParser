from unificador.ai_suggest import suggest_for_review


def modelo_que_responde(texto):
    return lambda prompt: texto



def test_sugerencia_valida():
    respuesta = '{"sugerencia": "AB333", "confianza": 0.9, "motivo": "familia de arandelas"}'
    rows = [{"original": "A333", "description": "Arandela plana 8 mm"}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde(respuesta))
    assert result[0]["estado"] == "SUGERIDO_IA"
    assert result[0]["sugerencia"] == "AB333"


def test_sugerencia_invalida():
    respuesta = '{"sugerencia": "AB33", "confianza": 0.9, "motivo": "familia de arandelas"}'
    rows = [{"original": "A333", "description": "Arandela plana 8 mm"}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde(respuesta))
    assert result[0]["estado"] == "SIN_SUGERENCIA"
    assert result[0]["sugerencia"] is None


def test_sugerencia_fuera_lista():
    respuesta = '{"sugerencia": "ZZ333", "confianza": 0.9, "motivo": "x"}'
    rows = [{"original": "A333", "description": "Arandela plana 8 mm"}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde(respuesta))
    assert result[0]["estado"] == "SIN_SUGERENCIA"
    assert result[0]["sugerencia"] is None


def test_codigo_vacio():
    rows = [{"original": "", "description": ""}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde("no sé"))
    assert result == []

    
def test_respuesta_no_json():
    rows = [{"original": "A333", "description": "Arandela plana 8 mm"}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde("no sé"))
    assert result[0]["estado"] == "SIN_SUGERENCIA"
    assert result[0]["sugerencia"] is None

def test_sugerencia_null():
    
    respuesta = '{"sugerencia": null, "confianza": 0.0, "motivo": "no se puede saber"}'
    rows = [{"original": "A333", "description": "Arandela plana 8 mm"}]
    result = suggest_for_review(rows, ["AB", "XB"], [("AB334", "Arandela plana 10 mm")], modelo_que_responde(respuesta))
    assert result[0]["estado"] == "SIN_SUGERENCIA"
    assert result[0]["sugerencia"] is None