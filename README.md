# passport-filter (Omar Hound style)

Deterministic image filter that transforms a photo into the visual style of poorly scanned/photocopied Russian passport photos: extremely high contrast, an almost-black silhouette with a bright band across the face, halftone, scan noise, and degradation from multiple generations of copying.

It does not use machine learning: it is an image-processing pipeline similar to an Instagram filter, with each step implemented using Pillow/numpy.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

To capture from a camera, the `camera` extra is also required:

```bash
pip install -e ".[camera]"
```

## Usage

```bash
passport-filter --input foto.jpg --output resultado.jpg
passport-filter --camera --output resultado.jpg
```

To overlay the decorative pattern (optional step):

```bash
passport-filter --input foto.jpg --output resultado.jpg --pattern assets/patterns/guilloche.png
```

## Pipeline

1. Grayscale conversion
2. Sigmoid contrast curve (`midpoint` fixed or calculated from the histogram)
3. Ordered dithering (4x4 Bayer)
4. Optional decorative pattern overlay (screen/multiply/overlay blend)
5. Gaussian noise (scan grain)
6. Generational degradation (downscale/upscale + JPEG recompression in a loop)
7. Blur + unsharp mask

## Tests

```bash
pytest
```
