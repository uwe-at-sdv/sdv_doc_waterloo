r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide the entry point for the Waterloo MCP server.
Public_functions:
	read_package_readme, build_app
Function_overview:
	read_package_readme:
		Provide the content of the package README as a string for use as MCP instructions.
	build_app:
		Build the MCP app according to the provided configuration, including loading the configured data roots and defining the MCP tools for accessing them.
"""

from __future__ import annotations

import argparse
import logging
import logging.config
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, cast

try:
	import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
	import tomli as tomllib

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

logger = logging.getLogger("wtrl_mcp")

from sdv.doc.waterloo.mcp import __version__
from sdv.doc.waterloo.mcp.wtrl_tools import (
    DocstringIndentMode_t,
    DocstringJsonMode_t,
    DocstringMode_t,
    DocstringProfile_t,
    ReferenceRecord,
    SearchObjectsFilter,
    SearchSectionsFilter,
    SearchTextFilter,
    gen_docstring,
    get_object,
    get_references,
    get_root,
    get_section,
    get_subsection,
    list_roots,
    search_objects,
    search_sections,
    search_text,
    _canonical_root_path,
    _read_json_document,
	_root_id_for_path,
)

# Run browser-based MCP-inspector with npx @modelcontextprotocol/inspector 

#----- begin helper classes for toml config parsing ----------#
@dataclass(frozen=True)
class ServerConfig:
	"""Parsed configuration for the MCP transport layer."""

	transport: str
	host: str
	port: int
	streamable_http_path: str


@dataclass(frozen=True)
class SecurityConfig:
	"""Parsed configuration for browser and host allowlisting."""

	allowed_hosts: list[str]
	allowed_origins: list[str]


@dataclass(frozen=True)
class LoggingConfig:
	"""Parsed configuration for logging behavior."""

	level: str
	config_path: Path | None
	access_log: bool | None


@dataclass(frozen=True)
class RootConfig:
	"""Parsed configuration for one Waterloo data root."""

	path: str
	label: str
	enabled: bool
	kind: str


@dataclass(frozen=True)
class RootMTimeRecord:
	"""Cached modification timestamp information for one Waterloo root."""

	root_id: str
	root_path: str
	mtime_ns: int | None


@dataclass(frozen=True)
class ReferenceIndex:
	"""Cached reverse reference map and root modification timestamps."""

	reverse_map: dict[tuple[str, str], list[ReferenceRecord]]
	root_mtimes: dict[str, RootMTimeRecord]


@dataclass(frozen=True)
class McpConfig:
	"""Parsed Waterloo MCP configuration."""

	server: ServerConfig
	security: SecurityConfig
	logging: LoggingConfig
	roots: list[RootConfig]
	source_path: Path

#----- end helper classes for toml config parsing ------------#

def read_package_readme() -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| resolve a resource path to the package |file|`README` file.
			|Must| read and return the content of the |file|`README` file for use as MCP instructions.
	Notes:
		Purpose:
			This is a simple way to provide rich instructions for the MCP server without hardcoding them in the source.
			The README can be edited as needed to update the instructions without touching the code.
		Usage:
			The string returned by this function is passes as the `instructions` parameter
			when building the MCP app, making it visible to clients in the MCP session metadata.
	Parameters:
	Returns:
		The content of the |file|`README` file as a string.
	Raises:
		FileNotFoundError:
			|may| raise if the |file|`README` file does not exist.
	"""
	path = Path(__file__).resolve().with_name("README")
	try:
		return path.read_text(encoding="utf-8").strip()
	except Exception:
		return "Waterloo MCP server"


def build_parser() -> argparse.ArgumentParser:
	"""Build the CLI parser for the config-driven MCP server."""
	prsr = argparse.ArgumentParser(prog="wtrl_mcp", description="Waterloo MCP server")
	prsr.add_argument(
		"--config",
		type=Path,
		help="Path to a Waterloo MCP TOML configuration file.",
	)
	prsr.add_argument(
		"--gen-config-template",
		action="store_true",
		help="Print a TOML configuration template to stdout and exit.",
	)
	prsr.add_argument(
		"--version",
		action="version",
		version=f"wtrl_mcp {__version__}",
	)
	return prsr


def _default_config_path() -> Path:
	return Path(__file__).resolve().with_name("wtrl_mcp.toml")


