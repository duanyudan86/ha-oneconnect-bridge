"""Replace one durable file atomically so a crash cannot leave it truncated."""

from __future__ import annotations

import os
from pathlib import Path
import tempfile


def write_atomic(path: Path, data: bytes) -> None:
    """Write ``data`` to ``path`` so readers never observe a partial file.

    The temp file name is unique per writer, so two writers racing on the same
    target cannot share (and overwrite) one staging file. Data is flushed to
    disk before the rename, which makes the replace the commit point: after a
    power loss the file holds either the previous or the complete new content.
    """

    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f"{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    os.chmod(path, 0o600)
