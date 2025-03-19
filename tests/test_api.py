from pathlib import Path

import pytest
from main import create_app

samples = Path("tests/samples")


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_server_is_up(client):
    response = client.get("/alive/")
    assert response.status_code == 200
    assert response.get_json() == {"message": "alive"}


def test_analyze_audio(client):
    response = client.post(
        "/analyze-audio/",
        json={"audio": (samples / "valid.txt").open().read()},
    )

    assert response.status_code == 200
    assert "duration" in response.get_json()
    assert "sample_rate" in response.get_json()
    assert "channels_count" in response.get_json()
    assert "format" in response.get_json()
    assert "bit_depth" in response.get_json()


def test_missing_audio_field(client):
    response = client.post("/analyze-audio/", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Audio field is required"}


def test_bad_base64_value(client):
    response = client.post("/analyze-audio/", json={"audio": "bad_base64"})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid base64 value"}


def test_unsupported_audio_format(client):
    response = client.post(
        "/analyze-audio/",
        json={"audio": (samples / "invalid.txt").open().read()},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Not supported audio format"}


def test_get_analyze_audio(client):
    response = client.get("/analyze-audio/")
    assert response.status_code == 405


def test_analyze_binary_audio(client):
    audio = samples / "valid.mp3"
    audio_content = open(audio, "rb")
    data = {"audio": (audio_content, "valid.mp3")}
    response = client.post(
        "/analyze-binary-audio/",
        data=data,
        buffered=True,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "duration" in response.get_json()
    assert "sample_rate" in response.get_json()
    assert "channels_count" in response.get_json()
    assert "format" in response.get_json()
    assert "bit_depth" in response.get_json()


def test_analyze_binary_audio_no_file(client):
    response = client.post("/analyze-binary-audio/")
    assert response.status_code == 400
    assert response.get_json() == {"error": "No file uploaded"}


def test_analyze_invalid_binary_audio(client):
    invalid_audio = samples / "invalid.pdf"
    invalid_audio_content = open(invalid_audio, "rb")
    data = {"audio": (invalid_audio_content, "invalid.pdf")}

    response = client.post(
        "/analyze-binary-audio/",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "Not supported audio format"}