def _package_root() -> Path:
	return Path(__file__).resolve().parent.parent


def _template_text() -> str:
	return """# Waterloo MCP server configuration template
#
# Save this under etc/ as wtrl_mcp.http.toml or wtrl_mcp.stdio.toml and edit it.
# Relative paths are resolved against the current directory and the installed
# Waterloo package root, so the etc/ prefix is intentional.

[server]
# transport = "stdio"
transport = "streamable-http"
# host = "127.0.0.1"
host = "127.0.0.1"
# port = 8000
port = 8000
# streamable_http_path = "/mcp"
streamable_http_path = "/mcp"

[security]
# allowed_hosts = ["127.0.0.1:8000"]
allowed_hosts = ["127.0.0.1:8000"]
# allowed_origins = ["http://localhost:6274"]
allowed_origins = ["http://gilgamesh:6274"]

[logging]
# level = "INFO"
# config_path = "package_main/src/sdv/doc/waterloo/mcp/logging.toml"
# access_log = true

[[roots]]
# Possible kind at current state of development: wtrl-json.
path = "doc-json/wtrl-mcp.wtrl.core.rfc-2119.json"
label = "Waterloo MCP Server and Tool set Reference"
enabled = true
kind = "wtrl-json"

# [[roots]]
# path = "/tmp/other-waterloo-root"
# label = "Other root"
# enabled = false
# kind = "directory"
"""


def _load_toml(path: Path) -> Mapping[str, object]:
	with path.open("rb") as fh:
		return cast(Mapping[str, object], tomllib.load(fh))


def _load_logging_config(path: Path) -> dict[str, object]:
	"""Load a logging configuration file for uvicorn."""
	if path.suffix.lower() == ".toml":
		with path.open("rb") as fh:
			return cast(dict[str, object], tomllib.load(fh))
	raise ValueError(f"Unsupported logging config format: {path}")


def _configure_waterloo_logging(config: McpConfig) -> None:
	"""Install the configured Waterloo logging dictionary before startup messages."""
	if config.logging.config_path is None:
		return
	logging.config.dictConfig(_load_logging_config(config.logging.config_path))


def _root_mtime_record(root_id: str, root_path: Path) -> RootMTimeRecord:
	try:
		mtime_ns = root_path.stat().st_mtime_ns
	except OSError:
		mtime_ns = None
	return RootMTimeRecord(root_id=root_id, root_path=str(root_path), mtime_ns=mtime_ns)


def _doc_profile(object_record: Mapping[str, object]) -> str | None:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return None
	preamble = doc.get("Preamble", {})
	if not isinstance(preamble, Mapping):
		return None
	profile = preamble.get("profile")
	if isinstance(profile, str):
		profile = profile.strip()
		return profile or None
	return None


def _doc_normative_sections(object_record: Mapping[str, object]) -> set[str]:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return set()
	preamble = doc.get("Preamble", {})
	if not isinstance(preamble, Mapping):
		return set()
	sections = preamble.get("normative_sections", [])
	if not isinstance(sections, list):
		return set()
	return {str(section).strip() for section in sections if str(section).strip()}


def _doc_see_also_refs(object_record: Mapping[str, object]) -> list[str]:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return []
	see_also = doc.get("See_also")
	if not isinstance(see_also, list):
		return []
	return [str(item).strip() for item in see_also if str(item).strip()]


def _resolve_reference_targets(
	ref: str,
	source_root_id: str,
	source_qid: str,
	qids_to_roots: Mapping[str, set[str]],
) -> list[tuple[str, str]]:
	candidates: list[str] = []
	if "." in ref:
		candidates.append(ref)
	if "." in source_qid:
		candidates.append(f"{source_qid.rsplit('.', 1)[0]}.{ref}")
	else:
		candidates.append(f"{source_qid}.{ref}")
	candidates.append(ref)

	resolved: list[tuple[str, str]] = []
	seen_candidates: set[str] = set()
	for cand in candidates:
		if cand in seen_candidates:
			continue
		seen_candidates.add(cand)
		root_ids = qids_to_roots.get(cand)
		if not root_ids:
			continue
		if source_root_id in root_ids:
			resolved.append((source_root_id, cand))
			continue
		if len(root_ids) == 1:
			root_id = next(iter(root_ids))
			resolved.append((root_id, cand))
	return resolved


