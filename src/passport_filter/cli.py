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
    source.add_argument(
        "--live",
        action="store_true",
        help="Vista en vivo desde la cámara con el efecto aplicado en tiempo real (ventana OpenCV, ESC para salir)",
    )
    parser.add_argument("--output", type=Path, default=Path("output.jpg"), help="Ruta de salida (ignorado con --live)")
    parser.add_argument(
        "--midpoint",
        type=float,
        default=None,
        help="Midpoint fijo de la curva de contraste (0.6-0.75). Si se omite, se calcula del histograma",
    )
    parser.add_argument("--pattern", type=Path, default=None, help="Ruta al patrón decorativo a superponer")
    parser.add_argument(
        "--blend-mode",
        choices=["multiply", "screen", "overlay"],
        default="multiply",
        help="Cómo se mezcla --pattern con la foto (default: multiply, sutil; screen resalta el patrón sobre las zonas oscuras, mejor para un sello marcado)",
    )
    parser.add_argument("--opacity", type=float, default=0.3, help="Intensidad de --pattern, de 0 a 1 (default: 0.3)")
    parser.add_argument(
        "--center-on-face",
        action="store_true",
        help="Detecta la cara y centra --pattern sobre ella en vez de estirarlo a toda la imagen. "
        "Si no se detecta ninguna cara, cae de vuelta al modo estático",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.live:
        from passport_filter.live import run_live_preview

        run_live_preview(
            midpoint=args.midpoint,
            pattern_path=args.pattern,
            blend_mode=args.blend_mode,
            opacity=args.opacity,
            center_pattern_on_face=args.center_on_face,
        )
        return

    if args.camera:
        from passport_filter.camera import capture_frame

        image = capture_frame()
    else:
        image = Image.open(args.input)

    result = run_pipeline(
        image,
        midpoint=args.midpoint,
        pattern_path=args.pattern,
        blend_mode=args.blend_mode,
        opacity=args.opacity,
        center_pattern_on_face=args.center_on_face,
    )
    result.save(args.output)


if __name__ == "__main__":
    main()
