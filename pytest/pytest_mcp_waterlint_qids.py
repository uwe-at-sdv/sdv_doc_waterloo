#!/usr/bin/env python3
"""Regression tests for waterlint QID naming."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WATERLINT_ROOT_JSON = ROOT / "mcp_roots" / "waterlint.wtrl.core.rfc-2119.json"


def test_waterlint_root_qids_keep_package_namespace() -> None:
	with WATERLINT_ROOT_JSON.open("r", encoding="utf-8") as fh:
		document = json.load(fh)
	assert isinstance(document, dict), document

	qids = set()
	for key in ("__WTRL_TOC_MODULES__", "__WTRL_TOC_CALLABLES__", "__WTRL_TOC_CLASSES__", "__WTRL_TOC_TYPES__", "__WTRL_TOC_VARIABLES__", "__WTRL_TOC_CONSTANTS__"):
		toc = document.get(key)
		assert isinstance(toc, dict), (key, document)
		qids.update(str(qid) for qid in toc.keys())

	assert qids, document
	assert all(qid.startswith("sdv.doc.waterloo.") for qid in qids), sorted(qids)
	assert "sdv.doc.waterloo.waterlint" in qids, sorted(qids)
	assert "sdv.doc.waterloo.waterlint.render_json_command" in qids, sorted(qids)
