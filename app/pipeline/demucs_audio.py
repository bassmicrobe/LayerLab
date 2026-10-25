"""Demucs-compatible WAV output without TorchAudio's optional codec ABI."""

from pathlib import Path

import soundfile as sf
import torch
from demucs.audio import prevent_clip


def save_audio(
    waveform: torch.Tensor,
    path: str | Path,
    *,
    samplerate: int,
    clip: str | None = "rescale",
    bits_per_sample: int = 16,
    as_float: bool = False,
) -> None:
    destination = Path(path)
    if destination.suffix.lower() != ".wav":
        raise ValueError("Demucs output must be a WAV file")
    if isinstance(samplerate, bool) or not isinstance(samplerate, int) or samplerate <= 0:
        raise ValueError("sample rate must be a positive integer")
    if waveform.ndim != 2 or waveform.shape[0] < 1 or waveform.shape[1] < 1:
        raise ValueError("audio must contain channels and samples")
    if not bool(torch.isfinite(waveform).all()):
        raise ValueError("audio contains non-finite samples")
    if bits_per_sample not in {16, 24, 32}:
        raise ValueError("unsupported PCM bit depth")
    samples = waveform.detach().to(device="cpu", dtype=torch.float32)
    clipped = prevent_clip(samples, mode=clip)
    subtype = "FLOAT" if as_float else f"PCM_{bits_per_sample}"
    sf.write(destination, clipped.transpose(0, 1).numpy(), samplerate, subtype=subtype)
