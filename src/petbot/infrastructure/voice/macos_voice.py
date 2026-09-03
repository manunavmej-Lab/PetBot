from __future__ import annotations

import subprocess
import plistlib
import tempfile
from pathlib import Path


class MacSpeechToText:
    def __init__(self, locale: str = "es-ES") -> None:
        self._locale = locale
        self._script = Path(__file__).with_name("macos_speech.swift")

    def transcribe(self) -> str:
        executable = self._ensure_helper()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "transcription.txt"
            # LaunchServices asocia el proceso con el bundle y su Info.plist de privacidad.
            try:
                result = subprocess.run(["open", "-W", "-n", str(executable.parents[2]), "--args", self._locale, str(output)], capture_output=True, text=True, timeout=20, check=False)
            except subprocess.TimeoutExpired as error:
                raise RuntimeError("Se agotó el tiempo de escucha. Prueba otra vez y habla al terminar de escribir 'hablar'.") from error
            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "No se pudo iniciar el reconocimiento de voz.")
            text = output.read_text().strip() if output.exists() else ""
        if not text:
            raise RuntimeError("No se detectó ninguna frase.")
        return text

    def _ensure_helper(self) -> Path:
        """Crea una app mínima: macOS exige su Info.plist para pedir permisos TCC."""
        app = Path.cwd() / "data" / "PetBotVoice.app"
        executable = app / "Contents" / "MacOS" / "PetBotVoice"
        info = app / "Contents" / "Info.plist"
        if executable.exists() and executable.stat().st_mtime >= self._script.stat().st_mtime:
            return executable
        executable.parent.mkdir(parents=True, exist_ok=True)
        with info.open("wb") as stream:
            plistlib.dump({
                "CFBundleIdentifier": "com.petbot.voice",
                "CFBundleName": "PETBOT Voice",
                "CFBundleExecutable": "PetBotVoice",
                "CFBundlePackageType": "APPL",
                "NSMicrophoneUsageDescription": "PETBOT necesita el micrófono para escuchar a su propietario.",
                "NSSpeechRecognitionUsageDescription": "PETBOT necesita reconocer la voz para conversar.",
            }, stream)
        subprocess.run(["swiftc", str(self._script), "-o", str(executable)], check=True, capture_output=True, text=True)
        subprocess.run(["xattr", "-cr", str(app)], check=True, capture_output=True, text=True)
        subprocess.run(["codesign", "--force", "--sign", "-", str(app)], check=True, capture_output=True, text=True)
        return executable


class MacTextToSpeech:
    def synthesize(self, text: str) -> str:
        return text


class MacSpeaker:
    def __init__(self, voice: str = "Monica") -> None:
        self._voice = voice
        self._process: subprocess.Popen[str] | None = None

    def play(self, utterance: str) -> None:
        self._process = subprocess.Popen(["say", "-v", self._voice, utterance])

    def is_speaking(self) -> bool:
        return self._process is not None and self._process.poll() is None
