r"""
	Preamble:
		profile:
			module
		normative_sections:
			Contract, Public_classes, Public_functions, Public_constants, Public_variables
		scope:
			public
	Contract:
		general:
			|Must| provide the entry point for the Waterloo MCP server.
	Public_classes:
		ServerConfig, SecurityConfig, AuthConfig, LoggingConfig, RootConfig, _RequestLogGroupMiddleware, RootMTimeRecord, ReferenceIndex, McpConfig, McpAppRunner
	Class_overview:
		ServerConfig:
			Parsed configuration for the MCP transport layer.
		SecurityConfig:
			Parsed configuration for browser and host allowlisting.
		AuthConfig:
			Parsed configuration for MCP bearer-token support and token-store location.
		LoggingConfig:
			Parsed configuration for logging behavior.
		RootConfig:
			Parsed configuration for one Waterloo data root.
		_RequestLogGroupMiddleware:
			Internal ASGI middleware that assigns a request id and log-group key to each HTTP request so the server logs can be grouped per request.
		RootMTimeRecord:
			Per-run snapshot of the root identifier, canonical root path, and cached modification timestamp.
		ReferenceIndex:
			Per-run cache for reverse references, qid-to-root membership, and root modification timestamps.
		McpConfig:
			Normalized runtime configuration for the MCP server, including transport, security, auth, logging, and configured roots.
		McpAppRunner:
			Public launcher object that loads the configuration and starts the MCP server; its `run` method is part of the entry-point API.
	Public_functions:
		read_package_readme, load_prompts, build_reference_index, build_app, load_config, parse_roots
	Function_overview:
		read_package_readme:
			Provide the content of the package README as a string for use as MCP instructions.
		load_prompts:
			Load the bundled MCP prompt templates from the package resources and return them as FastMCP prompt objects.
		build_reference_index:
			Build the reverse-reference index for all enabled roots, including qid-to-root membership and cached root mtimes.
		build_app:
			Build the MCP app according to the provided configuration, including loading the configured data roots and defining the MCP tools for accessing them.
		load_config:
			Load and validate a Waterloo MCP TOML configuration file, returning a normalized McpConfig object for server startup.
		parse_roots:
			Parse and validate the roots configuration, returning a list of RootConfig objects.
	Public_constants:
		WTRL_TOOL_DOCS:
			A global registry mapping canonical tool names to their unwrapped function objects
	Public_variables:
		logger:
			A module-level logger for the Waterloo MCP server.
	Notes:
		Admin_api:
			When auth is enabled, the server also exposes loopback-only `/admin` routes for token
			management in the configured JSON token store. These routes live in the same HTTP
			application as the MCP endpoint.
		Token_store:
			The token store path is resolved from the server configuration and used by both the
			bearer-token verifier and the admin routes.
	Terminology:
		CORS:
			Cross-Origin Resource Sharing, a security feature implemented by browsers to control how resources
			are requested from different origins. The server's CORS policy is determined by the allowed origins configuration.
		ASGI:
			Asynchronous Server Gateway Interface, a standard interface between async Python web servers and applications.
		Starlette:
			A lightweight ASGI framework used to build the MCP server app.
		FastMCP:
			A Python library that implements the Model Context Protocol (MCP) server and client functionality.
		Uvicorn:
			A lightning-fast ASGI server implementation used to run the MCP server app.
"""

from __future__ import annotations

import argparse
import json
import os
import importlib.resources
import inspect
import logging
import logging.config
from functools import lru_cache
import re
import tempfile
import sys
import textwrap
from string import Template
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Literal, Mapping, cast

from jsonschema import Draft202012Validator

try:
	import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
	import tomli as tomllib

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Route is a class that represents a single route in the Starlette application.
# It is used to define the path, endpoint, and methods for handling HTTP requests.
from starlette.routing import Route

from starlette.types import ASGIApp, Receive, Scope, Send

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import Message, Prompt, PromptArgument
from mcp.server.fastmcp.server import TransportSecuritySettings
from mcp.server.auth.settings import AuthSettings
from mcp.types import TextContent, ToolAnnotations

LogLevel_t = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

from sdv.doc.waterloo.mcp import __version__
from sdv.doc.waterloo.mcp.wtrl_tools import (
    DocstringIndentMode_t,
    DocstringJsonMode_t,
    DocstringMode_t,
    DocstringProfile_t,
    about,
    ExampleRef,
    ObjectSummary,
    ReferenceRecord,
    RelatedRecord,
    SearchObjectsFilter,
    SearchSectionsFilter,
    SearchTextFilter,
    gen_docstring,
    get_object,
    get_examples,
    get_example_source,
    get_signature,
    get_root_metadata,
    get_references,
    get_root,
    get_section,
    get_subsection,
    list_objects,
    list_roots,
    search_objects,
    search_related,
    search_sections,
    search_text,
    _canonical_root_path,
    _read_json_document,
    _root_id_for_path,
    WtrlJsonNode_t,
)
from sdv.doc.waterloo.mcp.wtrl_logging import (
    allocate_request_id,
    set_log_group_key,
    reset_log_group_key,
    reset_request_id,
    set_request_id,
)
from sdv.doc.waterloo.mcp.wtrl_auth import (
	AuthTokenConflictError,
	AuthTokenNotFoundError,
	AuthTokenValidationError,
	FileTokenVerifier,
	create_token,
	list_tokens,
	revoke_token,
)

# Run browser-based MCP-inspector with npx @modelcontextprotocol/inspector 

#----- begin constants and global variables ------------------#
logger = logging.getLogger("wtrl_mcp")
ADMIN_ENDPOINT_BASE: Final[str] = "/admin"
ADMIN_LOOPBACK_ONLY_ERROR: Final[str] = "The /admin API is loopback-only in v1."
_SERVER_IDENTITY_RE = re.compile(r"^[-_a-zA-Z][-_a-zA-Z0-9+]*$")

# Global tool documentation registry
WTRL_TOOL_DOCS: Final[dict[str, Callable[..., object] | None]] = {
	"list_roots": list_roots,
	"get_root": get_root,
	"get_root_metadata": get_root_metadata,
	"get_object": get_object,
	"get_section": get_section,
	"get_subsection": get_subsection,
	"list_objects": list_objects,
	"get_examples": get_examples,
	"get_example_source": get_example_source,
	"get_signature": get_signature,
	"get_references": get_references,
	"search_related": search_related,
	"search_objects": search_objects,
	"search_sections": search_sections,
	"search_text": search_text,
	"gen_docstring": gen_docstring,
	"about": about,
	"describe_tool": None,  # Will be set after function definition
}
#----- end constants and global variables --------------------#

