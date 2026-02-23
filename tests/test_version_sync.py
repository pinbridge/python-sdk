from __future__ import annotations

from pathlib import Path

import tomllib

import pinbridge_sdk


def test_package_version_matches_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    assert pinbridge_sdk.__version__ == data["project"]["version"]
