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
   (screen/multiply/overlay, `--blend-mode`) y opacidad configurable
   (`--opacity`, default 0.3) — `steps/overlay.py` ✅. Se activa solo si
   se pasa `--pattern <ruta>`; sin ese flag el paso se salta (sigue
   siendo opcional). Los assets viven **dentro del paquete**
   (`src/passport_filter/assets/patterns/`, resuelto vía
   `assets_dir.PATTERNS_DIR = Path(__file__).parent / ...`, no relativo
   al directorio desde donde se corre el programa — importante porque
   la GUI se lanza desde cualquier lado, no solo desde la raíz del
   repo), todos generados por código (nada descargado ni copiado de un
   documento real):
   - `guilloche.png` — patrón de fondo sutil (interferencia de
     senoidales, `scripts/generate_pattern.py`). Pensado para
     `--blend-mode multiply` con opacidad baja (default)
   - `stamp_crosshair.png` y `stamp_fingerprint.png` —
     "sellos" más marcados tipo el de las fotos de referencia del
     usuario, pero con símbolos genéricos (cruz/mira, huella) en vez
     del escudo real de Rusia o campos reales de pasaporte — decisión
     deliberada para no construir algo que funcione como plantilla de
     documento falso (`scripts/generate_stamp.py`). Se ven mejor con
     `--blend-mode screen --opacity 0.6-0.8` (resalta el patrón sobre
     las zonas oscuras de la silueta, no solo las claras)

   `--center-on-face` (opcional, no reemplaza el modo estático) detecta
   la cara con Haar cascade (`steps/face.py`, clasificador clásico
   incluido en OpenCV, no una red neuronal) y centra `--pattern` sobre
   la caja de la cara expandida un 40% (`expand_box`) en vez de
   estirarlo a toda la imagen. `overlay_pattern` acepta un `region`
   opcional para esto — fuera de esa región la imagen queda intacta
   (el valor "neutro" del blend mode se usa como relleno). Si no se
   detecta cara, cae de vuelta al modo estático automáticamente.
   **IMPORTANTE**: `opencv-python` está fijado a `<5` en `pyproject.toml`
   — la versión 5.0 sacó `cv2.CascadeClassifier` de los bindings de
   Python (lo reemplazaron por un detector DNN que requiere descargar
   un modelo `.onnx`, lo cual no queríamos)
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

### App de escritorio (`src/passport_filter/gui/`)
`passport-filter-gui` (extra `gui`: `flask` + `pywebview`) — ventana nativa
de escritorio (no una pestaña de navegador: `pywebview` renderiza HTML/CSS/JS
dentro de una ventana con su propio chrome de OS) que envuelve el mismo
`run_pipeline()`, sin tocar el pipeline en sí. Sin base de datos, sin
hosting, todo corre local (`server.py` levanta Flask en un thread en
`127.0.0.1:5173`, `app.py` abre la ventana apuntando ahí).

- `GET /api/patterns` — lista assets built-in (`assets_dir.PATTERNS_DIR`)
  + patrones subidos por el usuario (`~/.passport_filter/patterns/`, se
  crea si no existe)
- `POST /api/patterns/upload` — sube un patrón custom a esa carpeta
- `DELETE /api/patterns?path=<ruta>` — borra un patrón propio. Valida
  que la ruta esté dentro de `USER_PATTERNS_DIR` (nunca deja borrar
  algo de `PATTERNS_DIR`, los assets del proyecto). Botón "×" en la
  esquina de cada tile custom en la galería (`app.js`), con
  confirmación antes de borrar
- `POST /api/camera/capture` — llama a `camera.capture_frame()` (una foto)
- `POST /api/process` — recibe una foto (archivo subido o data-URL desde
  la cámara) + los mismos parámetros que el CLI (`pattern_path`,
  `blend_mode`, `opacity`, `midpoint`, `center_on_face`), corre
  `run_pipeline()` y devuelve el resultado como data-URL
- "Guardar imagen" no es una descarga de navegador: usa el puente
  `js_api` de pywebview (`Api.save_image` en `app.py`) para abrir el
  diálogo nativo "Guardar como" de Windows