#----- begin helper classes for toml config parsing ----------#
@dataclass(frozen=True)
class ServerConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the parsed configuration for the MCP transport layer.
			|Must| bundle the transport settings needed to start the server.
		constructor:
			|Must| be constructible from parsed transport settings.
	Public_variables:
		identity:
			Stores the optional stable server identity.
		transport:
			Stores the configured transport mode.
		host:
			Stores the configured host name or address. A value of |value|`0.0.0.0`
			means the server will listen on all interfaces (see Security notes).
		port:
			Stores the configured bind port. The default is |value|`13316`,
			which is the standard port for the Waterloo MCP server.
		streamable_http_path:
			Stores the configured streamable HTTP path.
	Notes:
		Security:
			Binding to |value|`0.0.0.0` is a security risk if the server is exposed to untrusted networks.
	"""

	identity: str | None
	transport: str
	host: str
	port: int
	streamable_http_path: str


@dataclass(frozen=True)
class SecurityConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the parsed configuration for browser and host allowlisting.
			|Must| bundle the effective allowlist values used by the server.
		constructor:
			|Must| be constructible from parsed host and origin allowlists.
	Terminology:
		CORS:
			Cross-Origin Resource Sharing, a security feature implemented by browsers to control how resources
			are requested from different origins. The server's CORS policy is determined by the allowed origins configuration.
	Public_variables:
		allowed_hosts:
			Stores the configured host allowlist.
		allowed_origins:
			Stores the configured origin allowlist. This is important for clients like the MCP Inspector
			which connect to the server via a browser and need to be allowed by the server's CORS policy.
	Notes:
		Security:
			Host and origin allowlists are important for security when the server is exposed to untrusted networks.
			If both allowlists are empty, the server will accept requests from any host or origin, which makes
			it vulnerable to dns rebinding attacks and other security risks.
	"""

	allowed_hosts: list[str]
	allowed_origins: list[str]


@dataclass(frozen=True)
class AuthConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the parsed configuration for MCP bearer-token support.
			|Must| bundle the effective enabled flag, token-store path, and realm label.
		constructor:
			|Must| be constructible from parsed auth settings.
	Public_variables:
		enabled:
			Stores whether MCP bearer-token support is enabled.
		token_store_path:
			Stores the resolved path to the JSON token-store file.
		realm:
			Stores the realm label used in auth-related responses.
	Notes:
		Default_store:
			When the configuration does not specify a token store path, the server uses
			``$XDG_STATE_HOME/wtrl_mcp/tokens.json`` if ``XDG_STATE_HOME`` is set, otherwise
			``~/.local/state/wtrl_mcp/tokens.json``.
	"""

	enabled: bool
	token_store_path: Path
	realm: str


@dataclass(frozen=True)
class LoggingConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the parsed configuration for logging behavior.
			|Must| bundle the logging settings used by the server startup path.
		constructor:
			|Must| be constructible from the selected logging level, config path, and access-log toggle.
	Public_variables:
		level:
			Stores the configured logging level.
		config_path:
			Stores the optional path to a logging config file.
		access_log:
			Stores the optional access-log toggle.
	"""

	level: str
	config_path: Path | None
	access_log: bool | None


@dataclass(frozen=True)
class RootConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the parsed configuration for one Waterloo data root.
			|Must| keep the fields normalized so the server can resolve roots consistently.
		constructor:
			|Must| be constructible from a root path, label, enabled flag, and kind.
	Public_variables:
		path:
			Stores the resolved root path as text.
		label:
			Stores the human-readable root label.
		enabled:
			Stores whether the root is active.
		kind:
			Stores the configured root kind.
	"""

	path: str
	label: str
	enabled: bool
	kind: str


@dataclass(frozen=True)
class RootMTimeRecord:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the cached modification-time snapshot for one Waterloo root.
			|Must| remember the root identifier, canonical root path, and modification timestamp.
		constructor:
			|Must| be easy to construct from a root id and canonical path.
	Public_variables:
		root_id:
			Stores the stable root identifier.
		root_path:
			Stores the canonical root path as text.
		mtime_ns:
			Stores the modification timestamp in nanoseconds or |None| if the timestamp could not be read.
	"""

	root_id: str
	root_path: str
	mtime_ns: int | None


@dataclass(frozen=True)
class ReferenceIndex:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the per-run reverse-reference data used by the MCP server.
			|Must| cache the mapping from target object to incoming reference records.
			|Must| cache which root IDs contain each qid.
			|Must| cache modification timestamps for roots that were inspected.
		constructor:
			|Must| be easy to construct from freshly built reverse-reference data.
	Public_variables:
		reverse_map:
			Maps (root_id, qid) pairs to incoming reference records.
		qids_to_roots:
			Maps qids to the set of root IDs that contain them.
		root_mtimes:
			Maps root IDs to their cached modification-time records.
	"""

	reverse_map: dict[tuple[str, str], list[ReferenceRecord]]
	qids_to_roots: dict[str, set[str]]
	root_mtimes: dict[str, RootMTimeRecord]


@dataclass(frozen=True)
class McpConfig:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables
	Contract:
		general:
			|Must| hold the normalized runtime configuration for the MCP server.
			|Must| bundle transport, security, auth, logging, configured roots, and the source path of the loaded configuration.
		constructor:
			|Must| be constructible from the parsed configuration objects and the resolved source path.
	Public_variables:
		server:
			stores the parsed transport settings.
		security:
			stores the parsed host and origin allowlists.
		auth:
			stores the parsed bearer-token configuration.
		logging:
			stores the parsed logging settings.
		roots:
			stores the normalized root entries.
		source_path:
			stores the resolved configuration file path.
	"""
	server: ServerConfig
	security: SecurityConfig
	auth: AuthConfig
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
		"--port",
		type=int,
		help="Override the internal server bind port.",
	)
	prsr.add_argument(
		"--public-port",
		type=int,
		help="Override the external/public port used for host allowlists and generated URLs.",
	)
	prsr.add_argument(
		"--allowed-hosts",
		nargs="+",
		metavar="HOST",
		help="Override the host allowlist; bare host names are normalized to the active server port, or to --public-port when set.",
	)
	prsr.add_argument(
		"--version",
		action="version",
		version=f"{__version__}",
	)
	return prsr


def _default_config_path() -> Path:
	return Path(__file__).resolve().with_name("wtrl_mcp.toml")


def _package_root() -> Path:
	return Path(__file__).resolve().parent.parent


def _default_auth_token_store_path() -> Path:
	"""Return the default JSON token-store path for MCP bearer tokens."""
	xdg_state_home = os.environ.get("XDG_STATE_HOME", "").strip()
	if xdg_state_home:
		base = Path(xdg_state_home).expanduser()
	else:
		base = Path("~/.local/state").expanduser()
	return (base / "wtrl_mcp" / "tokens.json").resolve()


def _format_os_error(exc: OSError) -> str:
	errno_text = f" {exc.errno}" if exc.errno is not None else ""
	strerror = exc.strerror or str(exc)
	return f"{exc.__class__.__name__}{errno_text}: {strerror}"


def _validate_auth_token_store_path(token_store_path: Path) -> None:
# Must not point to an existing directory.
	if token_store_path.exists() and token_store_path.is_dir():
		raise ValueError(
			"Auth token store path must point to a file, not a directory: "
			f"{token_store_path}. Create a file path instead."
		)
# At least the parent directory of the token store path must exist.
# We will not create paths for the token store file.
	if not token_store_path.parent.exists():
		raise ValueError(
			"Auth token store directory does not exist: "
			f"{token_store_path.parent}. Create the directory first or change auth.token_store."
		)
	try:
