"""Opt-in real-model separation check used by release CI and runtime validation."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

from app.core.config import ffmpeg_executable
from app.pipeline.demucs_worker import _load_model, separate_track, validate_demucs_compatibility


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("htdemucs_6s", "htdemucs_ft"), required=True)
    parser.add_argument("--device", choices=("cpu", "mps"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()
    validate_demucs_compatibility()
    torch.set_num_threads(2)
    args.output.mkdir(parents=True, exist_ok=True)
    source = args.output / "source.wav"
    if args.source:
        subprocess.run(
            [
                ffmpeg_executable(),
                "-nostdin",
                "-v",
                "error",
                "-i",
                str(args.source),
                "-t",
                "8",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-c:a",
                "pcm_f32le",
                "-y",
                str(source),
            ],
            check=True,
            timeout=60,
        )
    else:
        times = np.arange(44100 * 4, dtype=np.float32) / 44100
        signal = 0.1 * (np.sin(2 * np.pi * 110 * times) + np.sin(2 * np.pi * 440 * times))
        sf.write(source, np.column_stack((signal, signal * 0.8)), 44100, subtype="FLOAT")
    started = time.monotonic()
    model = _load_model(args.model, args.device)
    output = separate_track(
        model,
        args.model,
        args.device,
        {
            "requestId": "release-smoke",
            "source": str(source),
            "jobDir": str(args.output),
            "shifts": 0,
            "overlap": 0.25,
            "segment": 6.0,
            "jobs": 0,
            "float32": True,
            "clipMode": "none",
        },
    )
    expected = sf.info(source)
    for stem in model.sources:
        path = output / f"{stem}.wav"
        info = sf.info(path)
        samples, _ = sf.read(path, dtype="float32", always_2d=True)
        if (
            info.subtype != "FLOAT"
            or info.frames != expected.frames
            or info.samplerate != expected.samplerate
            or info.channels != 2
            or not np.isfinite(samples).all()
        ):
            raise RuntimeError(f"invalid output from {args.model}: {stem}")
    report = {
        "torch": torch.__version__,
        "model": args.model,
        "device": args.device,
        "stems": list(model.sources),
        "frames": expected.frames,
        "sampleRate": expected.samplerate,
        "subtype": "FLOAT",
        "elapsedSeconds": round(time.monotonic() - started, 2),
        "ok": True,
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
