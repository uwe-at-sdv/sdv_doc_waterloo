#!/usr/bin/env python3
"""Tests for tracer output target handling."""

from __future__ import annotations

import io
import json
import sys

from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.waterlint_common import DIAG_TARGET_STDERR, DIAG_TARGET_STDOUT, emit_tracer


class _TTYStringIO(io.StringIO):
	def isatty(self) -> bool:
		return True


def test_emit_tracer_supports_special_stream_targets(monkeypatch) -> None:
	stdout = _TTYStringIO()
	stderr = _TTYStringIO()
	monkeypatch.setattr(sys, "stdout", stdout)
	monkeypatch.setattr(sys, "stderr", stderr)

	tr = tracer()
	tr.add_error("TOOL-001", "tool", "boom")

	emit_tracer(
		tr,
		DIAG_TARGET_STDOUT,
		DIAG_TARGET_STDERR,
		debug=False,
		callback_build_json_doc=lambda tr_: {"ok": True},
	)

	assert "boom" in stdout.getvalue()
	assert "\"ok\": true" in stderr.getvalue().lower()


def test_emit_tracer_writes_regular_files(tmp_path) -> None:
	out_txt = tmp_path / "diag.txt"
	out_json = tmp_path / "diag.json"

	tr = tracer()
	tr.add_error("TOOL-001", "tool", "boom")

	emit_tracer(
		tr,
		str(out_txt),
		str(out_json),
		debug=False,
		callback_build_json_doc=lambda tr_: {"ok": True},
	)

	txt = out_txt.read_text(encoding="utf-8")
	assert "boom" in txt
	assert "\x1b[" not in txt
	assert json.loads(out_json.read_text(encoding="utf-8")) == {"ok": True}