# If there is a token store file, it must be readable and writable.
		if token_store_path.exists():
			with token_store_path.open("r", encoding="utf-8"):
				pass
			with token_store_path.open("a", encoding="utf-8"):
				pass
# If there is no such file, we must be able to create it.
		else:
			probe_path: Path | None = None
			try:
				with tempfile.NamedTemporaryFile(
					mode="w",
					encoding="utf-8",
					dir=token_store_path.parent,
					prefix=f".{token_store_path.name}.",
					suffix=".probe",
					delete=False,
				) as probe_fh:
					probe_path = Path(probe_fh.name)
			finally:
				if probe_path is not None:
					try:
						probe_path.unlink()
					except FileNotFoundError:
						pass
	except OSError as exc:
		raise ValueError(
			"Validating auth token store file: "
			f"{token_store_path}. Auth token store file must be readable and writable: "
			f"Fix the file permissions or change auth.token_store. ({_format_os_error(exc)})"
		) from exc


def _validate_auth_token_store_contents(token_store_path: Path) -> None:
	if not token_store_path.exists():
		return
	schema_path = importlib.resources.files("sdv.doc.waterloo") / "schema" / "wtrl-mcp-auth-token-store-json-0.1.0.schema.json"
	schema = json.loads(Path(str(schema_path)).read_text(encoding="utf-8"))
	doc = json.loads(token_store_path.read_text(encoding="utf-8"))
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(doc), key=lambda exc: list(exc.path))
	if errors:
		raise ValueError(
			f"Validating auth token store file: {token_store_path}. "
			f"Auth token store file is invalid: {errors[0].message}"
		)


def _auth_token_stats(token_store_path: Path) -> tuple[int, int]:
	tokens = list_tokens(token_store_path)
	valid = 0
	for token in tokens:
		if str(token.get("revoked_at") or "") == "":
			valid += 1
	revoked = len(tokens) - valid
	return valid, revoked


def _auth_issuer_url(config: McpConfig) -> str:
	host = config.server.host.strip() or "127.0.0.1"
	if host in {"0.0.0.0", "::"}:
		host = "127.0.0.1"
	return f"http://{host}:{config.server.port}/auth"


def _logging_toml_resource_path() -> str:
	"""Resolve the absolute path to the installed etc/logging.toml package resource."""
	ref = importlib.resources.files("sdv.doc.waterloo").joinpath("etc/logging.toml")
	return str(ref)


def _default_root_json_resource_path() -> str:
	"""Resolve the absolute path to the installed mcp/doc-json default root JSON resource."""
	ref = importlib.resources.files("sdv.doc.waterloo.mcp").joinpath("doc-json/wtrl_mcp.wtrl.core.rfc-2119.json")
	return str(ref)


def _template_text() -> str:
	logging_toml = _logging_toml_resource_path()
	default_root_json = _default_root_json_resource_path()
	default_token_store = _default_auth_token_store_path()
	return f"""# Waterloo MCP server configuration template
#
# Save this under etc/ as wtrl_mcp.http.toml or wtrl_mcp.stdio.toml and edit it.
# Relative paths are resolved against the current directory and the installed
# Waterloo package root, so the etc/ prefix is intentional.
#
# A sequence like
# $ wtrl_mcp --gen-config-template > /tmp/mcp.toml
# $ wtrl_mcp --config /tmp/mcp.toml
# should run out of the box with the default configuration,
# which includes one root with the default root JSON resource.

[server]
# identity = "wtrl_mcp"
# Set identity explicitly when auth.enabled = true.
# Choose a descriptive, preferably host-unique identity so the server can be
# identified reliably across different hosts and admin registries.
# transport = "stdio"
transport = "streamable-http"
# host = "127.0.0.1"
host = "127.0.0.1"
# port = 8000
port = 13316
# streamable_http_path = "/mcp"
streamable_http_path = "/mcp"

[security]
# allowed_hosts = ["127.0.0.1:8000"]
allowed_hosts = ["127.0.0.1:13316", "localhost:13316"]
# Enter your allowed origins here. This is important if you want to inspect
# the MCP server with a browser-based client like the MCP Inspector.
allowed_origins = ["http://myhost:6274"]

[logging]
# Provide either level and access_log, or config_path.
# level = "INFO"
# access_log = true
config_path = \"{logging_toml}\"

[auth]
enabled = false
token_store = \"{default_token_store}\"
realm = "Waterloo MCP"

[[roots]]
# Possible kind at current state of development: wtrl-json.
# This is a default path in order to get started quickly,
# but you can change it to point to any valid Waterloo JSON file.
path = \"{default_root_json}\"
label = "Waterloo MCP Server and Toolset Reference"
enabled = true
kind = "wtrl-json"

# [[roots]]
# path = "/tmp/other-waterloo-root"
# label = "Other root"
# enabled = false
# kind = "directory"
"""

# Load a TOML file and return it as a mapping. This is used
# for both the main config and the logging config.
def load_toml(path: Path) -> dict[str, object]:
	with path.open("rb") as fh:
		return cast(dict[str, object], tomllib.load(fh))
	
# Load a logging config file for uvicorn. Currently only TOML is supported.
def load_logging_config(path: Path) -> dict[str, object]:
	if path.suffix.lower() == ".toml":
		return load_toml(path)
	raise ValueError(f"Unsupported logging config format: {path}")


def _configure_waterloo_logging(config: McpConfig) -> None:
	"""Install the configured Waterloo logging dictionary before startup messages."""
	if config.logging.config_path is None:
		return
	logging.config.dictConfig(load_logging_config(config.logging.config_path))


def _runtime_allowed_hosts(
	config_hosts: list[str],
	override_hosts: list[str] | None,
	server_port: int,
	public_port: int | None,
	config_port: int,
) -> list[str]:
	"""Compute the effective host allowlist from config and runtime overrides."""
	if override_hosts is None and public_port is None and server_port == config_port:
		return list(config_hosts)
	if not 1 <= server_port <= 65535:
		raise ValueError("--port must be an integer between 1 and 65535.")
	port = server_port if public_port is None else public_port
	if not 1 <= port <= 65535:
		raise ValueError("--public-port must be an integer between 1 and 65535.")
	if public_port is None:
		hosts = override_hosts if override_hosts is not None else config_hosts
		effective: list[str] = []
		for host in hosts:
			host_text = host.strip()
			if not host_text:
				continue
			if ":" in host_text:
				host_text = host_text.rsplit(":", 1)[0]
			effective.append(f"{host_text}:{port}")
		return effective
	hosts = override_hosts or ["localhost", "127.0.0.1"]
	effective = []
	for host in hosts:
		host_text = host.strip()
		if not host_text:
			continue
		if ":" in host_text:
			raise ValueError("--allowed-hosts entries must not include a port.")
		effective.append(f"{host_text}:{port}")
	return effective


