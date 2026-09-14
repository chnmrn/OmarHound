# Proyecto: filtro estilo "pasaporte distorsionado / fotocopia mala"

## Objetivo
Programa que toma una foto (de archivo o de la cámara) y la convierte al
estilo visual de fotos de pasaporte ruso mal escaneadas/fotocopiadas:
altísimo contraste, cabeza casi toda negra con solo una franja de brillo
en el centro del rostro, textura de tramado (halftone), ruido de escaneo,
y en algunos ejemplos el patrón decorativo del documento "sangrando"
sobre el rostro.

## Decisión de enfoque (ya tomada, no hace falta re-evaluar)
NO se entrena ningún modelo de ML. Es un pipeline determinista de
procesamiento de imagen, tipo filtro de Instagram: más rápido de construir,
más controlable, más predecible que un enfoque de style transfer/GAN.

## Decisión de lenguaje (ya tomada)
Python para el prototipo, por la madurez de Pillow/numpy/OpenCV para
manipulación de píxeles y dithering. C# (ImageSharp) y JavaScript
(Canvas API) se consideraron; JS sería la opción natural más adelante
si se quiere una demo web compartible sin instalar nada.

## Estado actual
Paquete instalable en `src/passport_filter/` (layout `src/`, `pip install -e .`),
con cada paso del pipeline como módulo independiente en `steps/` y tests en
`tests/` (pytest). Pipeline orquestado por `pipeline.run_pipeline`, en orden:

1. Escala de grises — `steps/grayscale.py` ✅
2. Curva de contraste sigmoide — `steps/contrast.py` ✅. `midpoint` se
   calcula automáticamente por umbral de Otsu sobre el histograma
   (`auto_midpoint`), clampeado a [0.55, 0.8] para mantener el look de
   "silueta casi negra con una franja de luz"; también se puede fijar
   manualmente con `--midpoint`
3. Dithering ordenado (matriz de Bayer 4x4) — `steps/dithering.py` ✅
4. Overlay opcional de un patrón/textura con blend modes
   (screen/multiply/overlay) — `steps/overlay.py` ✅. El asset es un
   patrón guilloché genérico generado por código (interferencia de
   senoidales, `scripts/generate_pattern.py` →
   `assets/patterns/guilloche.png`), no una reproducción de un
   documento real. Se activa solo si se pasa `--pattern <ruta>`; sin
   ese flag el paso se salta (sigue siendo opcional)
5. Ruido gaussiano (grano de escaneo) — `steps/noise.py` ✅
6. Degradación por generaciones: downscale/upscale + recompresión JPEG
   en loop, simula fotocopia de una fotocopia — `steps/degradation.py` ✅
7. Blur + unsharp mask (efecto de tinta "corrida") — `steps/sharpen.py` ✅

CLI (`passport-filter` / `python -m passport_filter`) soporta `--input <ruta>`,
`--camera` (una sola foto) o `--live` (ventana OpenCV en loop, efecto aplicado
en tiempo real, ESC para salir — `live.py`). Los tres requieren el extra
`opencv-python` salvo `--input`, `pip install -e ".[camera]"`.
`camera.py` usa `cv2.VideoCapture(0, cv2.CAP_DSHOW)` — el backend por defecto
de OpenCV en Windows (MSMF) suele fallar o colgarse para abrir la cámara.

Probado con imágenes sintéticas generadas por código (gradiente radial en
`examples/`, gitignoreado) para validar que el pipeline funciona; falta
probar con fotos reales.

## Pendiente / lo que se quiere explorar ahora
- Probar el pipeline completo con fotos reales, no solo sintéticas
- Posible port a JavaScript para una demo web
- El modo `--live` corre el pipeline completo (incluida la degradación
  JPEG en loop) por frame; si se ve lento en cámara real, considerar un
  pipeline "ligero" para preview (menos generaciones de degradación)
- Antes de subir a GitHub: completar el nombre real en `LICENSE` (hoy
  tiene el placeholder `[TU NOMBRE]`)
