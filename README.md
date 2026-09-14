# passport-filter

Filtro de imagen determinista que convierte una foto al estilo visual de
fotos de pasaporte ruso mal escaneadas/fotocopiadas: altísimo contraste,
silueta casi negra con una franja de brillo en el rostro, halftone,
ruido de escaneo y degradación por generaciones de copia.

No usa machine learning: es un pipeline de procesamiento de imagen tipo
filtro de Instagram, con cada paso implementado sobre Pillow/numpy.

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Para capturar desde cámara también hace falta el extra `camera`:

```bash
pip install -e ".[camera]"
```

## Uso

```bash
passport-filter --input foto.jpg --output resultado.jpg
passport-filter --camera --output resultado.jpg
```

Para superponer el patrón decorativo (paso opcional):

```bash
passport-filter --input foto.jpg --output resultado.jpg --pattern assets/patterns/guilloche.png
```

## Pipeline

1. Escala de grises
2. Curva de contraste sigmoide (`midpoint` fijo o calculado del histograma)
3. Dithering ordenado (Bayer 4x4)
4. Overlay opcional de un patrón decorativo (blend screen/multiply/overlay)
5. Ruido gaussiano (grano de escaneo)
6. Degradación por generaciones (downscale/upscale + recompresión JPEG en loop)
7. Blur + unsharp mask

## Tests

```bash
pytest
```
