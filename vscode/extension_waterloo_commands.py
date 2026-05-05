#!/usr/bin/env python3
from __future__ import annotations

import sys
import ast
import json
import tempfile
from pathlib import Path
from typing import Any, Generator, cast
from ast import AsyncFunctionDef, ClassDef, FunctionDef, Module

try:
	import sdv.doc.waterloo.docitem as wtrl
	import sdv.doc.waterloo.docitem_genutil as genutil
except ImportError as e:
	ROOT = Path(__file__).resolve().parents[2]
	for p in (str(ROOT), str(ROOT / "package" / "src")):
		if p not in sys.path:
			sys.path.insert(0, p)
	try:
		import sdv_doc_docitem as wtrl
		import sdv_doc_docitem_genutil as genutil
	except ImportError:
		print(f"Error importing Waterloo modules: {e}", file=sys.stderr)
		print("Please download and install sdv_doc_waterloo from https://github.com/uwe-at-sdv/sdv_doc_waterloo", file=sys.stderr)
		sys.exit(1)


COMMAND_PING = "ping"
COMMAND_GENERATE_MINIMAL = "generate_minimal_docstring_to_tmp"
COMMAND_GENERATE_FULL = "generate_full_docstring_to_tmp"
COMMAND_VALIDATE = "validate_docstring"

HeaderNode_t = Module | ClassDef | FunctionDef | AsyncFunctionDef
DocstringOwnerNode_t = Module | ClassDef | FunctionDef | AsyncFunctionDef


def _parse_file_to_ast(filename: str) -> Module:
	with open(filename, "r", encoding="utf-8") as f:
		source = f.read()
	tree = ast.parse(source)
	return tree

