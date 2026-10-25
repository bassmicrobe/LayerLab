"""Load official Demucs packages with checked caches and restricted unpickling."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from urllib.parse import urlsplit

import numpy as np
import torch
from demucs.apply import Model
from demucs.demucs import Demucs
from demucs.hdemucs import HDemucs
from demucs.htdemucs import HTDemucs
from demucs.pretrained import REMOTE_ROOT, _parse_remote_files, demucs_unittest
from demucs.repo import AnyModelRepo, BagOnlyRepo, ModelOnlyRepo
from demucs.states import load_model
from numpy._core.multiarray import scalar

_MODEL_CLASSES = (Demucs, HDemucs, HTDemucs)


def read_checkpoint(path: Path, expected_checksum: str) -> dict:
    if not re.fullmatch(r"(?:[0-9a-f]{8}|[0-9a-f]{64})", expected_checksum):
        raise ValueError("invalid model checksum")
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if not actual.startswith(expected_checksum):
            raise ValueError(f"model checksum mismatch: {path.name}")
        stream.seek(0)
        # Official checkpoints store the architecture and a few NumPy scalars.
        # Never fall back to unrestricted pickle or persist these safe globals.
        with torch.serialization.safe_globals(
            [
                *_MODEL_CLASSES,
                Fraction,
                (scalar, "numpy.core.multiarray.scalar"),
                scalar,
                np.dtype,
                type(np.dtype(np.float32)),
                type(np.dtype(np.float64)),
            ]
        ):
            package = torch.load(stream, map_location="cpu", weights_only=True)
    if not isinstance(package, dict) or package.get("klass") not in _MODEL_CLASSES:
        raise ValueError("unsupported Demucs checkpoint architecture")
    if not isinstance(package.get("args"), (tuple, list)) or not isinstance(
        package.get("kwargs"), dict
    ):
        raise ValueError("invalid Demucs model parameters")
    state = package.get("state")
    if not isinstance(state, dict) or not all(
        isinstance(key, str) and isinstance(value, torch.Tensor) for key, value in state.items()
    ):
        raise ValueError("checkpoint must contain an unquantized tensor state")
    return package


@dataclass(frozen=True)
class SafeRemoteRepo(ModelOnlyRepo):
    models: Mapping[str, str]

    def has_model(self, signature: str) -> bool:
        return signature in self.models

    def get_model(self, signature: str) -> Model:
        if signature not in self.models:
            raise ValueError("unknown official Demucs model signature")
        url = self.models[signature]
        parsed = urlsplit(url)
        filename = Path(parsed.path).name
        match = re.fullmatch(r"[0-9a-f]{8}-([0-9a-f]{8})\.th", filename)
        if (
            parsed.scheme != "https"
            or parsed.netloc != "dl.fbaipublicfiles.com"
            or not parsed.path.startswith("/demucs/")
            or parsed.query
            or parsed.fragment
            or match is None
        ):
            raise ValueError("invalid official Demucs model URL")
        cache = Path(torch.hub.get_dir()) / "checkpoints" / filename
        if not cache.is_file():
            cache.parent.mkdir(parents=True, exist_ok=True)
            torch.hub.download_url_to_file(url, str(cache), hash_prefix=match.group(1))
        package = read_checkpoint(cache, match.group(1))
        return load_model(package, strict=True)


def get_model(name: str) -> Model:
    if not re.fullmatch(r"[A-Za-z0-9_]+", name):
        raise ValueError("invalid Demucs model name")
    if name == "demucs_unittest":
        return demucs_unittest().eval()
    catalog = MappingProxyType(_parse_remote_files(REMOTE_ROOT / "files.txt"))
    models = SafeRemoteRepo(catalog)
    model = AnyModelRepo(models, BagOnlyRepo(REMOTE_ROOT, models)).get_model(name)
    return model.eval()
