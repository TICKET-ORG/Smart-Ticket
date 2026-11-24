/**
 * Gate scanner camera stage.
 *
 * The camera is a preview only. Capturing a frame does not upload anything and
 * does not produce a verdict: the page states that verification is not
 * connected and leaves the pass untouched. Do not add a match here until the
 * check-in endpoint returns a real result.
 */

export function initScanner() {
  const root = document.querySelector("[data-gate]");

  if (!root) {
    return;
  }

  const video = root.querySelector("[data-gate-video]");
  const placeholder = root.querySelector("[data-gate-placeholder]");
  const startButton = root.querySelector("[data-gate-start]");
  const captureButton = root.querySelector("[data-gate-capture]");
  const status = root.querySelector("[data-gate-status]");
  const notice = root.querySelector("[data-gate-notice]");

  if (!video || !startButton || !captureButton) {
    return;
  }

  let stream = null;

  const setStatus = (message, tone = "") => {
    if (!status) {
      return;
    }
    status.textContent = message;
    if (tone) {
      status.dataset.tone = tone;
    } else {
      delete status.dataset.tone;
    }
  };

  const stopStream = () => {
    stream?.getTracks().forEach((track) => track.stop());
    stream = null;
    video.srcObject = null;
    video.hidden = true;
    placeholder?.removeAttribute("hidden");
    captureButton.disabled = true;
  };

  const startCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus(
        "This browser cannot reach a camera. The scanner needs a browser with camera support on localhost or HTTPS.",
        "error",
      );
      return;
    }

    setStatus("Requesting camera access…");

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 960 },
          facingMode: "environment",
        },
        audio: false,
      });

      video.srcObject = stream;
      await video.play();

      video.hidden = false;
      placeholder?.setAttribute("hidden", "");
      startButton.hidden = true;
      captureButton.disabled = false;
      notice?.setAttribute("hidden", "");
      setStatus("Camera ready. Frame the holder, then capture one frame.", "ready");
    } catch (error) {
      stopStream();
      setStatus(friendlyCameraError(error), "error");
    }
  };

  const capture = () => {
    if (!stream) {
      return;
    }

    if (!video.videoWidth) {
      setStatus("The camera is still warming up. Try again in a moment.", "error");
      return;
    }

    // Deliberately no upload, no descriptor, and no verdict.
    captureButton.disabled = true;
    notice?.removeAttribute("hidden");
    notice?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    setStatus(
      "Frame captured locally. Verification is not connected, so no match was run.",
      "ready",
    );
  };

  startButton.addEventListener("click", startCamera);
  captureButton.addEventListener("click", capture);
  window.addEventListener("pagehide", stopStream);
}

function friendlyCameraError(error) {
  switch (error?.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Camera permission was denied. Allow access in the browser, then try again.";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "No camera was found on this device. The scanner needs a reader camera.";
    case "NotReadableError":
      return "The camera is busy in another app. Close it and try again.";
    default:
      return `Camera could not start: ${error?.message ?? "unknown error"}.`;
  }
}

initScanner();