def _build_reference_index(roots: list[RootConfig]) -> ReferenceIndex:
	reverse_map: dict[tuple[str, str], list[ReferenceRecord]] = {}
	root_mtimes: dict[str, RootMTimeRecord] = {}
	objects_by_root: dict[str, list[tuple[str, Mapping[str, object]]]] = {}
	qids_to_roots: dict[str, set[str]] = {}

	for root in roots:
		if not root.enabled:
			continue
		root_path = _canonical_root_path(root.path)
		root_id = _root_id_for_path(str(root_path))
		root_mtimes[root_id] = _root_mtime_record(root_id, root_path)
		try:
			document = _read_json_document(str(root_path))
		except Exception:
			continue
		if not isinstance(document, Mapping):
			continue
		objects = document.get("__WTRL_OBJECTS__", {})
		if not isinstance(objects, Mapping):
			continue
		root_objects: list[tuple[str, Mapping[str, object]]] = []
		for qid, object_record in objects.items():
			if not isinstance(object_record, Mapping):
				continue
			qid_text = str(qid)
			root_objects.append((qid_text, object_record))
			qids_to_roots.setdefault(qid_text, set()).add(root_id)
		objects_by_root[root_id] = root_objects

	for root_id, root_objects in objects_by_root.items():
		for qid_text, object_record in root_objects:
			source_profile = _doc_profile(object_record)
			if source_profile not in {"module", "class", "function", "method"}:
				continue
			refs = _doc_see_also_refs(object_record)
			if not refs:
				continue
			is_normative = "See_also" in _doc_normative_sections(object_record)
			source_record = ReferenceRecord(
				source_root_id=root_id,
				source_qid=qid_text,
				source_profile=source_profile,
				is_normative=is_normative,
			)
			for ref in refs:
				for target_root_id, target_qid in _resolve_reference_targets(ref, root_id, qid_text, qids_to_roots):
					reverse_map.setdefault((target_root_id, target_qid), []).append(source_record)

	for records in reverse_map.values():
		records.sort(key=lambda record: (record.source_root_id, record.source_qid, record.source_profile))
	return ReferenceIndex(reverse_map=reverse_map, root_mtimes=root_mtimes)


def _resolve_config_path(config_path: Path | None) -> Path:
	if config_path is None:
		return _default_config_path()
	if config_path.is_absolute():
		return config_path
	candidates = [
		Path.cwd() / config_path,
		_package_root() / config_path,
	]
	for candidate in candidates:
		if candidate.exists():
			return candidate
	return config_path

def _parse_roots(raw_roots: object, config_dir: Path) -> list[RootConfig]:
	roots: list[RootConfig] = []
	if not isinstance(raw_roots, list) or not raw_roots:
		raise ValueError("Configuration file must contain at least one [[roots]] entry.")
	for item in raw_roots:
		if not isinstance(item, Mapping):
			raise ValueError("Each [[roots]] entry must be a table.")
		path_text = str(item.get("path", "")).strip()
		if not path_text:
			raise ValueError("Each [[roots]] entry needs a path.")
		path = Path(path_text).expanduser()
		if not path.is_absolute():
			path = (config_dir / path).expanduser()
		path = path.resolve()
		roots.append(
			RootConfig(
				path=str(path),
				label=str(item.get("label") or path.name or str(path)),
				enabled=bool(item.get("enabled", True)),
				kind=str(item.get("kind") or "directory"),
			)
		)
	return roots


