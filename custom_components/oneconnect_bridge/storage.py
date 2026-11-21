from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .const import DOMAIN


_PATH_SEPARATORS = ("/", "\\", "\x00")


def is_safe_child_key(key: object) -> bool:
    """Return whether a mapping key can be used as a single child directory name."""

    return (
        isinstance(key, str)
        and bool(key)
        and key not in {".", ".."}
        and not any(char in key for char in _PATH_SEPARATORS)
        and not any(ord(char) < 0x20 or ord(char) == 0x7F for char in key)
    )


class GatewayStore:
    """Store runtime material below HA's .storage directory."""

    def __init__(self, config_dir: str, serial: str) -> None:
        if not serial or any(char not in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_-" for char in serial):
            raise ValueError("gateway serial contains an unsafe path character")
        self._serial = serial
        self._gateways_root = (
            Path(config_dir) / ".storage" / DOMAIN / "gateways"
        )
        self.root = self._gateways_root / serial
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)

    def path(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if self.root.resolve() not in path.parents and path != self.root.resolve():
            raise ValueError("storage path escapes the gateway directory")
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return path

    def read_json(self, relative: str) -> dict[str, Any] | None:
        path = self.path(relative)
        if not path.is_file():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"stored JSON is invalid: {path}") from error
        if not isinstance(value, dict):
            raise ValueError(f"stored JSON object expected: {path}")
        return value

    def read_child_materials(self) -> dict[str, dict[str, Any]]:
        """Read all child material files in this gateway's storage scope."""

        children_root = self.root / "children"
        if not children_root.is_dir():
            return {}

        materials: dict[str, dict[str, Any]] = {}
        for child_root in sorted(children_root.iterdir(), key=lambda path: path.name):
            if not child_root.is_dir():
                continue
            material_path = child_root / "material.json"
            if not material_path.is_file():
                materials[child_root.name] = {}
                continue
            try:
                value = json.loads(material_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                value = None
            materials[child_root.name] = value if isinstance(value, dict) else {}
        return materials

    def write_json(self, relative: str, value: dict[str, Any]) -> Path:
        path = self.path(relative)
        self._write_atomic(
            path,
            (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        )
        return path

    @staticmethod
    def _write_atomic(path: Path, data: bytes) -> None:
        """Replace one file atomically without sharing a temp name across writers."""

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

    def ensure_mapping_file(self, source: Path) -> Path:
        """Copy the bundled sample mapping once into this gateway scope."""

        target = self.path("mapping.yaml")
        if target.is_file():
            return target
        if not source.is_file():
            raise FileNotFoundError(source)
        self._write_atomic(target, source.read_bytes())
        return target

    def remove_gateway(self) -> None:
        """Remove exactly this gateway's storage scope."""

        root = self.root.resolve()
        gateways_root = self._gateways_root.resolve()
        if root.parent != gateways_root or root.name != self._serial:
            raise ValueError("refusing to remove an unexpected gateway path")
        if root.is_dir():
            shutil.rmtree(root)

    def remove_child(self, key: str) -> None:
        """Remove exactly one child storage scope."""

        if not is_safe_child_key(key):
            raise ValueError("child key contains an unsafe path character")
        children_root = (self.root / "children").resolve()
        child_root = (children_root / key).resolve()
        if child_root.parent != children_root or child_root.name != key:
            raise ValueError("refusing to remove an unexpected child path")
        if child_root.is_dir():
            shutil.rmtree(child_root)