def _gen_qis_and_nodes(nd_parent: ast.AST, prefix: str) -> Generator[tuple[str, DocstringOwnerNode_t], None, None]:
# Only consider objects which can have a docstring as per Python standard.
	if isinstance(nd_parent, ast.Module):
		qi = prefix
		yield qi, nd_parent
	elif isinstance(nd_parent, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
		qi = f"{prefix}.{nd_parent.name}"
		yield qi,nd_parent
	else:
		qi = prefix
	for nd in ast.iter_child_nodes(nd_parent):
		yield from _gen_qis_and_nodes(nd, qi)

def _qualify_documented_object(module_filename: str, name: str, line: int) -> str:
	tree = _parse_file_to_ast(module_filename)
	module_name = Path(module_filename).stem
	for qi,nd in _gen_qis_and_nodes(tree,module_name):
# We are only interested in objects with a docstring.
		doc: str | None = ast.get_docstring(nd)
		if doc:
#			print(qi,"<->",name)
			if qi.split(".")[-1] == name:
# Module node has no lineno/end_lineno and does not represent the selected header.
				if isinstance(nd, ast.Module):
					continue
# Check against full range for better robustness.
# Important because decorators might shift beg_line.
				beg_line = nd.lineno
				end_line = nd.end_lineno if nd.end_lineno is not None else beg_line
				if line in range(beg_line,end_line + 1):
					return qi
	return ""

def _validate_source_fragment(tr: wtrl.tracer,kind: str, source_fragment: str) -> HeaderNode_t:
	try:
		return cast(HeaderNode_t, genutil.parse_source_fragment(cast(genutil.Profile, kind), source_fragment))
	except SyntaxError as e:
		tr.add_error("XTNSN-007","extension","error parsing source_fragment.",{"ast":f"{str(e)}"})
		raise RuntimeError() from e
	except RuntimeError as e:
		tr.add_error("XTNSN-006","extension",str(e))
		raise


def _write_docstring_to_tmp(content: str) -> str:
	tmp_dir = Path(tempfile.gettempdir()) / "waterloo-docstrings"
	tmp_dir.mkdir(parents=True, exist_ok=True)
	with tempfile.NamedTemporaryFile(
		mode="w",
		encoding="utf-8",
		suffix=".txt",
		prefix="waterloo-docstring-",
		delete=False,
		dir=tmp_dir,
	) as handle:
		handle.write(content)
		return str(Path(handle.name))


# A ping is sent by VSCode when the extension is activated,
# e.g. when a Python file is loaded in the Editor panel.
def _handle_ping(tr: wtrl.tracer,version: Any) -> dict[str, Any]:
	if version != 1:
		tr.add_error("XTNSN-003","extension","Unsupported protocol version",{"version":f"{version!r}"})
	if tr.has_errors():
		raise RuntimeError()
	return {
		"ok": True,
		"command": "pong",
		"version": 1,
		"capabilities": [
			"generateMinimalDocstring",
			"generateFullDocstring",
			"validateDocstring",
		],
		"sdv_doc_waterloo": {
			"file":wtrl.__file__,
			"version":wtrl.__version__,
		}
	}


def _handle_generate_minimal(tr: wtrl.tracer,version: Any, kind: Any, source_fragment: Any) -> dict[str, Any]:
	if version != 1:
		tr.add_error("XTNSN-003","extension","Unsupported protocol version",{"version":f"{version!r}"})
	if kind not in {"module", "class", "function", "method"}:
		tr.add_error("XTNSN-004","extension","Unsupported subcommand",{"kind":f"{kind!r}"})
	if not isinstance(source_fragment, str):
		tr.add_error("XTNSN-005","extension","Source fragment must be a string")
	if tr.has_errors():
		raise RuntimeError()

	node = _validate_source_fragment(tr,kind, source_fragment)
	if tr.has_errors():
		raise RuntimeError()
	doc = genutil.generate_minimal_docstring_from_node(cast(genutil.Profile, kind), node)

	tmp_path = _write_docstring_to_tmp(doc)
	return {"kind": kind, "tmp_file": tmp_path}


def _handle_generate_full(tr: wtrl.tracer,version: Any, kind: Any, source_fragment: Any) -> dict[str, Any]:
	if version != 1:
		tr.add_error("XTNSN-003","extension","Unsupported protocol version",{"version":f"{version!r}"})
	if kind not in {"module", "class", "function", "method"}:
		tr.add_error("XTNSN-004","extension","Unsupported subcommand",{"kind":f"{kind!r}"})
	if not isinstance(source_fragment, str):
		tr.add_error("XTNSN-005","extension","Source fragment must be a string")
	if tr.has_errors():
		raise RuntimeError()

	node = _validate_source_fragment(tr,kind, source_fragment)
	if tr.has_errors():
		raise RuntimeError()
	doc = genutil.generate_full_docstring_from_node(cast(genutil.Profile, kind), node)

	tmp_path = _write_docstring_to_tmp(doc)
	return {"kind": kind, "tmp_file": tmp_path}

def _handle_validate(
	tr: wtrl.tracer,
	version: Any,
	kind: Any,
	source_fragment: Any,
	source_file: str,
	line: int,
) -> dict[str, Any]:
	if version != 1:
		tr.add_error("XTNSN-003","extension","Unsupported protocol version",{"version":f"{version!r}"})
	if kind not in {"module", "class", "function", "method"}:
		tr.add_error("XTNSN-004","extension","Unsupported subcommand",{"kind":f"{kind!r}"})
	if not isinstance(source_fragment, str):
		tr.add_error("XTNSN-005","extension","Source fragment must be a string")
	if not isinstance(source_file, str) or not source_file.strip():
		tr.add_error("XTNSN-010","extension","Source file must be a non-empty string.")
	if not isinstance(line, int):
		tr.add_error("XTNSN-011","extension","Line must be an integer.")
	if tr.has_errors():
		raise RuntimeError()

	qi = ""
	if kind == "module":
		qi = Path(source_file).stem
	else:
# Parse source fragment
		node = _validate_source_fragment(tr,kind, source_fragment)
		if tr.has_errors():
			raise RuntimeError()
		if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
			tr.add_error("XTNSN-006","extension","Source fragment does not define a class/function header.")
			raise RuntimeError()
# Parse complete module and qualify the selected object.
		try:
# In ast, line numbers are one-based, hence +1.
			qi = _qualify_documented_object(source_file,node.name,line + 1)
		except Exception as e:
			tr.add_error("XTNSN-008","extension","Could not parse",{"source_file":source_file,"exc":str(e)})
		if tr.has_errors():
			raise RuntimeError()
		if not qi:
			tr.add_error("XTNSN-012","extension","Could not qualify documented object.",{"source_file":source_file,"line":f"{line}"})
			raise RuntimeError()
# Make sure the module is found.
	module_dir = str(Path(source_file).parent)
	sys.path.insert(0,module_dir)
# At this point we have a qualified identifier. Resolve the object.
	try:
		obj,_ = wtrl.resolve_object(qi,None)
	except Exception as e:
		tr.add_error("XTNSN-009","extension","Could not resolve object",{"dir":module_dir,"qi":qi,"exc":str(e)})
	if tr.has_errors():
		raise RuntimeError()
# Validate
	wtrl.validate_docstring(tr,obj)
	if tr.has_errors():
		raise RuntimeError()
	return {"kind": kind, "qualified_identifier": qi}

def _build_diagnostics_summary(diag: dict[str, Any]) -> dict[str, int]:
	debug_entries = diag.get("__WTRL_DEBUG__", [])
	info_entries = diag.get("__WTRL_INFO__", [])
	warn_entries = diag.get("__WTRL_WARNING__", [])
	error_entries = diag.get("__WTRL_ERROR__", [])
	return {
		"debug": len(debug_entries) if isinstance(debug_entries, list) else 0,
		"info": len(info_entries) if isinstance(info_entries, list) else 0,
		"warning": len(warn_entries) if isinstance(warn_entries, list) else 0,
		"error": len(error_entries) if isinstance(error_entries, list) else 0,
	}


def _build_response(
	*,
	ok: bool,
	command: Any,
	version: Any,
	tr: wtrl.tracer,
	data: dict[str, Any] | None = None,
	error: str | None = None,
	include_diagnostics: bool = False,
) -> dict[str, Any]:
	diag_full = tr.build_json(wtrl.tracer.Severity.DEBUG)
	response: dict[str, Any] = {
		"ok": ok,
		"command": command,
		"version": version,
		"diagnostics_summary": _build_diagnostics_summary(diag_full),
	}
	if data is not None:
		response["data"] = data
	if error is not None:
		response["error"] = error
# Full diagnostics can be requested by extension/client or
# is enforced by this backend in case of an error.
	if include_diagnostics or (not ok):
		response["diagnostics"] = diag_full
	return response


def main() -> int:
	tr = wtrl.tracer()
	command: Any = None
	version: Any = None
	include_diagnostics = False
	try:
		payload = json.loads(input())
	except Exception as exc:  # noqa: BLE001
		tr.add_error("XTNSN-001","extension","Invalid JSON input",details={"exc":f"{exc}"})
		print(json.dumps(_build_response(
			ok=False,
			command=command,
			version=version,
			tr=tr,
			error="Invalid JSON input",
			include_diagnostics=True,
		)))
		return 1

	try:
		version = payload.get("version")
		command = payload.get("command")
		include_diagnostics = bool(payload.get("include_diagnostics", False))
# Plugin activation tests Phase-B (Phase-A is performed in extension.js only)
		if command == COMMAND_PING:
			data = _handle_ping(tr,version)
#----- begin useful commands ----------------------------------#
# The response can be specific for each command.
		elif command == COMMAND_GENERATE_MINIMAL:
			data = _handle_generate_minimal(tr,
				version,
				payload.get("kind"),
				payload.get("source_fragment", ""),
			)
		elif command == COMMAND_GENERATE_FULL:
			data = _handle_generate_full(tr,
				version,
				payload.get("kind"),
				payload.get("source_fragment", ""),
			)
		elif command == COMMAND_VALIDATE:
			data = _handle_validate(tr,
				version,
				payload.get("kind"),
				payload.get("source_fragment", ""),
				payload.get("source_file",""),
				payload.get("line",-1),
			)
#----- end useful commands ------------------------------------#
		else:
			tr.add_error("XTNSN-002","extension","Unsupported command",details={"command":f"{command}"})
			print(json.dumps(_build_response(
				ok=False,
				command=command,
				version=version,
				tr=tr,
				error="Unsupported command",
				include_diagnostics=include_diagnostics,
			)))
			return 1
# Write JSON object to stdout (success)
		print(json.dumps(_build_response(
			ok=True,
			command=command,
			version=version,
			tr=tr,
			data=data,
			include_diagnostics=include_diagnostics,
		)))
		return 0
	except Exception as exc:  # noqa: BLE001
# Write JSON object to stdout (failure). The client can identify the response
# as an error by analysing field "$schema" which contains "sci-d-vis.com/schema/wtrl-tracer-json".
		print(json.dumps(_build_response(
			ok=False,
			command=command,
			version=version,
			tr=tr,
			error=str(exc),
			include_diagnostics=include_diagnostics,
		)))
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
