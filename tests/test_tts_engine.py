import sys
from types import SimpleNamespace

import numpy as np

from src.audio.tts_engine import EdgeTTSEngine


def test_edge_mp3_is_decoded_to_float_audio(monkeypatch):
    expected = np.array([0.25, -0.5], dtype="<f4")
    monkeypatch.setitem(
        sys.modules,
        "imageio_ffmpeg",
        SimpleNamespace(get_ffmpeg_exe=lambda: "ffmpeg"),
    )

    def fake_run(command, **kwargs):
        assert command[0] == "ffmpeg"
        assert kwargs["input"] == b"mp3-data"
        assert "pipe:0" in command and "pipe:1" in command
        return SimpleNamespace(stdout=expected.tobytes(), stderr=b"")

    monkeypatch.setattr("src.audio.tts_engine.subprocess.run", fake_run)
    engine = EdgeTTSEngine.__new__(EdgeTTSEngine)
    engine.sample_rate = 24000

    assert engine._decode_mp3(b"mp3-data").tolist() == expected.tolist()
