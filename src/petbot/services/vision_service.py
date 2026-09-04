from __future__ import annotations

from petbot.domain.events import PerceptionEvent
from petbot.interfaces.vision import Camera, EventBus, VisionDetector


class VisionService:
    def __init__(self, camera: Camera, detector: VisionDetector, event_bus: EventBus) -> None:
        self._camera = camera
        self._detector = detector
        self._event_bus = event_bus

    def observe_once(self) -> list[PerceptionEvent]:
        frame = self._camera.capture_frame()
        events = self._detector.detect(frame)
        preview = getattr(self._camera, "show_preview", None)
        if callable(preview):
            preview(frame, getattr(self._detector, "last_faces", []))
        for event in events:
            self._event_bus.publish(event)
        return events

    def close(self) -> None:
        self._camera.close()

    def set_preview_enabled(self, enabled: bool) -> bool:
        setter = getattr(self._camera, "set_preview_enabled", None)
        if not callable(setter):
            return False
        setter(enabled)
        return True

    @property
    def latest_jpeg(self) -> bytes | None:
        image = getattr(self._camera, "latest_jpeg", None)
        return image if isinstance(image, bytes) else None

    @property
    def last_embedding(self) -> list[float] | None:
        """Huella de la última cara observada, si el detector puede proporcionarla."""
        embedding = getattr(self._detector, "last_embedding", None)
        return embedding if isinstance(embedding, list) else None

    @property
    def last_embeddings(self) -> list[list[float]]:
        """Huellas de todas las caras que aparecieron en la última observación."""
        embeddings = getattr(self._detector, "last_embeddings", None)
        if isinstance(embeddings, list):
            return [embedding for embedding in embeddings if isinstance(embedding, list)]
        embedding = self.last_embedding
        return [embedding] if embedding is not None else []
