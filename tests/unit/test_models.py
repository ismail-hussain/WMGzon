from application.models import FriendsCharacter

def test_new_character():
    character = FriendsCharacter('Joey', 12, "HOLA")

    assert character.name == "Joey"
    assert character.age == 12
    assert character.catch_phrase == "HOLA"
