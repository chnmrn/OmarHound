import argparse
from pathlib import Path

from PIL import Image

from passport_filter.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="passport-filter",
        description="Convierte una foto al estilo pasaporte ruso mal fotocopiado",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Ruta a la imagen de entrada")
    source.add_argument("--camera", action="store_true", help="Captura desde la cámara")
    parser.add_argument("--output", type=Path, default=Path("output.jpg"), help="Ruta de salida")
    parser.add_argument(
        "--midpoint",
        type=float,
        default=None,
        help="Midpoint fijo de la curva de contraste (0.6-0.75). Si se omite, se calcula del histograma",
    )
    parser.add_argument("--pattern", type=Path, default=None, help="Ruta al patrón decorativo a superponer")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.camera:
        from passport_filter.camera import capture_frame

        image = capture_frame()
    else:
        image = Image.open(args.input)

    result = run_pipeline(image, midpoint=args.midpoint, pattern_path=args.pattern)
    result.save(args.output)


if __name__ == "__main__":
    main()
