/**
 * Guided face enrollment.
 *
 * Frames are drawn to a local canvas so the participant can confirm each pose.
 * Nothing is uploaded: there is no fetch, no descriptor, and no measurement in
 * this file. The final save button reports that the backend is not connected.
 */

const TARGET_SAMPLES = 9;

export function initEnrollment() {
  const root = document.querySelector("[data-enrollment]");

  if (!root) {
    return;
  }

  const video = root.querySelector("[data-camera-video]");
  const placeholder = root.querySelector("[data-camera-placeholder]");
  const startButton = root.querySelector("[data-camera-start]");
  const captureButton = root.querySelector("[data-camera-capture]");
  const resetButton = root.querySelector("[data-enrollment-reset]");
  const status = root.querySelector("[data-camera-status]");
  const countLabel = root.querySelector("[data-pose-count]");
  const poseLabel = root.querySelector("[data-pose-label]");
  const poseInstruction = root.querySelector("[data-pose-instruction]");
  const progress = root.querySelector("[data-progress]");
  const progressbar = root.querySelector("[data-progressbar]");
  const notice = root.querySelector("[data-enrollment-notice]");

  const rail = document.querySelector(".enroll-rail");
  const steps = Array.from(document.querySelectorAll("[data-pose]"));
  const consentPanel = rail?.querySelector("[data-consent]");
  const consentCheck = rail?.querySelector("[data-consent-check]");
  const saveButton = rail?.querySelector("[data-enrollment-save]");

  if (!video || !startButton || !captureButton || steps.length === 0) {
    return;
  }

  let stream = null;
  let current = 0;

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

  const updateProgress = () => {
    const percent = Math.round((current / TARGET_SAMPLES) * 100);
    if (progress) {
      progress.style.setProperty("--value", `${percent}%`);
    }
    if (progressbar) {
      progressbar.setAttribute("aria-valuenow", String(current));
    }
    if (countLabel) {
      countLabel.textContent = `${String(current).padStart(2, "0")} / ${String(
        TARGET_SAMPLES,
      ).padStart(2, "0")}`;
    }
  };

  const updatePose = () => {
    steps.forEach((step, index) => {
      step.classList.toggle("is-active", index === current);
    });

    if (current < steps.length) {
      const step = steps[current];
      if (poseLabel) {
        poseLabel.textContent = step.dataset.label ?? "";
      }
      if (poseInstruction) {
        poseInstruction.textContent = step.dataset.instruction ?? "";
      }
      captureButton.disabled = !stream;
      return;
    }

    if (poseLabel) {
      poseLabel.textContent = "All nine captured";
    }
    if (poseInstruction) {
      poseInstruction.textContent =
        "Review the samples, then confirm consent to save the profile.";
    }
    captureButton.disabled = true;
    consentPanel?.removeAttribute("hidden");
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
        "This browser cannot reach a camera. Enrollment needs a browser with camera support on localhost or HTTPS.",
        "error",
      );
      return;
    }

    setStatus("Requesting camera access…");

    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 960 },
          height: { ideal: 720 },
          facingMode: "user",
        },
        audio: false,
      });

      video.srcObject = stream;
      await video.play();

      video.hidden = false;
      placeholder?.setAttribute("hidden", "");
      startButton.hidden = true;
      captureButton.disabled = false;
      setStatus(
        "Camera ready. Hold still, then capture each pose in order.",
        "ready",
      );
      updatePose();
    } catch (error) {
      stopStream();
      setStatus(friendlyCameraError(error), "error");
    }
  };

  const capture = () => {
    if (!stream || current >= steps.length) {
      return;
    }

    if (!video.videoWidth) {
      setStatus("The camera is still warming up. Try again in a moment.", "error");
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const frame = canvas.toDataURL("image/jpeg", 0.85);
    const step = steps[current];
    const thumbnail = step.querySelector("[data-pose-thumb]");
    const state = step.querySelector("[data-pose-state]");

    if (thumbnail) {
      thumbnail.src = frame;
      thumbnail.alt = `Captured pose: ${step.dataset.label ?? ""}`;
      thumbnail.hidden = false;
    }

    if (state) {
      state.textContent = "Captured";
    }

    step.classList.remove("is-active");
    step.classList.add("is-done");

    current += 1;
    resetButton?.removeAttribute("hidden");
    notice?.setAttribute("hidden", "");
    updateProgress();
    updatePose();

    if (current >= TARGET_SAMPLES) {
      setStatus(
        "Nine frames captured in this tab. Nothing was uploaded.",
        "ready",
      );
    }
  };

  const reset = () => {
    current = 0;
    steps.forEach((step) => {
      step.classList.remove("is-done", "is-active");
      const thumbnail = step.querySelector("[data-pose-thumb]");
      const state = step.querySelector("[data-pose-state]");
      if (thumbnail) {
        thumbnail.removeAttribute("src");
        thumbnail.hidden = true;
      }
      if (state) {
        state.textContent = "Waiting";
      }
    });

    consentPanel?.setAttribute("hidden", "");
    if (consentCheck) {
      consentCheck.checked = false;
    }
    if (saveButton) {
      saveButton.disabled = true;
    }
    notice?.setAttribute("hidden", "");
    resetButton?.setAttribute("hidden", "");
    updateProgress();
    updatePose();
    setStatus(
      stream
        ? "Camera ready. Hold still, then capture each pose in order."
        : "Nothing leaves this browser. Start the camera to capture the nine poses.",
      stream ? "ready" : "",
    );
  };

  startButton.addEventListener("click", startCamera);
  captureButton.addEventListener("click", capture);
  resetButton?.addEventListener("click", reset);

  consentCheck?.addEventListener("change", () => {
    if (saveButton) {
      saveButton.disabled = !consentCheck.checked;
    }
  });

  saveButton?.addEventListener("click", () => {
    if (!consentCheck?.checked) {
      return;
    }
    notice?.removeAttribute("hidden");
    notice?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    saveButton.disabled = true;
    saveButton.textContent = "Not connected (demo)";
  });

  window.addEventListener("pagehide", stopStream);

  updateProgress();
  updatePose();
}

function friendlyCameraError(error) {
  switch (error?.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Camera permission was denied. Allow access in the browser, then try again.";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "No camera was found on this device. Enrollment needs a webcam.";
    case "NotReadableError":
      return "The camera is busy in another app. Close it and try again.";
    default:
      return `Camera could not start: ${error?.message ?? "unknown error"}.`;
  }
}

initEnrollment();
