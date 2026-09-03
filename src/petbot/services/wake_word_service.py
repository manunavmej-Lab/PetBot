from __future__ import annotations

import re
from collections.abc import Callable
from threading import Event, Thread
from time import sleep

from petbot.interfaces.voice import SpeechToText


class WakeWordService:
    """Escucha frases cortas en bucle y entrega solo las que contienen el nombre de la mascota."""

    def __init__(self, speech_to_text: SpeechToText, wake_word: str, on_message: Callable[[str], None], is_speaking: Callable[[], bool]) -> None:
        self._speech_to_text = speech_to_text
        self._wake_word = wake_word
        # En reconocimiento español b y v se transcriben indistintamente.
        phonetic_word = "".join("[bv]" if character in "bv" else re.escape(character) for character in wake_word.casefold())
        self._wake_pattern = re.compile(rf"\b{phonetic_word}\b", re.IGNORECASE)
        self._on_message = on_message
        self._is_speaking = is_speaking
        self._stop = Event()
        self._thread: Thread | None = None

    def start(self) -> None:
        self._thread = Thread(target=self._listen_loop, daemon=True, name="petbot-wake-word")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def extract_message(self, transcription: str) -> str | None:
        match = self._wake_pattern.search(transcription)
        if match is None:
            return None
        # Puede estar al principio, al final o en medio: se conserva toda la frase menos el nombre.
        message = " ".join(f"{transcription[:match.start()]} {transcription[match.end():]}".strip(" ,:;").split())
        message = re.sub(r"^oye[,:;]?\s*", "", message, flags=re.IGNORECASE)
        return message or "hola"

    def _listen_loop(self) -> None:
        while not self._stop.is_set():
            if self._is_speaking():
                sleep(0.2)
                continue
            try:
                transcription = self._speech_to_text.transcribe()
            except (RuntimeError, TimeoutError):
                continue
            message = self.extract_message(transcription)
            if message is not None:
                self._on_message(message)
