import pytest

from petbot.services.voice_service import VoiceService


class FakeSpeechToText:
    def transcribe(self) -> str:
        return "hola Buvi"


class FakeTextToSpeech:
    def synthesize(self, text: str) -> str:
        return f"audio:{text}"


class FakeSpeaker:
    def __init__(self, speaking: bool = False) -> None:
        self.speaking = speaking
        self.played: list[str] = []

    def play(self, utterance: str) -> None:
        self.played.append(utterance)

    def is_speaking(self) -> bool:
        return self.speaking


def test_voice_service_listens_and_speaks() -> None:
    speaker = FakeSpeaker()
    service = VoiceService(FakeSpeechToText(), FakeTextToSpeech(), speaker)

    assert service.listen() == "hola Buvi"
    service.speak("Hola, Manu")
    assert speaker.played == ["audio:Hola, Manu"]


def test_voice_service_does_not_listen_while_speaking() -> None:
    service = VoiceService(FakeSpeechToText(), FakeTextToSpeech(), FakeSpeaker(speaking=True))

    with pytest.raises(RuntimeError, match="hablando"):
        service.listen()
