from __future__ import annotations

import shutil
import subprocess
from os import environ


class LinuxSpeechToText:
    """La escucha se habilitará al conectar un micrófono compatible."""

    def transcribe(self) -> str:
        raise RuntimeError("La escucha por voz necesita un micrófono configurado en la Raspberry.")


class LinuxTextToSpeech:
    def synthesize(self, text: str) -> str:
        return text


class LinuxSpeaker:
    def __init__(self, voice: str | None = None, device: str | None = None, speed: int | None = None) -> None:
        self._voice = voice or environ.get("PETBOT_VOICE", "es")
        self._device = device or environ.get("PETBOT_AUDIO_DEVICE", "default")
        self._speed = speed or int(environ.get("PETBOT_SPEECH_SPEED", "150"))
        self._process: subprocess.Popen[str] | None = None
        self._synthesizer: subprocess.Popen[bytes] | None = None

    def play(self, utterance: str) -> None:
        executable = shutil.which("espeak-ng")
        if executable is None:
            raise RuntimeError("Falta espeak-ng. Instálalo en la Raspberry con: sudo apt install espeak-ng")
        self._synthesizer = subprocess.Popen([executable, "--stdout", "-v", self._voice, "-s", str(self._speed), utterance], stdout=subprocess.PIPE)
        self._process = subprocess.Popen(["aplay", "-D", self._device], stdin=self._synthesizer.stdout)
        if self._synthesizer.stdout is not None:
            self._synthesizer.stdout.close()

    def is_speaking(self) -> bool:
        return self._process is not None and self._process.poll() is None


class PiperSpeaker:
    """Voz neuronal local Piper: no envía texto ni audio fuera de la Raspberry."""

    def __init__(self, model: str | None = None, speaker: int | None = None, device: str | None = None) -> None:
        self._model = model or environ.get("PETBOT_PIPER_MODEL", "models/voice/es_ES-sharvard-medium.onnx")
        self._speaker = speaker if speaker is not None else int(environ.get("PETBOT_PIPER_SPEAKER", "1"))
        self._device = device or environ.get("PETBOT_AUDIO_DEVICE", "default")
        self._process: subprocess.Popen[bytes] | None = None
        self._synthesizer: subprocess.Popen[bytes] | None = None

    def play(self, utterance: str) -> None:
        executable = environ.get("PETBOT_PIPER_EXECUTABLE") or shutil.which("piper")
        if executable is None:
            raise RuntimeError("Falta Piper. Instálalo con: python -m pip install piper-tts")
        self._synthesizer = subprocess.Popen(
            [executable, "--model", self._model, "--speaker", str(self._speaker), "--output-raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        if self._synthesizer.stdin is not None:
            self._synthesizer.stdin.write(f"{utterance}\n".encode())
            self._synthesizer.stdin.close()
        self._process = subprocess.Popen(
            ["aplay", "-D", self._device, "-r", "22050", "-f", "S16_LE", "-t", "raw"],
            stdin=self._synthesizer.stdout,
        )
        if self._synthesizer.stdout is not None:
            self._synthesizer.stdout.close()

    def is_speaking(self) -> bool:
        return self._process is not None and self._process.poll() is None
