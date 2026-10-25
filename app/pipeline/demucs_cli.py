"""One-shot fallback using the same safe model loader and WAV writer as workers."""

from __future__ import annotations

import argparse
import json
import sys

from app.pipeline.demucs_protocol import PROTOCOL_PREFIX
from app.pipeline.demucs_worker import _load_model, separate_track, validate_demucs_compatibility


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-n", "--name", required=True)
    parser.add_argument("-d", "--device", required=True)
    parser.add_argument("--shifts", type=int, default=1)
    parser.add_argument("--overlap", type=float, default=0.25)
    parser.add_argument("--segment", type=float, default=0.0)
    parser.add_argument("-j", "--jobs", type=int, default=0)
    parser.add_argument("--float32", action="store_true")
    parser.add_argument(
        "--clip-mode", choices=("rescale", "clamp", "tanh", "none"), default="rescale"
    )
    parser.add_argument("-o", "--out", required=True)
    parser.add_argument("source")
    args = parser.parse_args()
    validate_demucs_compatibility()
    model = _load_model(args.name, args.device)

    def emit(event: dict) -> None:
        print(PROTOCOL_PREFIX + json.dumps(event), file=sys.stderr, flush=True)

    separate_track(
        model,
        args.name,
        args.device,
        {
            "requestId": "cli",
            "source": args.source,
            "jobDir": args.out,
            "shifts": args.shifts,
            "overlap": args.overlap,
            "segment": args.segment,
            "jobs": args.jobs,
            "float32": args.float32,
            "clipMode": args.clip_mode,
        },
        emitter=emit,
    )


if __name__ == "__main__":
    main()
