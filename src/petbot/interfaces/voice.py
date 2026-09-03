from __future__ import annotations

from typing import Protocol


class SpeechToText(Protocol):
    def transcribe(self) -> str: ...


class TextToSpeech(Protocol):
    def synthesize(self, text: str) -> str: ...


class Speaker(Protocol):
    def play(self, utterance: str) -> None: ...
    def is_speaking(self) -> bool: ...
