import argparse

from .pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Unifica códigos de producto.")
    parser.add_argument("input", help="CSV con columnas: code, description")
    parser.add_argument("--prefixes", default="data/legacy_prefixes.csv", help="CSV con columnas: legacy, canonical")
    parser.add_argument("--out", default="output", help="carpeta de salida")
    parser.add_argument("--ai", action="store_true", help="pedir sugerencias a Gemini para los casos en REVIEW")
    parser.add_argument("--max-ai", type=int, default=10, help="máximo de filas a enviar a la IA")

    args = parser.parse_args()

    stats = run(args.input, args.prefixes, args.out, use_ai=args.ai, max_ai=args.max_ai)


    print(f"Total de registros:            {stats['total']}")
    print(f"Ya correctos (OK):             {stats['ok']}")
    print(f"Corregidos por reglas (FIXED): {stats['fixed']}")
    print(f"A revisar a mano (REVIEW):     {stats['review']}")
    print(f"Grupos con el mismo código:    {stats['grupos_mismo_codigo']}")
    print(f"Pares de descripción parecida: {stats['pares_descripcion_parecida']}")
    print(f"Reportes en: {args.out}/")

    if args.ai:
        print(f"Sugeridos por IA:              {stats['sugeridos_ia']}")

if __name__ == "__main__":
    main()
