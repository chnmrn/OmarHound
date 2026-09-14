const state = {
  sourceDataUrl: null,
  sourceFile: null,
  selectedPatternPath: null,
  resultDataUrl: null,
  cameraStream: null,
};

const el = (id) => document.getElementById(id);

function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function setSourcePreview(dataUrl) {
  stopCamera();
  state.sourceDataUrl = dataUrl;
  el("source-preview").src = dataUrl;
  el("source-preview").hidden = false;
  el("source-empty").hidden = true;
  el("process-btn").disabled = false;
}

function showError(message) {
  const box = el("error-message");
  box.textContent = message;
  box.hidden = false;
}

function clearError() {
  el("error-message").hidden = true;
}

async function loadPatterns() {
  const response = await fetch("/api/patterns");
  const patterns = await response.json();
  renderPatternGrid(patterns);
}

function renderPatternGrid(patterns) {
  const grid = el("pattern-grid");
  grid.innerHTML = "";

  const noneTile = document.createElement("div");
  noneTile.className = "pattern-tile";
  noneTile.textContent = "Ninguno";
  noneTile.addEventListener("click", () => selectPattern(null, noneTile));
  grid.appendChild(noneTile);
  if (state.selectedPatternPath === null) {
    noneTile.classList.add("selected");
  }

  for (const pattern of patterns) {
    const tile = document.createElement("div");
    tile.className = "pattern-tile";
    if (pattern.path === state.selectedPatternPath) {
      tile.classList.add("selected");
    }
    tile.style.backgroundImage = `url(/api/patterns/thumbnail?path=${encodeURIComponent(pattern.path)})`;
    tile.title = pattern.name;
    tile.addEventListener("click", () => selectPattern(pattern.path, tile));

    if (pattern.source === "custom") {
      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "pattern-delete-btn";
      deleteBtn.textContent = "×";
      deleteBtn.title = "Borrar este patrón";
      deleteBtn.addEventListener("click", (event) => {
        event.stopPropagation();
        deletePattern(pattern.path);
      });
      tile.appendChild(deleteBtn);
    }

    grid.appendChild(tile);
  }
}

async function deletePattern(path) {
  if (!confirm("¿Borrar este patrón? No se puede deshacer.")) {
    return;
  }

  const response = await fetch(`/api/patterns?path=${encodeURIComponent(path)}`, { method: "DELETE" });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    showError(data.error || "No se pudo borrar el patrón");
    return;
  }

  if (state.selectedPatternPath === path) {
    state.selectedPatternPath = null;
    el("placement-choice").hidden = true;
  }
  await loadPatterns();
}

function selectPattern(path, tileEl) {
  state.selectedPatternPath = path;
  document.querySelectorAll(".pattern-tile").forEach((tile) => tile.classList.remove("selected"));
  tileEl.classList.add("selected");

  el("placement-choice").hidden = path === null;
  el("face-message").hidden = true;
}

async function uploadPattern(file) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch("/api/patterns/upload", { method: "POST", body: formData });
  if (!response.ok) {
    showError("No se pudo subir el patrón");
    return;
  }
  await loadPatterns();
}

async function useCamera() {
  clearError();
  try {
    state.cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
  } catch (err) {
    await captureFromBackendCamera();
    return;
  }

  const video = el("camera-video");
  video.srcObject = state.cameraStream;
  el("camera-live").hidden = false;
  el("source-preview").hidden = true;
  el("source-empty").hidden = true;
}

function stopCamera() {
  if (state.cameraStream) {
    state.cameraStream.getTracks().forEach((track) => track.stop());
    state.cameraStream = null;
  }
  el("camera-live").hidden = true;
}

function buildProcessFormData(photoDataUrl) {
  const centerOnFace = state.selectedPatternPath !== null && getPlacement() === "face";

  const formData = new FormData();
  formData.append("photo_data_url", photoDataUrl);
  formData.append("blend_mode", el("blend-mode").value);
  formData.append("opacity", el("opacity").value);
  formData.append("center_on_face", centerOnFace ? "true" : "false");
  if (state.selectedPatternPath) {
    formData.append("pattern_path", state.selectedPatternPath);
  }
  if (!el("midpoint-auto").checked) {
    formData.append("midpoint", el("midpoint-manual").value);
  }
  return formData;
}

function captureFromVideo() {
  const video = el("camera-video");
  const canvas = el("capture-canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  setSourcePreview(canvas.toDataURL("image/jpeg", 0.92));
}

async function captureFromBackendCamera() {
  const button = el("use-camera-btn");
  button.disabled = true;
  try {
    const response = await fetch("/api/camera/capture", { method: "POST" });
    const data = await response.json();
    if (!response.ok) {
      showError(data.error || "No se pudo acceder a la cámara");
      return;
    }
    setSourcePreview(data.image);
  } finally {
    button.disabled = false;
  }
}

function getPlacement() {
  const checked = document.querySelector('input[name="placement"]:checked');
  return checked ? checked.value : "background";
}

async function processImage() {
  clearError();
  if (!state.sourceDataUrl) {
    return;
  }

  el("process-btn").disabled = true;
  el("result-empty").hidden = true;
  el("result-preview").hidden = true;
  el("face-message").hidden = true;
  el("spinner").hidden = false;

  try {
    const response = await fetch("/api/process", {
      method: "POST",
      body: buildProcessFormData(state.sourceDataUrl),
    });
    const data = await response.json();
    if (!response.ok) {
      showError(data.error || "Ocurrió un error al procesar la imagen");
      return;
    }
    state.resultDataUrl = data.image;
    el("result-preview").src = data.image;
    el("result-preview").hidden = false;
    el("save-btn").disabled = false;

    if (data.face_message) {
      const msg = el("face-message");
      msg.textContent = data.face_message;
      msg.hidden = false;
    }
  } catch (err) {
    showError("Ocurrió un error al procesar la imagen");
  } finally {
    el("spinner").hidden = true;
    el("process-btn").disabled = false;
  }
}

async function saveResult() {
  if (!state.resultDataUrl || !window.pywebview) {
    return;
  }
  await window.pywebview.api.save_image(state.resultDataUrl, "resultado.jpg");
}

function init() {
  el("pick-file-btn").addEventListener("click", () => el("file-input").click());
  el("file-input").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    state.sourceFile = file;
    setSourcePreview(await fileToDataUrl(file));
  });

  el("use-camera-btn").addEventListener("click", useCamera);
  el("capture-btn").addEventListener("click", captureFromVideo);
  el("cancel-camera-btn").addEventListener("click", stopCamera);

  el("upload-pattern-btn").addEventListener("click", () => el("pattern-file-input").click());
  el("pattern-file-input").addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (file) uploadPattern(file);
  });

  el("opacity").addEventListener("input", (event) => {
    el("opacity-value").textContent = Number(event.target.value).toFixed(2);
  });

  el("midpoint-auto").addEventListener("change", (event) => {
    el("midpoint-manual").disabled = event.target.checked;
  });

  el("process-btn").addEventListener("click", processImage);
  el("save-btn").addEventListener("click", saveResult);

  loadPatterns();
}

init();
