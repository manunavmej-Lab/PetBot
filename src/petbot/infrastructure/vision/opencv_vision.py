from __future__ import annotations

from pathlib import Path
from typing import Any

from petbot.domain.events import EventType, PerceptionEvent


class OpenCVCamera:
    def __init__(self, device_index: int = 0) -> None:
        cv2 = _load_cv2()
        self._cv2 = cv2
        self._capture = cv2.VideoCapture(device_index)
        self._preview_enabled = False
        self._preview_window = "Buvi — vista de cámara (desarrollo)"
        self._latest_jpeg: bytes | None = None
        if not self._capture.isOpened():
            raise RuntimeError("No se pudo abrir la cámara. Revisa el permiso de cámara de macOS.")

    def capture_frame(self) -> Any:
        ok, frame = self._capture.read()
        if not ok:
            raise RuntimeError("No se pudo capturar una imagen de la cámara.")
        encoded, jpeg = self._cv2.imencode(".jpg", frame)
        if encoded:
            self._latest_jpeg = jpeg.tobytes()
        return frame

    @property
    def latest_jpeg(self) -> bytes | None:
        return self._latest_jpeg

    def close(self) -> None:
        self._capture.release()
        try:
            self._cv2.destroyWindow(self._preview_window)
        except self._cv2.error:
            pass

    def set_preview_enabled(self, enabled: bool) -> None:
        self._preview_enabled = enabled
        if not enabled:
            try:
                self._cv2.destroyWindow(self._preview_window)
            except self._cv2.error:
                pass

    def show_preview(self, frame: Any, faces: list[tuple[int, int, int, int]]) -> None:
        if not self._preview_enabled:
            return
        preview = frame.copy()
        for x, y, width, height in faces:
            self._cv2.rectangle(preview, (x, y), (x + width, y + height), (0, 190, 255), 2)
            self._cv2.putText(preview, "Cara detectada", (x, max(24, y - 10)), self._cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 190, 255), 2)
        self._cv2.imshow(self._preview_window, preview)
        self._cv2.waitKey(1)


class OpenCVVisionDetector:
    def __init__(self) -> None:
        cv2 = _load_cv2()
        self._cv2 = cv2
        models = Path("models/vision")
        detector_model = models / "face_detection_yunet_2023mar.onnx"
        recognizer_model = models / "face_recognition_sface_2021dec.onnx"
        if not detector_model.is_file() or not recognizer_model.is_file():
            raise RuntimeError("Faltan los modelos locales de reconocimiento facial en models/vision.")
        try:
            self._face_detector = cv2.FaceDetectorYN.create(str(detector_model), "", (320, 320), 0.9, 0.3, 5000)
            self._face_recognizer = cv2.FaceRecognizerSF.create(str(recognizer_model), "")
        except AttributeError as error:
            raise RuntimeError("Tu versión de OpenCV no incluye reconocimiento facial. Reinstala las dependencias de visión.") from error
        self._person_was_visible = False
        self.last_embedding: list[float] | None = None
        self.last_embeddings: list[list[float]] = []
        self.last_faces: list[tuple[int, int, int, int]] = []

    def detect(self, frame: Any) -> list[PerceptionEvent]:
        height, width = frame.shape[:2]
        self._face_detector.setInputSize((width, height))
        _, faces = self._face_detector.detect(frame)
        person_visible = faces is not None and len(faces) > 0
        self.last_embedding = None
        self.last_embeddings = []
        self.last_faces = []
        events: list[PerceptionEvent] = []
        if person_visible:
            for face in faces:
                x, y, face_width, face_height = (int(value) for value in face[:4])
                self.last_faces.append((x, y, face_width, face_height))
                aligned_face = self._face_recognizer.alignCrop(frame, face)
                self.last_embeddings.append(self._face_recognizer.feature(aligned_face).flatten().tolist())
            self.last_embedding = self.last_embeddings[0]
            events.extend([PerceptionEvent.create(EventType.FACE_DETECTED), PerceptionEvent.create(EventType.PERSON_DETECTED)])
            if not self._person_was_visible:
                events.append(PerceptionEvent.create(EventType.PERSON_ENTERED_VIEW))
        elif self._person_was_visible:
            events.append(PerceptionEvent.create(EventType.PERSON_LEFT_VIEW))
        self._person_was_visible = person_visible
        return events


def _load_cv2() -> Any:
    try:
        import cv2
    except ImportError as error:
        raise RuntimeError("Instala visión con: python -m pip install '.[vision]'") from error
    return cv2