def _with_runtime_security_overrides(
	config: McpConfig,
	server_port: int | None,
	allowed_hosts: list[str] | None,
	public_port: int | None,
) -> McpConfig:
	"""Return a config with runtime security overrides applied."""
	effective_server_port = config.server.port if server_port is None else server_port
	effective_allowed_hosts = _runtime_allowed_hosts(
		config.security.allowed_hosts,
		allowed_hosts,
		effective_server_port,
		public_port,
		config.server.port,
	)
	if (
		effective_allowed_hosts == config.security.allowed_hosts
		and effective_server_port == config.server.port
		and allowed_hosts is None
		and server_port is None
		and public_port is None
	):
		return config
	return McpConfig(
		server=ServerConfig(
			identity=config.server.identity,
			transport=config.server.transport,
			host=config.server.host,
			port=effective_server_port,
			streamable_http_path=config.server.streamable_http_path,
		),
		security=SecurityConfig(
			allowed_hosts=effective_allowed_hosts,
			allowed_origins=config.security.allowed_origins,
		),
		auth=config.auth,
		logging=config.logging,
		roots=config.roots,
		source_path=config.source_path,
	)


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


def build_reference_index(roots: list[RootConfig]) -> ReferenceIndex:
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
			|Must| build the reverse-reference index for all enabled roots.
			|Must| record which qids are available in which roots.
			|Must| record the root modification timestamps used by the MCP server.
			|Must| sort the reverse-reference lists into a stable order.
	Parameters:
		roots:
			The configured Waterloo roots to inspect.
	Returns:
		A populated |type|`ReferenceIndex` for the current server run.
	Raises:
		Exception:
			|May| raise if a root cannot be read or parsed.
	"""
	reverse_map: dict[tuple[str, str], list[ReferenceRecord]] = {}
	qids_to_roots: dict[str, set[str]] = {}
	root_mtimes: dict[str, RootMTimeRecord] = {}
	objects_by_root: dict[str, list[tuple[str, Mapping[str, WtrlJsonNode_t]]]] = {}

	for root in roots:
		if not root.enabled:
			continue
		root_path = _canonical_root_path(root.path)
		root_id = _root_id_for_path(str(root_path))
		root_mtimes[root_id] = _root_mtime_record(root_id, root_path)
		try:
			document = _read_json_document(str(root_path))
		except Exception as exc:
			logger.error(
				"Failed to load Waterloo root '%s' from %s: %s",
				root.label,
				root_path,
				exc,
			)
			continue
		if not isinstance(document, Mapping):
			continue
		objects = document.get("__WTRL_OBJECTS__", {})
		if not isinstance(objects, Mapping):
			continue
		root_objects: list[tuple[str, Mapping[str, WtrlJsonNode_t]]] = []
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
			source_profile_t = cast(Literal["module", "class", "function", "method"], source_profile)
			refs = _doc_see_also_refs(object_record)
			if not refs:
				continue
			is_normative = "See_also" in _doc_normative_sections(object_record)
			source_record = ReferenceRecord(
				source_root_id=root_id,
				source_qid=qid_text,
				source_profile=source_profile_t,
				is_normative=is_normative,
			)
			for ref in refs:
				for target_root_id, target_qid in _resolve_reference_targets(ref, root_id, qid_text, qids_to_roots):
					reverse_map.setdefault((target_root_id, target_qid), []).append(source_record)

	for records in reverse_map.values():
		records.sort(key=lambda record: (record.source_root_id, record.source_qid, record.source_profile))
	return ReferenceIndex(reverse_map=reverse_map, qids_to_roots=qids_to_roots, root_mtimes=root_mtimes)


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

def parse_roots(raw_roots: object, config_dir: Path) -> list[RootConfig]:
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
			|Must| parse the raw |attr|`[[roots]]` entries from the TOML configuration.
			|Must| validate that at least one root entry is present and properly structured.
			|Must| expand user home directory references (|file|`~`) in all paths.
			|Must| resolve relative paths against |var|`config_dir`.
			|Must| use absolute paths as-is after home expansion.
			|Must| canonicalize all final paths via |func|`resolve()` to follow symlinks and normalize separators.
			|Must| apply label fallback: use path basename if no label, or full path if basename is empty.
			|Must| apply field defaults: |attr|`enabled` defaults to |value|`True`, |attr|`kind` defaults to |value|`"directory"`.
			|Must| return a list of normalized |type|`RootConfig` records with absolute paths.
	Parameters:
		raw_roots:
			The raw configuration data from the |attr|`[[roots]]` section of the TOML file.
			|Must| be a list of TOML tables, where each table represents one Waterloo root.
		config_dir:
			The absolute parent directory of the configuration file itself.
			Used as the base directory for resolving relative paths in root entries.
	Returns:
		A list of |type|`RootConfig` records, one per validated root entry.
		All |attr|`path` fields are resolved to absolute filesystem paths.
	Raises:
		ValueError:
			|May| be raised if |var|`raw_roots` is not a non-empty list,
			if any entry is not a TOML table,
			if any entry lacks a |attr|`path` field,
			or if field values cannot be coerced to expected types.
	"""
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
			|Must| load and validate a Waterloo MCP TOML configuration file.
			|Must| resolve relative configuration paths against supported lookup locations.
			|Must| return a normalized |type|`McpConfig` object for server startup.
	Parameters:
		config_path:
			Optional path to the TOML configuration file.
			If omitted, the default package-local configuration path is used.
	Returns:
		A parsed and validated |type|`McpConfig` instance.
	Raises:
		FileNotFoundError:
			|May| be raised if the configuration file cannot be found.
		ValueError:
			|May| be raised if required TOML sections are missing or invalid,
			or if configured transport values are unsupported.
	"""
	path = _resolve_config_path(config_path)
	if not path.exists():
		if config_path is not None and not config_path.is_absolute():
			raise FileNotFoundError(
				"Waterloo MCP configuration file not found:\n"
				f"* {config_path}\nSearched:\n* {Path.cwd() / config_path}\n* {_package_root() / config_path}"
			)
		raise FileNotFoundError(f"Waterloo MCP configuration file not found: {path}")
	config_map = load_toml(path)
	if not isinstance(config_map, Mapping):
		raise ValueError("Waterloo MCP configuration file must contain a TOML table.")
	server_data = config_map.get("server", {})
	security_data = config_map.get("security", {})
	auth_data = config_map.get("auth", {})
	logging_data = config_map.get("logging", {})
	roots_data = config_map.get("roots", [])
	if not isinstance(server_data, Mapping):
		raise ValueError("[server] must be a TOML table.")
	if not isinstance(security_data, Mapping):
		raise ValueError("[security] must be a TOML table.")
	if not isinstance(auth_data, Mapping):
		raise ValueError("[auth] must be a TOML table.")
	if not isinstance(logging_data, Mapping):
		raise ValueError("[logging] must be a TOML table.")
	config_dir = path.parent.resolve()
	server_identity_raw = server_data.get("identity")
	server_identity_text = "" if server_identity_raw is None else str(server_identity_raw).strip()
	if server_identity_text and not _SERVER_IDENTITY_RE.fullmatch(server_identity_text):
		raise ValueError("[server].identity must match [-_a-zA-Z][-_a-zA-Z0-9+]*.")
	if bool(auth_data.get("enabled", False)) and not server_identity_text:
		raise ValueError("[server].identity is required when [auth].enabled is true.")
	server = ServerConfig(
		identity=server_identity_text or None,
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
	token_store_text = str(auth_data.get("token_store") or _default_auth_token_store_path())
	token_store_path = Path(token_store_text).expanduser()
	if not token_store_path.is_absolute():
		token_store_path = (config_dir / token_store_path).resolve()
	auth = AuthConfig(
		enabled=bool(auth_data.get("enabled", False)),
		token_store_path=token_store_path,
		realm=str(auth_data.get("realm", "Waterloo MCP")).strip() or "Waterloo MCP",
	)
	if auth.enabled:
		_validate_auth_token_store_path(auth.token_store_path)
		_validate_auth_token_store_contents(auth.token_store_path)
	# If a logging config path is provided, we will attempt to load it during server startup
	# and pass it to uvicorn. If the path is invalid or the file cannot be loaded,
	# the server will fail to start with an error message.
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
	roots = parse_roots(roots_data, config_dir)
	return McpConfig(server=server, security=security, auth=auth, logging=logging_cfg, roots=roots, source_path=path)


def _make_prompt_renderer(raw_messages: list[object], prompt_source: str) -> Callable[..., list[Message]]:
	"""Build a runtime renderer for one bundled MCP prompt template."""

	def _render_prompt(**kwargs: object) -> list[Message]:
		substitutions = {key: str(value) for key, value in kwargs.items()}
		messages: list[Message] = []
		for raw_message in raw_messages:
			if not isinstance(raw_message, dict):
				raise ValueError(f"Invalid MCP prompt message in {prompt_source}")
			role = raw_message.get("role")
			if role not in ("user", "assistant"):
				raise ValueError(f"Invalid MCP prompt message role in {prompt_source}")
			content = raw_message.get("content")
			if not isinstance(content, str):
				raise ValueError(f"Invalid MCP prompt message content in {prompt_source}")
			messages.append(
				Message(
					role=cast(Literal["user", "assistant"], role),
					content=TextContent(type="text", text=Template(content).safe_substitute(substitutions)),
				)
			)
		return messages

	return _render_prompt


def load_prompts() -> list[Prompt]:
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
			|Must| load the bundled MCP prompt definitions from the package resources.
			|Must| return one FastMCP prompt object per bundled JSON file.
			|Must| preserve the JSON name, title, description, arguments, and message order.
			|May| raise if a bundled prompt file is malformed or incomplete.
	Parameters:
	Returns:
		The bundled prompt templates as FastMCP prompt objects.
	Raises:
		ValueError:
			|May| raise if a bundled prompt definition is malformed.
	Notes:
		Bundled prompts:
			- `docstring_sphinx_guidelines`: Best practices for writing Sphinx-compatible Waterloo docstrings.
			- `draft_docstring`: Draft or refine a Waterloo docstring from a callable signature or an existing object.
			- `inspect_object`: Inspect one Waterloo object together with its signature, examples, and reverse references.
			- `inspect_root`: Get a compact structural overview of one Waterloo root before drilling into objects or searches.
		Storage:
			The prompt definitions are served from `sdv.doc.waterloo.mcp.prompts` at runtime rather than being hardcoded.
	"""
	prompts_dir = importlib.resources.files(__package__).joinpath("prompts")
	prompts: list[Prompt] = []
	for prompt_path in sorted((entry for entry in prompts_dir.iterdir() if entry.name.endswith(".json")), key=lambda entry: entry.name):
		prompt_data = json.loads(prompt_path.read_text(encoding="utf-8"))
		if not isinstance(prompt_data, dict):
			raise ValueError(f"Invalid MCP prompt definition: {prompt_path}")
		name = prompt_data.get("name")
		if not isinstance(name, str) or not name:
			raise ValueError(f"Invalid MCP prompt name in {prompt_path}")
		title = prompt_data.get("title")
		if title is not None and not isinstance(title, str):
			raise ValueError(f"Invalid MCP prompt title in {prompt_path}")
		description = prompt_data.get("description")
		if description is not None and not isinstance(description, str):
			raise ValueError(f"Invalid MCP prompt description in {prompt_path}")
		raw_arguments = prompt_data.get("arguments", [])
		if not isinstance(raw_arguments, list):
			raise ValueError(f"Invalid MCP prompt arguments in {prompt_path}")
		arguments: list[PromptArgument] = []
		for raw_argument in raw_arguments:
			if not isinstance(raw_argument, dict):
				raise ValueError(f"Invalid MCP prompt argument in {prompt_path}")
			argument_name = raw_argument.get("name")
			if not isinstance(argument_name, str) or not argument_name:
				raise ValueError(f"Invalid MCP prompt argument name in {prompt_path}")
			argument_description = raw_argument.get("description")
			if argument_description is not None and not isinstance(argument_description, str):
				raise ValueError(f"Invalid MCP prompt argument description in {prompt_path}")
			required = raw_argument.get("required", False)
			if not isinstance(required, bool):
				raise ValueError(f"Invalid MCP prompt argument required flag in {prompt_path}")
			arguments.append(
				PromptArgument(
					name=argument_name,
					description=argument_description,
					required=required,
				)
			)
		raw_messages = prompt_data.get("messages", [])
		if not isinstance(raw_messages, list):
			raise ValueError(f"Invalid MCP prompt messages in {prompt_path}")
		prompts.append(
			Prompt(
				name=name,
				title=title,
				description=description,
				arguments=arguments,
				fn=_make_prompt_renderer(raw_messages, str(prompt_path)),
				context_kwarg=None,
			)
		)
	return prompts


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
	Notes:
		Prompt_registration:
			The app currently registers the bundled prompts from `sdv.doc.waterloo.mcp.prompts`:
			- `docstring_sphinx_guidelines`
			- `draft_docstring`
			- `inspect_object`
			- `inspect_root`
		Reference_index:
			The app also builds a `ReferenceIndex` once per run and stores it on the MCP app for fast reverse-reference lookups.
			The reference index is the core per-run cache for reverse references, qid-to-root membership, and root mtimes.
	"""
	"""Build the Waterloo MCP app with the configured data roots."""
	reference_index = build_reference_index(config.roots)
	token_verifier = FileTokenVerifier(config.auth.token_store_path) if config.auth.enabled else None
	auth_settings = (
		AuthSettings(
			issuer_url=_auth_issuer_url(config),
			resource_server_url=None,
		)
		if config.auth.enabled
		else None
	)

	mcp = FastMCP(
		name="wtrl_mcp",
		instructions=read_package_readme(),
		token_verifier=token_verifier,
		debug=False,
		log_level=cast(LogLevel_t, config.logging.level),
		host=config.server.host,
		port=config.server.port,
		streamable_http_path=config.server.streamable_http_path,
		auth=auth_settings,
	)
	setattr(mcp, "_waterloo_reference_index", reference_index)
	if config.security.allowed_hosts or config.security.allowed_origins:
		mcp.settings.transport_security = TransportSecuritySettings(
			enable_dns_rebinding_protection=True,
			allowed_hosts=list(config.security.allowed_hosts),
			allowed_origins=list(config.security.allowed_origins),
		)

	def _root_mappings() -> list[Mapping[str, WtrlJsonNode_t]]:
		return [
			{
				"path": root.path,
				"label": root.label,
				"enabled": root.enabled,
				"kind": root.kind,
			}
			for root in config.roots
		]

	def _format_tool_signature(tool: Callable[..., object]) -> str:
		signature = str(inspect.signature(tool))
		signature = re.sub(r": '([^']+)'", r": \1", signature)
		signature = re.sub(r"-> '([^']+)'", r"-> \1", signature)
		return signature

	def _tool_help_text(toolname: str, tool: Callable[..., object], doc_source: Callable[..., object]) -> str:
		doc = inspect.getdoc(doc_source) or ""
		doc = textwrap.dedent(doc).strip()
		doc = doc.replace("\t", "    ")
		if not doc:
			doc = "No Waterloo docstring available."
		lines = [
			f"Tool: {toolname}",
			"",
			"Signature:",
			f"  {_format_tool_signature(tool)}",
			"",
			"Waterloo docstring:",
		]
		lines.extend(f"  {line}" if line else "" for line in doc.splitlines())
		return "\n".join(lines).strip()

	def _register_prompts(mcp: FastMCP) -> list[Prompt]:
		prompts = load_prompts()
		for prompt in prompts:
			mcp.add_prompt(prompt)
		return prompts

	# These are hints for the MCP client. They show up as badges
	# in the MCP inspector: click "List Tools" -> click <tool>.
	readonly_tool_annotations = ToolAnnotations(
		readOnlyHint=True,
		destructiveHint=False,
		idempotentHint=True,
	)

	@mcp.resource(
		"wtrl-mcp://instructions",
		name="instructions",
		description="The Waterloo MCP server instructions text (the package README), served live so clients can re-read it without reconnecting.",
		mime_type="text/plain",
	)
	def _instructions() -> str:
		return read_package_readme()

	@mcp.tool(name="list_roots", description="List configured Waterloo data roots.", annotations=readonly_tool_annotations)
	def _list_roots() -> list[dict[str, WtrlJsonNode_t]]:
		return list_roots(_root_mappings())

	@mcp.tool(name="get_root", description="Read one configured Waterloo data root by root_id.", annotations=readonly_tool_annotations)
	def _get_root(root_id: str) -> dict[str, WtrlJsonNode_t]:
		return get_root(root_id, _root_mappings())

	@mcp.tool(name="get_root_metadata", description="Read compact header metadata for one configured Waterloo data root.", annotations=readonly_tool_annotations)
	def _get_root_metadata(root_id: str) -> dict[str, WtrlJsonNode_t]:
		return get_root_metadata(root_id, _root_mappings())

	@mcp.tool(name="get_object", description="Read one Waterloo object by qid from a configured root.", annotations=readonly_tool_annotations)
	def _get_object(root_id: str, qid: str) -> dict[str, WtrlJsonNode_t]:
		return get_object(root_id, qid, _root_mappings())

	@mcp.tool(name="get_section", description="Read one stored section of one Waterloo object.", annotations=readonly_tool_annotations)
	def _get_section(root_id: str, qid: str, section: str) -> dict[str, WtrlJsonNode_t]:
		return get_section(root_id, qid, section, _root_mappings())

	@mcp.tool(name="get_subsection", description="Read one stored subsection of one Waterloo object.", annotations=readonly_tool_annotations)
	def _get_subsection(root_id: str, qid: str, section: str, subsection: str) -> dict[str, WtrlJsonNode_t]:
		return get_subsection(root_id, qid, section, subsection, _root_mappings())

	@mcp.tool(name="list_objects", description="List all Waterloo objects in one configured root.", annotations=readonly_tool_annotations)
	def _list_objects(root_id: str) -> list[ObjectSummary]:
		return list_objects(root_id, _root_mappings())

	@mcp.tool(name="get_examples", description="Read structured example metadata for one Waterloo object.", annotations=readonly_tool_annotations)
	def _get_examples(root_id: str, qid: str) -> list[ExampleRef]:
		return get_examples(root_id, qid, _root_mappings())

	@mcp.tool(name="get_example_source", description="Read the source text for one Waterloo example reference.", annotations=readonly_tool_annotations)
	def _get_example_source(root_id: str, example_path: str) -> str:
		return get_example_source(root_id, example_path, _root_mappings())

	@mcp.tool(name="get_signature", description="Read the stored signature block for one Waterloo object.", annotations=readonly_tool_annotations)
	def _get_signature(root_id: str, qid: str) -> dict[str, WtrlJsonNode_t]:
		return get_signature(root_id, qid, _root_mappings())

	@mcp.tool(name="get_references", description="Read structured incoming See_also references for one Waterloo object.", annotations=readonly_tool_annotations)
	def _get_references(root_id: str, qid: str, normative_only: bool = False) -> list[ReferenceRecord]:
		return get_references(reference_index.reverse_map, root_id, qid, normative_only)

	@mcp.tool(name="search_related", description="Read the star-shaped See_also neighborhood for one Waterloo object.", annotations=readonly_tool_annotations)
	def _search_related(root_id: str, qid: str, normative_only: bool = False) -> list[RelatedRecord]:
		return search_related(reference_index.reverse_map, reference_index.qids_to_roots, root_id, qid, _root_mappings(), normative_only)

	@mcp.tool(name="search_objects", description="Search Waterloo objects by expression and structural filters.", annotations=readonly_tool_annotations)
	def _search_objects(expression: str, filter: SearchObjectsFilter | None = None) -> list[tuple[str, str, str]]:
		return search_objects(expression, _root_mappings(), filter)

	@mcp.tool(name="search_sections", description="Search Waterloo section and subsection labels by expression and structural filters.", annotations=readonly_tool_annotations)
	def _search_sections(expression: str, filter: SearchSectionsFilter | None = None) -> list[dict[str, WtrlJsonNode_t]]:
		return search_sections(expression, _root_mappings(), filter)

	@mcp.tool(name="search_text", description="Search Waterloo text content by terms and structural filters.", annotations=readonly_tool_annotations)
	def _search_text(terms: list[str], filter: SearchTextFilter | None = None) -> list[dict[str, WtrlJsonNode_t]]:
		return search_text(terms, _root_mappings(), filter)

	@mcp.tool(name="gen_docstring", description="Generate a Waterloo docstring template for a given profile.", annotations=readonly_tool_annotations)
	def _gen_docstring(
		profile: DocstringProfile_t,
		signature: str | None = None,
		mode: DocstringMode_t = "minimal",
		indent_mode: DocstringIndentMode_t = "tab",
		json_mode: DocstringJsonMode_t = "full",
	) -> dict[str, WtrlJsonNode_t]:
		return gen_docstring(profile=profile, signature=signature, mode=mode, indent_mode=indent_mode, json_mode=json_mode)

	@mcp.tool(name="about", description="Read one Waterloo help topic from the bundled about files.", annotations=readonly_tool_annotations)
	def _about(topic: str | None = None) -> dict[str, WtrlJsonNode_t]:
		return about(topic)

	@mcp.tool(name="describe_tool", description="Describe one MCP tool by its canonical tool name.", annotations=readonly_tool_annotations)
	def _describe_tool(toolname: str) -> str:
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
				|Must| return the stored Waterloo tool signature together with the Waterloo-normative docstring for one MCP tool.
				|Must| help an agent discover the tool set without needing an out-of-band explanation channel.
		Parameters:
			toolname:
				The canonical MCP tool name to describe.
		Returns:
			A plain text help string containing the signature and the Waterloo docstring for the requested tool.
			Any short example text is part of the stored Waterloo docstring itself, not an extra synthetic layer.
		Raises:
			ValueError:
				|May| raise if the requested tool name is unknown.
		"""
		tool_wrappers: dict[str, Callable[..., object]] = {
            "about": _about,
            "describe_tool": _describe_tool,
            "gen_docstring": _gen_docstring,
			"get_examples": _get_examples,
			"get_example_source": _get_example_source,
			"get_object": _get_object,
			"get_references": _get_references,
			"get_root": _get_root,
			"get_root_metadata": _get_root_metadata,
			"get_section": _get_section,
			"get_subsection": _get_subsection,
			"get_signature": _get_signature,
			"list_objects": _list_objects,
			"list_roots": _list_roots,
			"search_objects": _search_objects,
			"search_related": _search_related,
			"search_sections": _search_sections,
			"search_text": _search_text,
        }
		if toolname not in tool_wrappers or toolname not in WTRL_TOOL_DOCS:
			raise ValueError(f"MCPS-007 unknown tool: {toolname}")
		tool_doc = WTRL_TOOL_DOCS[toolname]
		if tool_doc is None:
			raise ValueError(f"MCPS-007 unknown tool: {toolname}")
		return _tool_help_text(toolname, tool_wrappers[toolname], tool_doc)

	WTRL_TOOL_DOCS["describe_tool"] = _describe_tool

	prompts = _register_prompts(mcp)

	logger.info("wtrl_mcp %s ready.", __version__)
	if config.server.identity is not None:
		logger.info("Server identity: %s", config.server.identity)
	if config.auth.enabled:
		logger.info("Authentication is enabled for MCP clients. Token store: %s", config.auth.token_store_path)
		try:
			valid_tokens, revoked_tokens = _auth_token_stats(config.auth.token_store_path)
		except Exception as exc:
			logger.info("* Token store status: unavailable (%s)", exc)
		else:
			logger.info("* Valid tokens: %d", valid_tokens)
			logger.info("* Revoked tokens: %d", revoked_tokens)
	else:
		logger.info("Authentication is disabled.")

	# Hosts allowed for administration, e.g. generate bearer-tokens.
	# We leave this in regardless of authentication config.
	logger.info(f"Allowed hosts for administration:")
	logger.info(f"* {', '.join(_local_request_hosts())}")

	# Log security stuff: allowed_hosts
	logger.info(f"Allowed hosts is the list of urls under which the MCP server is allowed to be accessed.")
	logger.info(f"This is important for preventing DNS rebinding attacks if the server is exposed to untrusted networks.")
	for host in config.security.allowed_hosts:
		logger.info(f"* Allowed host: {host}")
	# Log security stuff: allowed_origins
	logger.info(f"Allowed origins is the list of urls allowed to access the MCP server via CORS.")
	for origin in config.security.allowed_origins:
		logger.info(f"* Allowed origin: {origin}")
	# Log the prompt names.
	logger.info("Serving %d prompts.", len(prompts))
	for prompt in prompts:
		if prompt.title and prompt.title != prompt.name:
			logger.info(f"* Registered prompt: {prompt.name} ({prompt.title})")
		else:
			logger.info(f"* Registered prompt: {prompt.name}")
	# Log the tool names.
	logger.info("Serving %d tools.", len(WTRL_TOOL_DOCS))
	for toolname in sorted(WTRL_TOOL_DOCS.keys()):
		logger.info(f"* Registered tool: {toolname}")
	# Log the configured roots and the size of the reference index for visibility on startup.
	logger.info(f"Loaded {len(config.roots)} configured roots.")
	for root in config.roots:
		logger.info(f"* Configured root: {root.path} '{root.label}' (enabled={root.enabled}, kind={root.kind})")
	logger.info(
		"Built reference index with %d target entries and %d source references.",
		len(reference_index.reverse_map),
		sum(len(records) for records in reference_index.reverse_map.values()),
	)
	return mcp