def load_config(config_path: Path | None = None) -> McpConfig:
	"""Load a Waterloo MCP TOML configuration file."""
	path = _resolve_config_path(config_path)
	if not path.exists():
		if config_path is not None and not config_path.is_absolute():
			raise FileNotFoundError(
				"Waterloo MCP configuration file not found: "
				f"{config_path} (searched {Path.cwd() / config_path} and {_package_root() / config_path})"
			)
		raise FileNotFoundError(f"Waterloo MCP configuration file not found: {path}")
	raw = _load_toml(path)
	if not isinstance(raw, Mapping):
		raise ValueError("Waterloo MCP configuration file must contain a TOML table.")
	server_data = raw.get("server", {})
	security_data = raw.get("security", {})
	logging_data = raw.get("logging", {})
	roots_data = raw.get("roots", [])
	if not isinstance(server_data, Mapping):
		raise ValueError("[server] must be a TOML table.")
	if not isinstance(security_data, Mapping):
		raise ValueError("[security] must be a TOML table.")
	if not isinstance(logging_data, Mapping):
		raise ValueError("[logging] must be a TOML table.")
	config_dir = path.parent.resolve()
	server = ServerConfig(
		transport=str(server_data.get("transport", "stdio")).strip().lower(),
		host=str(server_data.get("host", "127.0.0.1")),
		port=int(server_data.get("port", 8000)),
		streamable_http_path=str(server_data.get("streamable_http_path", "/mcp")),
	)
	if server.transport not in {"stdio", "streamable-http"}:
		raise ValueError('[server].transport must be "stdio" or "streamable-http".')
	security = SecurityConfig(
		allowed_hosts=[str(item) for item in security_data.get("allowed_hosts", [])],
		allowed_origins=[str(item) for item in security_data.get("allowed_origins", [])],
	)
	logging_cfg = LoggingConfig(
		level=str(logging_data.get("level", "INFO")).strip().upper(),
		config_path=(
			(Path(str(logging_data["config_path"])).expanduser() if logging_data.get("config_path") else None)
		),
		access_log=logging_data.get("access_log"),
	)
	if logging_cfg.config_path and not logging_cfg.config_path.is_absolute():
		logging_cfg = LoggingConfig(
			level=logging_cfg.level,
			config_path=(config_dir / logging_cfg.config_path).resolve(),
			access_log=logging_cfg.access_log,
		)
	roots = _parse_roots(roots_data, config_dir)
	return McpConfig(server=server, security=security, logging=logging_cfg, roots=roots, source_path=path)


