import pytest

from app import validate_generation_request


def test_generation_request_is_trimmed_and_validated():
    request = validate_generation_request(
        {"text": "  hello there  ", "lang": "en", "voice": "female"}
    )
    assert request == {"text": "hello there", "lang": "en", "voice": "female"}


def test_malayalam_request_requires_malayalam_script():
    request = validate_generation_request(
        {"text": "നമസ്കാരം സുഹൃത്തുക്കളേ", "lang": "ml", "voice": "female"}
    )
    assert request["lang"] == "ml"

    with pytest.raises(ValueError, match="does not look like Malayalam"):
        validate_generation_request(
            {"text": "Hello, how are you?", "lang": "ml", "voice": "female"}
        )


@pytest.mark.parametrize(
    "payload",
    [
        {"text": "  ", "lang": "en", "voice": "male"},
        {"text": "hello", "lang": "fr", "voice": "male"},
        {"text": "hello", "lang": "ml", "voice": "other"},
    ],
)
def test_generation_request_rejects_invalid_fields(payload):
    with pytest.raises(ValueError):
        validate_generation_request(payload)
