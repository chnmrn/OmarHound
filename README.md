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

To use the desktop GUI, install the `gui` extra:

```bash
pip install -e ".[gui,camera]"
```

## Usage

```bash
passport-filter --input foto.jpg --output resultado.jpg
passport-filter --camera --output resultado.jpg
passport-filter --live
```

To overlay the decorative pattern (optional step):

```bash
passport-filter --input foto.jpg --output resultado.jpg --pattern src/passport_filter/assets/patterns/guilloche.png
```

There are also two generic "stamp" patterns (a crosshair seal and a fingerprint-like
texture, both procedurally generated — not real official symbols) that read better
with a stronger blend:

```bash
passport-filter --input foto.jpg --output resultado.jpg --pattern src/passport_filter/assets/patterns/stamp_crosshair.png --blend-mode screen --opacity 0.7
```

To auto-detect the face and center the pattern on it instead of stretching it across the whole photo, add `--center-on-face` (falls back to the static/stretched mode if no face is found):

```bash
passport-filter --input foto.jpg --output resultado.jpg --pattern src/passport_filter/assets/patterns/stamp_crosshair.png --blend-mode screen --opacity 0.7 --center-on-face
```

## Desktop app

A local desktop GUI wraps the same pipeline (no CLI needed): pick a photo or
use the camera, choose or upload a stamp pattern, adjust the blend/opacity/
face-centering, and save the result — all through a native window, no
internet or hosting involved.

```bash
passport-filter-gui
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
