# Unificador de códigos de producto

Herramienta en Python que toma un listado de productos con códigos inconsistentes
(`x111`, `xb-111`, `XB 111`...), los lleva a un formato único y detecta posibles
duplicados. Lo que no puede resolver con seguridad lo separa para revisión manual.

## El problema

En muchas empresas el mismo producto aparece con códigos escritos de distinta forma
o con prefijos de sistemas viejos. Unificarlos a mano es lento y propenso a errores.

## Formato canónico

2 letras mayúsculas + 3 dígitos, sin separadores. Ejemplo: `XB111`.

## Qué hace

1. **Normaliza** cada código con reglas explícitas:
   - saca espacios y separadores (`-`, `_`, `.`, `/`) y pasa a mayúsculas: `xb-111` → `XB111`
   - completa prefijos viejos de una letra con una tabla de equivalencias
     (`data/legacy_prefixes.csv`): `x111` → `XB111`
2. **Marca** cada registro: `OK` (ya estaba bien), `FIXED` (corregido por reglas) o
   `REVIEW` (requiere decisión humana).
3. **Detecta duplicados**: mismo código normalizado, y descripciones muy parecidas
   con códigos distintos.
4. **Genera reportes** en `output/`: `mapping.csv` (qué pasó con cada código),
   `review.csv` y `duplicates.csv`.

## Decisiones de diseño

- **No adivina.** Si el prefijo no tiene equivalencia definida (`A333`) o faltan
  dígitos (`q9`), no se inventa nada: va a `review.csv`. Un código mal unificado
  es peor que uno sin unificar.
- **Auditable.** `mapping.csv` guarda el código original, el resultado y el motivo
  de cada cambio, para poder revertir o explicar cualquier decisión.
- **Las medidas importan.** `Tornillo 5 mm` y `Tornillo 6 mm` son casi iguales como
  texto pero son productos distintos, así que si los números difieren no se marcan
  como duplicados.
- **Reglas en datos, no en código.** Las equivalencias de prefijos están en un CSV
  que puede editar quien conoce el catálogo.

## Cómo usarlo

```bash
pip install -r requirements.txt
python -m unificador data/sample_products.csv --out output
pytest
```

El CSV de entrada necesita las columnas `code` y `description`.

## Estructura

```
unificador/
  normalizer.py   reglas de normalización
  dedupe.py       detección de duplicados
  pipeline.py     lectura, proceso y reportes
  ai_suggest.py   paso 2 (a completar): sugerencias con IA para los casos en REVIEW
data/             datos de ejemplo y tabla de prefijos
tests/            pruebas automáticas
```

## Próximos pasos

- [ ] Sugerencias con IA para los registros en `REVIEW` (ver `ai_suggest.py`): el
      modelo propone, una persona aprueba.
- [ ] Leer Excel además de CSV.
- [ ] Interfaz simple para revisar y aprobar los casos en `REVIEW`.
