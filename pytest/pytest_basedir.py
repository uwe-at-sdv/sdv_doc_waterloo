"""Regression tests for --basedir object resolution."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from sdv.doc.waterloo.waterlint_common import _apply_basedir


def _clear_namespace(namespace: str) -> None:
	for name in tuple(sys.modules):
		if name == namespace or name.startswith(f"{namespace}."):
			del sys.modules[name]


def test_apply_basedir_preserves_sibling_namespace_portions(tmp_path: Path, monkeypatch) -> None:
	"""A basedir package can import a sibling portion of its namespace."""

	namespace = "waterloo_basedir_namespace"
	base_root = tmp_path / "base"
	sibling_root = tmp_path / "sibling"
	feature_dir = base_root / namespace / "feature"
	shared_dir = sibling_root / namespace / "shared"
	feature_dir.mkdir(parents=True)
	shared_dir.mkdir(parents=True)
	(feature_dir / "__init__.py").write_text(
		"from waterloo_basedir_namespace.shared import VALUE\n",
		encoding="utf-8",
	)
	(shared_dir / "__init__.py").write_text("VALUE = \"sibling value\"\n", encoding="utf-8")

	_clear_namespace(namespace)
	monkeypatch.syspath_prepend(str(sibling_root))
	try:
		_apply_basedir(str(base_root), f"{namespace}.feature")
		feature = importlib.import_module(f"{namespace}.feature")
		assert feature.VALUE == "sibling value"
		assert set(sys.modules[namespace].__path__) == {
			str(base_root / namespace),
			str(sibling_root / namespace),
		}
	finally:
		_clear_namespace(namespace)
