import hashlib
import pickle
from pathlib import Path

import pytest
import torch
from demucs.htdemucs import HTDemucs

from app.pipeline.demucs_models import read_checkpoint


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def test_safe_checkpoint_retains_demucs_architecture_without_disabling_weights_only(tmp_path):
    path = tmp_path / "model.th"
    package = {"klass": HTDemucs, "args": (), "kwargs": {}, "state": {"a": torch.ones(2)}}
    torch.save(package, path)

    loaded = read_checkpoint(path, checksum(path))

    assert loaded["klass"] is HTDemucs
    assert torch.equal(loaded["state"]["a"], torch.ones(2))
    assert HTDemucs not in torch.serialization.get_safe_globals()


def test_modified_cache_is_rejected_before_deserialization(tmp_path, monkeypatch):
    path = tmp_path / "model.th"
    torch.save({"state": {}}, path)
    expected = checksum(path)
    path.write_bytes(path.read_bytes() + b"tampered")
    monkeypatch.setattr(torch, "load", lambda *_args, **_kwargs: pytest.fail("unsafe load"))

    with pytest.raises(ValueError, match="checksum"):
        read_checkpoint(path, expected)


def test_weights_only_rejects_arbitrary_pickle_without_executing_it(tmp_path):
    path = tmp_path / "model.th"
    marker = tmp_path / "executed"

    class Payload:
        def __reduce__(self):
            return eval, (f"__import__('pathlib').Path({str(marker)!r}).write_text('executed')",)

    torch.save({"state": Payload()}, path)

    with pytest.raises(pickle.UnpicklingError):
        read_checkpoint(path, checksum(path))

    assert not marker.exists()
