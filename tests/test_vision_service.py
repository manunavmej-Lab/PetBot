from petbot.domain.events import EventType, PerceptionEvent
from petbot.infrastructure.events.in_memory_event_bus import InMemoryEventBus
from petbot.services.vision_service import VisionService


class FakeCamera:
    def __init__(self) -> None:
        self.preview_enabled: bool | None = None

    def capture_frame(self) -> str:
        return "frame"

    def close(self) -> None:
        pass

    def set_preview_enabled(self, enabled: bool) -> None:
        self.preview_enabled = enabled


class FakeDetector:
    def detect(self, frame: str) -> list[PerceptionEvent]:
        assert frame == "frame"
        return [PerceptionEvent.create(EventType.PERSON_DETECTED)]


class MultiFaceFakeDetector(FakeDetector):
    last_embeddings = [[1.0, 0.0], [0.0, 1.0]]


def test_detection_is_published_as_event() -> None:
    bus = InMemoryEventBus()

    events = VisionService(FakeCamera(), FakeDetector(), bus).observe_once()

    assert events[0].type is EventType.PERSON_DETECTED
    assert bus.events == events


def test_exposes_each_detected_face_embedding() -> None:
    service = VisionService(FakeCamera(), MultiFaceFakeDetector(), InMemoryEventBus())

    service.observe_once()

    assert service.last_embeddings == [[1.0, 0.0], [0.0, 1.0]]


def test_can_toggle_development_camera_preview() -> None:
    camera = FakeCamera()
    service = VisionService(camera, FakeDetector(), InMemoryEventBus())

    assert service.set_preview_enabled(True)
    assert camera.preview_enabled is True
