from __future__ import annotations

from petbot.interfaces.voice import Speaker, SpeechToText, TextToSpeech


class VoiceService:
    def __init__(self, speech_to_text: SpeechToText, text_to_speech: TextToSpeech, speaker: Speaker) -> None:
        self._speech_to_text = speech_to_text
        self._text_to_speech = text_to_speech
        self._speaker = speaker

    def listen(self) -> str:
        if self._speaker.is_speaking():
            raise RuntimeError("Buvi está hablando; espera a que termine.")
        return self._speech_to_text.transcribe()

    def speak(self, text: str) -> None:
        self._speaker.play(self._text_to_speech.synthesize(text))
