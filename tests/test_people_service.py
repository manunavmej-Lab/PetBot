from uuid import uuid4

from petbot.services.people_service import PeopleService


class FakePeopleRepository:
    def __init__(self) -> None:
        self.people = []

    def save(self, person: object) -> None:
        self.people.append(person)

    def list_for_pet(self, pet_id: object) -> list[object]:
        return [person for person in self.people if person.pet_id == pet_id]


def test_registers_a_consented_person_and_recognizes_their_embedding() -> None:
    pet_id = uuid4()
    service = PeopleService(FakePeopleRepository())

    saved = service.register_with_consent(pet_id, "Ana", [1.0, 0.0, 0.0])
    recognized = service.identify(pet_id, [0.98, 0.02, 0.0])

    assert recognized == saved


def test_does_not_recognize_a_different_face() -> None:
    pet_id = uuid4()
    service = PeopleService(FakePeopleRepository())
    service.register_with_consent(pet_id, "Ana", [1.0, 0.0, 0.0])

    assert service.identify(pet_id, [0.0, 1.0, 0.0]) is None