def build_app(config: McpConfig) -> FastMCP:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| build an MCP app according to the provided configuration.
	Parameters:
		config:
			The loaded MCP configuration according to which the app should be built.
	Returns:
		The built MCP app.
	Raises:
		ValueError:
			|May| raise if the configuration is invalid in any way.
	"""
	"""Build the Waterloo MCP app with the configured data roots."""
	reference_index = _build_reference_index(config.roots)

	mcp = FastMCP(
		name="wtrl_mcp",
		instructions=read_package_readme(),
		debug=False,
		log_level=config.logging.level,
		host=config.server.host,
		port=config.server.port,
		streamable_http_path=config.server.streamable_http_path,
	)
	setattr(mcp, "_waterloo_reference_index", reference_index)
	if config.security.allowed_hosts or config.security.allowed_origins:
		mcp.settings.transport_security = TransportSecuritySettings(
			enable_dns_rebinding_protection=True,
			allowed_hosts=list(config.security.allowed_hosts),
			allowed_origins=list(config.security.allowed_origins),
		)

	def _root_mappings() -> list[Mapping[str, object]]:
		return [
			{
				"path": root.path,
				"label": root.label,
				"enabled": root.enabled,
				"kind": root.kind,
			}
			for root in config.roots
		]

	@mcp.tool(name="list_roots", description="List configured Waterloo data roots.")
	def _list_roots() -> list[dict[str, object]]:
		return list_roots(_root_mappings())

	@mcp.tool(name="get_root", description="Read one configured Waterloo data root by root_id.")
	def _get_root(root_id: str) -> dict[str, object]:
		return get_root(root_id, _root_mappings())

	@mcp.tool(name="get_object", description="Read one Waterloo object by qid from a configured root.")
	def _get_object(root_id: str, qid: str) -> dict[str, object]:
		return get_object(root_id, qid, _root_mappings())

	@mcp.tool(name="get_section", description="Read one stored section of one Waterloo object.")
	def _get_section(root_id: str, qid: str, section: str) -> dict[str, object]:
		return get_section(root_id, qid, section, _root_mappings())

	@mcp.tool(name="get_subsection", description="Read one stored subsection of one Waterloo object.")
	def _get_subsection(root_id: str, qid: str, section: str, subsection: str) -> dict[str, object]:
		return get_subsection(root_id, qid, section, subsection, _root_mappings())

	@mcp.tool(name="get_references", description="Read structured incoming See_also references for one Waterloo object.")
	def _get_references(root_id: str, qid: str, normative_only: bool = False) -> list[ReferenceRecord]:
		return get_references(reference_index.reverse_map, root_id, qid, normative_only)

	@mcp.tool(name="search_objects", description="Search Waterloo objects by expression and structural filters.")
	def _search_objects(expression: str, filter: SearchObjectsFilter | None = None) -> list[tuple[str, str, str]]:
		return search_objects(expression, _root_mappings(), filter)

	@mcp.tool(name="search_sections", description="Search Waterloo section and subsection labels by expression and structural filters.")
	def _search_sections(expression: str, filter: SearchSectionsFilter | None = None) -> list[dict[str, object]]:
		return search_sections(expression, _root_mappings(), filter)

	@mcp.tool(name="search_text", description="Search Waterloo text content by terms and structural filters.")
	def _search_text(terms: list[str], filter: SearchTextFilter | None = None) -> list[dict[str, object]]:
		return search_text(terms, _root_mappings(), filter)

	@mcp.tool(name="gen_docstring", description="Generate a Waterloo docstring template for a given profile.")
	def _gen_docstring(
		profile: DocstringProfile_t,
		signature: str | None = None,
		mode: DocstringMode_t = "minimal",
		indent_mode: DocstringIndentMode_t = "tab",
		json_mode: DocstringJsonMode_t = "full",
	) -> dict[str, object]:
		return gen_docstring(profile=profile, signature=signature, mode=mode, indent_mode=indent_mode, json_mode=json_mode)

	logger.info("Ready to serve via Uvicorn.")
	logger.info(f"Loaded {len(config.roots)} configured roots.")
	for root in config.roots:
		logger.info(f"Configured root: {root.path} '{root.label}' (enabled={root.enabled}, kind={root.kind})")
	logger.info(
		"Built reference index with %d target entries and %d source references.",
		len(reference_index.reverse_map),
		sum(len(records) for records in reference_index.reverse_map.values()),
	)
	return mcp


def _wrap_browser_cors(app: ASGIApp, origins: list[str]) -> ASGIApp:
	"""Wrap an ASGI app with permissive browser CORS for MCP Inspector use."""
	return CORSMiddleware(
		app,
		allow_origins=origins,
		allow_methods=["GET", "POST", "DELETE"],
		allow_headers=["*"],
		expose_headers=["Mcp-Session-Id"],
	)


def _print_config_error(exc: Exception) -> None:
	"""Print a user-facing configuration error."""
	print(f"wtrl_mcp: {exc}", file=sys.stderr)


def _run_loaded_config(config: McpConfig) -> None:
	"""Run the server according to a loaded configuration."""
	_configure_waterloo_logging(config)
	mcp = build_app(config)
	if config.server.transport == "streamable-http":
		http_app = mcp.streamable_http_app()
		if config.security.allowed_origins:
			http_app = _wrap_browser_cors(http_app, list(config.security.allowed_origins))
		# Streamable HTTP is exposed directly here so browser clients can
		# negotiate CORS. SSE stays out of v1.
		uvicorn.run(
			http_app,
			host=config.server.host,
			port=config.server.port,
			log_level=config.logging.level.lower(),
			access_log=bool(config.logging.access_log) if config.logging.access_log is not None else True,
			log_config=_load_logging_config(config.logging.config_path) if config.logging.config_path else None,
		)
		return

	# Stdio is the default development transport.
	mcp.run(transport="stdio")


class _McpAppProxy:
	"""Lazy server proxy used by the MCP CLI wrappers."""

	dependencies: list[str] = []

	def __init__(self, config_path: Path | None = None) -> None:
		self._config_path = config_path or _default_config_path()

	def run(self, transport: str | None = None) -> None:
		try:
			config = load_config(self._config_path)
		except (FileNotFoundError, ValueError) as exc:
			_print_config_error(exc)
			raise SystemExit(1) from exc
		if transport is not None:
			config = McpConfig(
				server=ServerConfig(
					transport=transport,
					host=config.server.host,
					port=config.server.port,
					streamable_http_path=config.server.streamable_http_path,
				),
				security=config.security,
				logging=config.logging,
				roots=config.roots,
				source_path=config.source_path,
			)
		_run_loaded_config(config)


app = _McpAppProxy()


def main(argv: list[str] | None = None) -> int:
	"""Start the Waterloo MCP server."""
	args = build_parser().parse_args(argv)
	if args.gen_config_template:
		print(_template_text())
		return 0
	try:
		config = load_config(args.config)
	except (FileNotFoundError, ValueError) as exc:
		_print_config_error(exc)
		return 1
	_run_loaded_config(config)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