def _json_error(message: str, status_code: int) -> JSONResponse:
	return JSONResponse({"error": message}, status_code=status_code)


@lru_cache(maxsize=1)
def _local_request_hosts() -> frozenset[str]:
	hosts = {"127.0.0.1", "::1", "::ffff:127.0.0.1", "localhost"}
	route_path = Path("/proc/net/route")
	try:
		text = route_path.read_text(encoding="utf-8")
	except OSError:
		return frozenset(hosts)
	hosts.update(_local_request_hosts_from_route_text(text))
	return frozenset(hosts)


def _local_request_hosts_from_route_text(text: str) -> set[str]:
	hosts: set[str] = set()
	for line in text.splitlines()[1:]:
		parts = line.split()
		if len(parts) < 3 or parts[1] != "00000000":
			continue
		gateway_hex = parts[2].strip()
		if len(gateway_hex) != 8 or gateway_hex == "00000000":
			continue
		try:
			gateway = ".".join(str(int(gateway_hex[idx : idx + 2], 16)) for idx in (6, 4, 2, 0))
		except ValueError:
			continue
		hosts.add(gateway)
	return hosts


def _is_loopback_request(request: Request) -> bool:
	client = request.client
	if client is None:
		return False
	return client.host in _local_request_hosts()


def _install_admin_routes(app: Starlette, auth_config: AuthConfig, server_identity: str | None) -> None:
	async def _reject_if_not_loopback(request: Request) -> JSONResponse | None:
		if _is_loopback_request(request):
			return None
		return _json_error(ADMIN_LOOPBACK_ONLY_ERROR, 403)

	async def _admin_status(request: Request) -> JSONResponse:
		rejection = await _reject_if_not_loopback(request)
		if rejection is not None:
			logger.info(f"request.client is {str(request.client)}. Will be rejected.")
			return rejection
		payload: dict[str, object] = {"auth_enabled": auth_config.enabled, "identity": server_identity or ""}
		if auth_config.enabled:
			try:
				valid_tokens, revoked_tokens = _auth_token_stats(auth_config.token_store_path)
			except Exception as exc:
				return _json_error(f"Could not read auth token store: {exc}", 500)
			payload["valid_tokens"] = valid_tokens
			payload["revoked_tokens"] = revoked_tokens
		return JSONResponse(payload)

	async def _list_tokens(request: Request) -> JSONResponse:
		rejection = await _reject_if_not_loopback(request)
		if rejection is not None:
			return rejection
		return JSONResponse({"tokens": list_tokens(auth_config.token_store_path)})

	async def _create_token(request: Request) -> JSONResponse:
		rejection = await _reject_if_not_loopback(request)
		if rejection is not None:
			return rejection
		try:
			payload = await request.json()
		except json.JSONDecodeError:
			return _json_error("The admin request body must contain valid JSON.", 400)
		if not isinstance(payload, dict):
			return _json_error("The admin request body must be a JSON object.", 400)
		try:
			tid = payload.get("token_id")
			if not isinstance(tid, str):
				raise AuthTokenValidationError()
			record = create_token(
				auth_config.token_store_path,
				token_id=tid,
				expires_at=payload.get("expires_at"),
				notes=payload.get("notes"),
			)
		except AuthTokenValidationError as exc:
			return _json_error(str(exc), 400)
		except AuthTokenConflictError as exc:
			return _json_error(str(exc), 409)
		return JSONResponse(record, status_code=201)

	async def _revoke_token(request: Request) -> Response:
		rejection = await _reject_if_not_loopback(request)
		if rejection is not None:
			return rejection
		token_id = request.path_params.get("token_id")
		if not isinstance(token_id, str) or not token_id.strip():
			return _json_error("The token id path parameter is required.", 400)
		try:
			revoke_token(auth_config.token_store_path, token_id.strip())
		except AuthTokenNotFoundError as exc:
			return _json_error(str(exc), 404)
		except AuthTokenConflictError as exc:
			return _json_error(str(exc), 409)
		return Response(status_code=204)
	# Register the admin routes under the configured base path.
	app.router.routes.append(Route(f"{ADMIN_ENDPOINT_BASE}", endpoint=_admin_status, methods=["GET"]))
	if auth_config.enabled:
		app.router.routes.append(Route(f"{ADMIN_ENDPOINT_BASE}/tokens", endpoint=_list_tokens, methods=["GET"]))
		app.router.routes.append(Route(f"{ADMIN_ENDPOINT_BASE}/tokens", endpoint=_create_token, methods=["POST"]))
		app.router.routes.append(Route(f"{ADMIN_ENDPOINT_BASE}/tokens/{{token_id}}", endpoint=_revoke_token, methods=["DELETE"])
		)


