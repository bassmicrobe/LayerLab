import numpy as np
import pytest
import soundfile as sf
import torch

from app.pipeline.demucs_audio import save_audio


@pytest.mark.parametrize("as_float, subtype", [(True, "FLOAT"), (False, "PCM_16")])
def test_save_audio_keeps_sample_rate_channels_and_length(tmp_path, as_float, subtype):
    path = tmp_path / "stem.wav"
    waveform = torch.tensor([[0.25, -0.25, 0.0], [0.5, -0.5, 0.0]])
    original = waveform.clone()

    save_audio(waveform, path, samplerate=48000, as_float=as_float, clip="none")

    actual, sample_rate = sf.read(path, dtype="float32", always_2d=True)
    assert sf.info(path).subtype == subtype
    assert sample_rate == 48000
    assert actual.shape == (3, 2)
    np.testing.assert_allclose(actual, waveform.numpy().T, atol=1 / 32768)
    assert torch.equal(waveform, original)


def test_float_wav_preserves_super_unity_samples_without_torchcodec(tmp_path, monkeypatch):
    import torchaudio

    monkeypatch.setattr(
        torchaudio, "save", lambda *_args, **_kwargs: pytest.fail("TorchCodec path used")
    )
    waveform = torch.tensor([[1.25, -1.5], [0.0, 0.5]])
    path = tmp_path / "stem.wav"

    save_audio(waveform, path, samplerate=44100, as_float=True, clip="none")

    actual, _ = sf.read(path, dtype="float32", always_2d=True)
    np.testing.assert_array_equal(actual, waveform.numpy().T)


@pytest.mark.parametrize("clip", ["rescale", "clamp", "tanh"])
def test_save_audio_preserves_demucs_clipping_modes(tmp_path, clip):
    from demucs.audio import prevent_clip

    waveform = torch.tensor([[1.5, -2.0], [0.4, -0.1]])
    path = tmp_path / "stem.wav"
    save_audio(waveform, path, samplerate=44100, as_float=True, clip=clip)

    actual, _ = sf.read(path, dtype="float32", always_2d=True)
    np.testing.assert_allclose(actual, prevent_clip(waveform, clip).numpy().T)


@pytest.mark.parametrize("waveform", [torch.tensor([[float("nan")]]), torch.empty((2, 0))])
def test_save_audio_rejects_invalid_samples_without_overwriting(tmp_path, waveform):
    path = tmp_path / "existing.wav"
    path.write_bytes(b"keep")

    with pytest.raises(ValueError):
        save_audio(waveform, path, samplerate=44100, as_float=True)

    assert path.read_bytes() == b"keep"
