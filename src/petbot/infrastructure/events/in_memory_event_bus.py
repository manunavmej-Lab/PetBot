from __future__ import annotations

from petbot.domain.events import PerceptionEvent


class InMemoryEventBus:
    def __init__(self) -> None:
        self.events: list[PerceptionEvent] = []

    def publish(self, event: PerceptionEvent) -> None:
        self.events.append(event)
