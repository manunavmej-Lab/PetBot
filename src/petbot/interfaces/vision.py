from __future__ import annotations

from typing import Any, Protocol

from petbot.domain.events import PerceptionEvent


class Camera(Protocol):
    def capture_frame(self) -> Any: ...
    def close(self) -> None: ...


class VisionDetector(Protocol):
    def detect(self, frame: Any) -> list[PerceptionEvent]: ...


class EventBus(Protocol):
    def publish(self, event: PerceptionEvent) -> None: ...