def _wrap_browser_cors(app: ASGIApp, origins: list[str]) -> ASGIApp:
	"""Wrap an ASGI app with permissive browser CORS for MCP Inspector use."""
	return CORSMiddleware(
		app,
		allow_origins=origins,
		allow_methods=["GET", "POST", "DELETE"],
		allow_headers=["*"],
		expose_headers=["Mcp-Session-Id"],
	)


def _build_http_app(config: McpConfig, mcp: FastMCP) -> ASGIApp:
	http_app = mcp.streamable_http_app()
	_install_admin_routes(http_app, config.auth, config.server.identity)
	if config.security.allowed_origins:
		http_app = _wrap_browser_cors(http_app, list(config.security.allowed_origins))
	http_app = _RequestLogGroupMiddleware(http_app)
	return http_app


class _RequestLogGroupMiddleware:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			extension
	Contract:
		general:
			|Must| wrap an ASGI application and assign a request id to each HTTP request.
			|Must| set the request-local log-group key before handing control to the wrapped application.
			|Must| preserve the request id for the duration of the request task so that application logs and access logs can use the same prefix.
			|May| leave non-HTTP scopes untouched.
		constructor:
			|Must| take the ASGI application to wrap as a parameter.
			|Must_not| start the server or handle any requests itself.
	Notes:
		Purpose:
			This middleware keeps the log grouping logic local to the MCP server entry point.
			It lets the formatter show a visible request prefix without forcing the rest of the application to know about the logging transport details.
		Behavior:
			The request id is generated sequentially and is currently only intended for human-readable log grouping.
	"""

	def __init__(self, app: ASGIApp) -> None:
		self._app = app

	async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
		if scope.get("type") != "http":
			await self._app(scope, receive, send)
			return

		request_id = allocate_request_id()
		method = str(scope.get("method", "HTTP"))
		path = str(scope.get("path", ""))
		session_id = None
		headers = scope.get("headers")
		if isinstance(headers, list):
			for key, value in headers:
				if isinstance(key, bytes) and key.lower() == b"mcp-session-id" and isinstance(value, bytes):
					session_id = value.decode("utf-8", errors="replace")
					break
		group_key = f"{request_id} {method} {path}"
		if session_id:
			group_key = f"{group_key} session={session_id}"

		request_token = set_request_id(request_id)
		group_token = set_log_group_key(group_key)
		# Keep the request id alive for the rest of the request task so that
		# both the application logs and the later Uvicorn access log line can
		# see the same request prefix.
		try:
			await self._app(scope, receive, send)
		finally:
			reset_request_id(request_token)
			reset_log_group_key(group_token)


def _print_config_error(exc: Exception, config_path: Path | None = None) -> None:
	"""Print a user-facing configuration error with load context."""
	if config_path is not None:
		print(f"wtrl_mcp: Loading configuration file: {config_path}", file=sys.stderr)
	message = str(exc).strip()
	if not message:
		message = exc.__class__.__name__
	for line in message.splitlines():
		print(f"wtrl_mcp: {line}", file=sys.stderr)


def _run_loaded_config(config: McpConfig) -> None:
	"""Run the server according to a loaded configuration."""
	_configure_waterloo_logging(config)
	mcp = build_app(config)
	if config.server.transport == "streamable-http":
		http_app = _build_http_app(config, mcp)
		logger.info("Using configuration file: %s", config.source_path.resolve())
		# Streamable HTTP is exposed directly here so browser clients can
		# negotiate CORS. SSE is not part of this transport setup.
		uvicorn.run(
			http_app,
			host=config.server.host,
			port=config.server.port,
			log_level=config.logging.level.lower(),
			access_log=bool(config.logging.access_log) if config.logging.access_log is not None else True,
			log_config=load_logging_config(config.logging.config_path) if config.logging.config_path else None,
		)
		return

	# Stdio is the default development transport.
	logger.info("Using configuration file: %s", config.source_path.resolve())
	mcp.run(transport="stdio")


class McpAppRunner:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
			|Must| provide a public launcher for the MCP app that can be used before the configuration is loaded.
			|Must| allow the app to be built and run after the configuration is loaded.
		constructor:
			|Must| take an optional configuration path to use for loading the configuration.
	"""
	dependencies: list[str] = []

	def __init__(self, config_path: Path | None = None) -> None:
		self._config_path = config_path or _default_config_path()

	def run(self, transport: str | None = None) -> None:
		try:
			config = load_config(self._config_path)
		except (FileNotFoundError, ValueError) as exc:
			_print_config_error(exc, self._config_path)
			raise SystemExit(1) from exc
		if transport is not None:
			config = McpConfig(
				server=ServerConfig(
					identity=config.server.identity,
					transport=transport,
					host=config.server.host,
					port=config.server.port,
					streamable_http_path=config.server.streamable_http_path,
				),
				security=config.security,
				auth=config.auth,
				logging=config.logging,
				roots=config.roots,
				source_path=config.source_path,
			)
		_run_loaded_config(config)

runner = McpAppRunner()


def main(argv: list[str] | None = None) -> int:
	"""Start the Waterloo MCP server."""
	args = build_parser().parse_args(argv)
	if args.gen_config_template:
		print(_template_text())
		return 0
	try:
		config = load_config(args.config)
		config = _with_runtime_security_overrides(
			config,
			getattr(args, "port", None),
			getattr(args, "allowed_hosts", None),
			getattr(args, "public_port", None),
		)
	except (FileNotFoundError, ValueError) as exc:
		_print_config_error(exc, args.config)
		return 1
	_run_loaded_config(config)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