- Cámara en vivo (`app.js`): usa `navigator.mediaDevices.getUserMedia`
  directo en el frontend (la ventana de pywebview es un navegador
  embebido — WebView2/Edge — así que esto funciona nativamente, sin
  tocar Python) en vez de streamear frames desde `cv2`. Muestra el
  video, el usuario ve lo que la cámara ve y aprieta "Capturar" para
  tomar el frame actual a un `<canvas>`. Si `getUserMedia` falla
  (permiso denegado, no soportado), cae de vuelta automáticamente al
  endpoint viejo `/api/camera/capture` (una sola foto vía
  `camera.capture_frame()`) — no se sacó ese endpoint, queda como
  fallback
- Se probó y se sacó un modo de "filtro en vivo" sobre la cámara (poll
  a `/api/process` cada 500ms con el frame actual). El usuario pidió
  quitarlo por ahora para hacer pruebas de fotos primero; si se retoma
  más adelante, la idea era esa — reusar `/api/process` sin tocar el
  backend, solo pollear desde el frontend
- "¿Dónde va el patrón?" (fondo vs. cara) ahora es una elección
  explícita al lado de la galería de patrones, no un checkbox suelto en
  Ajustes — se ocultaba y la gente no lo encontraba. Si se elige "cara"
  y no se detecta ninguna, el backend igual corre en modo fondo pero
  ahora **avisa por qué** (`face_message` en la respuesta de
  `/api/process`, llama a `detect_face_box` una vez más solo para el
  mensaje — sí, corre la detección dos veces en ese caso, aceptable
  porque es un click de botón, no un stream por frame)
- Interfaz traducida a inglés (por el usuario, directo en el HTML) y
  luego rediseñada con paleta "expediente clasificado" (papel crema,
  tinta oscura, acento rojo sello, monoespaciada, marcas de esquina en
  las esquinas de los paneles, headers numerados 01/02/03/04 tipo
  campo de formulario) — inspirado en una referencia visual del
  usuario, pero sin copiar nombres/logo de la marca de la que viene esa
  referencia (era el estilo de documentos in-game de un videojuego).
  Tarjetas de patrones ahora son miniatura + etiqueta con nombre (antes
  solo la imagen pelada con tooltip), con íconos SVG inline en todos
  los botones (subir, cámara, capturar, generar, guardar) — sin
  dependencias externas ni CDN, todo dibujado a mano en el HTML/JS para
  que la app funcione 100% offline
- Bug encontrado durante la revisión visual: `.preview { display: block }`
  le ganaba al atributo `hidden` de los `<img>` de origen/resultado, así
  que se veían íconos de "imagen rota" antes de subir/generar algo
  (bug preexistente al rediseño, no introducido por él). Fix: regla
  global `[hidden] { display: none !important; }` al tope de
  `style.css`
- De paso se tradujeron al inglés los strings que habían quedado en
  español en `app.js` y `server.py` (mensajes de error, confirmación de
  borrado, `face_message`), para consistencia con el resto de la UI ya
  traducida

Probado con Flask test client (`tests/test_gui.py`, sin servidor/ventana
real) y con una corrida real de la ventana en este entorno — cargó la
página, el CSS/JS y la lista de patrones correctamente. **No probado
todavía**: subir un patrón propio, capturar con cámara real, ni el botón
de guardar (necesitan hardware/diálogos nativos que no existen en este
entorno de desarrollo).

Si más adelante se quiere compartir con alguien sin Python instalado,
empaquetar con PyInstaller (`passport-filter-gui` como entry point) —
no implementado todavía.

## Pendiente / lo que se quiere explorar ahora
- Probar el pipeline completo con fotos reales, no solo sintéticas
  (`detect_face_box` tampoco se probó con una cara real todavía — solo
  con la imagen sintética, donde correctamente no detecta nada)
- Posible port a JavaScript para una demo web
- El modo `--live` corre el pipeline completo (incluida la degradación
  JPEG en loop, y ahora potencialmente detección de cara) por frame; si
  se ve lento en cámara real, considerar un pipeline "ligero" para
  preview (menos generaciones de degradación, o no correr detección de
  cara en cada frame sino cada N frames)
