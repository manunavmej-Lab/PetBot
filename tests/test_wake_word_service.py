from petbot.services.wake_word_service import WakeWordService


class FakeSpeechToText:
    def transcribe(self) -> str:
        return ""


def service(wake_word: str = "Bulvi") -> WakeWordService:
    return WakeWordService(FakeSpeechToText(), wake_word, lambda text: None, lambda: False)


def test_extracts_only_phrases_addressed_to_bulvi() -> None:
    listener = service()

    assert listener.extract_message("Bulvi, hola") == "hola"
    assert listener.extract_message("Bulbi, hola") == "hola"
    assert listener.extract_message("hola Bulvi") == "hola"
    assert listener.extract_message("estoy triste, Bulvi") == "estoy triste"
    assert listener.extract_message("oye Bulvi me siento triste") == "me siento triste"
    assert listener.extract_message("hola mascota") is None


def test_wake_word_alone_becomes_greeting() -> None:
    assert service().extract_message("Bulvi") == "hola"
