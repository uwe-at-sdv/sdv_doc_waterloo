"""Command-line helper for managing Waterloo MCP admin servers and tokens."""

from typing import Final

import argparse
import io
import contextlib
import importlib.resources
import ipaddress
import json
import os
import re
import shutil
import socket
import sys
import time
import tempfile
import subprocess
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator
import sdv.doc.waterloo.docitem as docitem

from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.mcp.sdv_tty_util_table import Align, table as tty_table
from sdv.doc.waterloo.waterlint_common import DIAG_TARGET_STDERR, DIAG_TARGET_STDOUT, emit_diagnostics


DEFAULT_REGISTRY_PATH = Path.home() / ".wtrl_mcp_admin.json"
DEFAULT_MCP_ENDPOINT = "/mcp"
DEFAULT_ADMIN_ENDPOINT = "/admin"
DEFAULT_ORIGIN = "http://localhost:6274"
DEFAULT_PROTOCOL_VERSION = "2025-11-25"
DEFAULT_TIMEOUT = 5.0
TABLE_CELL_WRAP_WIDTH = 32
SSH_TUNNEL_TIMEOUT = 5.0
SERVER_IDENTITY_MAX_LENGTH = 63
SERVER_IDENTITY_RE = re.compile(r"^[-_a-zA-Z][-_a-zA-Z0-9+]*$")
TRACER_JSON_ID_PREFIX = "urn:wtrl_mcp_admin:wtrl-tracer-json"

HTTP_STATUS_MESSAGE: Final[dict[int, str]] = {
	200: "ok",
	201: "created",
	202: "accepted",
	204: "no content",
	400: "bad request",
	401: "unauthorized",
	403: "forbidden",
	404: "not found",
	500: "internal server error",
}

@dataclass(frozen=True)
class ServerEntry:
	identity: str
	label: str
	url: str
	mcp_endpoint: str = DEFAULT_MCP_ENDPOINT
	admin_endpoint: str = DEFAULT_ADMIN_ENDPOINT
	description: str = ""

	def host_port(self) -> str:
		parsed = urlparse(self.url)
		return parsed.netloc or self.url


@dataclass(frozen=True)
class TableColumn:
	key: str
	label: str


@dataclass(frozen=True)
class TableReport:
	kind: str
	columns: tuple[TableColumn, ...]
	rows: list[dict[str, str]]


@dataclass(frozen=True)
class AdminAccess:
	mode: str
	base_url: str


@dataclass
class AdminCliError(Exception):
	rule_id: str
	message: str
	exit_code: int = 1

	def __str__(self) -> str:
		return self.message


def _print_err(message: str) -> None:
	print(f"wtrl_mcp_admin: {message}", file=sys.stderr)


def _normalize_label(text: str) -> str:
	label = text.strip()
	if not label:
		raise ValueError("label must not be empty")
	return label


def _normalize_identity(text: str | None) -> str:
	identity = "" if text is None else str(text).strip()
	if not identity:
		return ""
	if len(identity) > SERVER_IDENTITY_MAX_LENGTH:
		raise ValueError(f"identity must not exceed {SERVER_IDENTITY_MAX_LENGTH} characters")
	if not SERVER_IDENTITY_RE.fullmatch(identity):
		raise ValueError("identity must match [-_a-zA-Z][-_a-zA-Z0-9+]*")
	return identity


def _normalize_path(path: str, default: str) -> str:
	value = str(path or default).strip()
	if not value:
		value = default
	if not value.startswith("/"):
		value = "/" + value
	value = value.rstrip("/") or "/"
	return value


def _base_url_from_args(url: str | None, host: str | None, port: int | None) -> str:
	if url:
		parsed = urlparse(url)
		if parsed.scheme not in {"http", "https"} or not parsed.netloc:
			raise ValueError("url must be an absolute http(s) URL")
		return f"{parsed.scheme}://{parsed.netloc}"
	if host and port:
		return f"http://{host.strip()}:{port}"
	raise ValueError("either --url or --host/--port must be provided")


def _server_url(base_url: str, endpoint: str) -> str:
	return base_url.rstrip("/") + _normalize_path(endpoint, "/").rstrip("/")


def _registry_path(value: str | None) -> Path:
	if value:
		return Path(value).expanduser()
	env_value = os.environ.get("WTRL_MCP_ADMIN_REGISTRY", "").strip()
	if env_value:
		return Path(env_value).expanduser()
	return DEFAULT_REGISTRY_PATH


def _registry_load_context(path: Path) -> str:
	return f"Validating admin registry file: {path}."


def _load_registry(path: Path) -> dict[str, Any]:
	if not path.exists():
		return {"servers": []}
	text = path.read_text(encoding="utf-8").strip()
	if not text:
		return {"servers": []}
	try:
		data = json.loads(text)
	except json.JSONDecodeError as exc:
		raise AdminCliError("MCPA-002", f"{_registry_load_context(path)} Registry file is not valid JSON: {exc.msg}") from exc
	if not isinstance(data, dict):
		raise AdminCliError("MCPA-002", f"{_registry_load_context(path)} Registry root must be a JSON object")
	servers = data.get("servers", [])
	if not isinstance(servers, list):
		raise AdminCliError("MCPA-002", f"{_registry_load_context(path)} Registry must contain a servers list")
	for entry in servers:
		if not isinstance(entry, dict):
			raise AdminCliError("MCPA-002", f"{_registry_load_context(path)} Registry contains a non-object server entry")
	_validate_registry_schema(data, path)
	return data


def _validate_registry_schema(data: dict[str, Any], path: Path) -> None:
	schema_path = importlib.resources.files("sdv.doc.waterloo") / "schema" / "wtrl-mcp-admin-registry-json-0.2.0.schema.json"
	try:
		schema = json.loads(schema_path.read_text(encoding="utf-8"))
	except OSError as exc:
		raise AdminCliError("MCPA-002", f"could not read admin registry schema: {schema_path}") from exc
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(data), key=lambda exc: list(exc.path))
	if errors:
		first = errors[0]
		location = "/".join(str(part) for part in first.path) or "<root>"
		raise AdminCliError(
			"MCPA-002",
			f"Validating admin registry file: {path}. "
			f"Registry file is invalid at {location}: {first.message}"
		)


def _save_registry(path: Path, data: dict[str, Any]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent), prefix=f"{path.name}.", suffix=".tmp") as handle:
		json.dump(data, handle, indent=2, sort_keys=True)
		handle.write("\n")
		tmp_path = Path(handle.name)
	tmp_path.replace(path)


def _server_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
	servers = data.get("servers", [])
	if not isinstance(servers, list):
		raise AdminCliError("MCPA-002", "registry must contain a servers list")
	return [entry for entry in servers if isinstance(entry, dict)]


def _read_server_entry(data: dict[str, Any], label: str) -> ServerEntry:
	for entry in _server_entries(data):
		if str(entry.get("label", "")).strip() == label:
			identity = _normalize_identity(entry.get("identity"))
			url = str(entry.get("url") or "").strip()
			if not url:
				raise AdminCliError("MCPA-002", f"server '{label}' is missing its url")
			return ServerEntry(
				identity=identity,
				label=label,
				url=url,
				mcp_endpoint=_normalize_path(entry.get("mcp_endpoint", DEFAULT_MCP_ENDPOINT), DEFAULT_MCP_ENDPOINT),
				admin_endpoint=_normalize_path(entry.get("admin_endpoint", DEFAULT_ADMIN_ENDPOINT), DEFAULT_ADMIN_ENDPOINT),
				description=str(entry.get("description") or ""),
			)
	raise AdminCliError("MCPA-001", f"unknown server label: {label}")


def _store_server_entry(data: dict[str, Any], entry: ServerEntry) -> dict[str, Any]:
	servers = _server_entries(data)
	updated: list[dict[str, Any]] = [srv for srv in servers if str(srv.get("label", "")).strip() != entry.label]
	updated.append(
		{
			"identity": entry.identity,
			"label": entry.label,
			"url": entry.url,
			"mcp_endpoint": entry.mcp_endpoint,
			"admin_endpoint": entry.admin_endpoint,
			"description": entry.description,
		}
	)
	data["servers"] = updated
	return data


def _remove_server_entry(data: dict[str, Any], label: str) -> bool:
	servers = _server_entries(data)
	updated = [srv for srv in servers if str(srv.get("label", "")).strip() != label]
	if len(updated) == len(servers):
		return False
	data["servers"] = updated
	return True


def _server_hostname(entry: ServerEntry) -> str:
	parsed = urlparse(entry.url)
	return (parsed.hostname or "").strip()


def _server_port(entry: ServerEntry) -> int:
	parsed = urlparse(entry.url)
	if parsed.port is not None:
		return parsed.port
	if parsed.scheme == "https":
		return 443
	return 80


def _is_loopback_host(host: str) -> bool:
	if host == "localhost":
		return True
	try:
		return ipaddress.ip_address(host).is_loopback
	except ValueError:
		return False


def _free_local_port() -> int:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.bind(("127.0.0.1", 0))
		return int(sock.getsockname()[1])


def _wait_for_tcp_port(host: str, port: int, timeout: float) -> None:
	deadline = time.monotonic() + timeout
	last_error: OSError | None = None
	while time.monotonic() < deadline:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.settimeout(0.2)
			try:
				sock.connect((host, port))
			except OSError as exc:
				last_error = exc
			else:
				return
		time.sleep(0.05)
	if last_error is None:
		raise RuntimeError(f"timed out waiting for SSH tunnel on {host}:{port}")
	raise RuntimeError(f"timed out waiting for SSH tunnel on {host}:{port}: {last_error}")


def _admin_access_mode(entry: ServerEntry) -> str:
	host = _server_hostname(entry)
	if not host or _is_loopback_host(host):
		return "direct"
	return "ssh"


@contextmanager
def _admin_access(entry: ServerEntry) -> Any:
	mode = _admin_access_mode(entry)
	host = _server_hostname(entry)
	if mode == "direct":
		yield AdminAccess(mode="direct", base_url=entry.url)
		return
	if shutil.which("ssh") is None:
		raise AdminCliError("MCPA-003", "ssh is required for non-loopback admin access, but it was not found")
	local_port = _free_local_port()
	remote_port = _server_port(entry)
	ssh_target = host
	ssh_cmd = [
		"ssh",
		"-o",
		"BatchMode=yes",
		"-o",
		"ExitOnForwardFailure=yes",
		"-N",
		"-L",
		f"127.0.0.1:{local_port}:127.0.0.1:{remote_port}",
		ssh_target,
	]
	proc = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	try:
		_wait_for_tcp_port("127.0.0.1", local_port, SSH_TUNNEL_TIMEOUT)
		yield AdminAccess(mode="ssh", base_url=f"http://127.0.0.1:{local_port}")
	finally:
		if proc.poll() is None:
			proc.terminate()
			try:
				proc.wait(timeout=1.0)
			except subprocess.TimeoutExpired:
				proc.kill()
				proc.wait(timeout=1.0)
		else:
			proc.wait(timeout=1.0)


def _table_report_to_json(report: TableReport) -> dict[str, Any]:
	return {
		"kind": report.kind,
		"columns": [{"key": column.key, "label": column.label} for column in report.columns],
		"rows": report.rows,
	}


def _render_table_report(report: TableReport) -> str:
	rows = [[row.get(column.key, "") for column in report.columns] for row in report.rows]
	headers = [column.label for column in report.columns]
	tbl = tty_table()
	tbl.row(*headers)
	tbl.sep()
	for row in rows:
		tbl.row(*[_hard_wrap_text(cell) for cell in row])
	for index, column in enumerate(report.columns, start=1):
		if "status" in column.label.lower():
			tbl.col_align(index, Align.COL_ALIGN_LEFT)
	return str(tbl)


def _write_output(path_text: str | None, text: str, *, default_stream: Any | None = None) -> None:
	if default_stream is None:
		default_stream = sys.stdout
	if path_text is None:
		print(text, file=default_stream)
		return
	if path_text in {"-", "@STDOUT"}:
		print(text, file=default_stream)
		return
	Path(path_text).write_text(text, encoding="utf-8")


def _write_report(report: TableReport, *, out: str | None, out_json: str | None, default_stream: Any | None = None) -> None:
	if out is not None and out_json is not None:
		raise ValueError("use only one of --out or --out-json")
	if out_json is not None:
		payload = json.dumps(_table_report_to_json(report), indent=2, sort_keys=True, ensure_ascii=False)
		_write_output(out_json, payload + "\n", default_stream=default_stream)
		return
	_write_output(out, _render_table_report(report), default_stream=default_stream)


def _strip_ansi_for_stream(stream: Any) -> bool:
	isatty = getattr(stream, "isatty", None)
	if callable(isatty):
		try:
			return not bool(isatty())
		except Exception:
			return True
	return True


def _open_diag_target(path: str | None, default_stream: Any) -> Any:
	if path is None:
		return contextlib.nullcontext(default_stream)
	if path == DIAG_TARGET_STDOUT:
		return contextlib.nullcontext(sys.stdout)
	if path == DIAG_TARGET_STDERR:
		return contextlib.nullcontext(sys.stderr)
	return open(path, "w", encoding="utf-8")


def _build_admin_tracer_json_doc(tr: tracer) -> dict[str, Any]:
	return tr.build_json(
		tr.Severity.INFO,
		schema_version=docitem.WTRL_TRACER_JSON_SCHEMA_VERSION,
		waterloo_version=docitem.__version__,
		id_prefix=TRACER_JSON_ID_PREFIX,
		include_debug=False,
	)


def _emit_admin_diagnostics(tr: tracer, out_diag: str | None, out_diag_json: str | None) -> None:
	if out_diag is not None:
		with _open_diag_target(out_diag, sys.stderr) as fh:
			emit_diagnostics(tr, fh, debug=False, strip_ansi=_strip_ansi_for_stream(fh))
	if out_diag_json is not None:
		doc = _build_admin_tracer_json_doc(tr)
		with _open_diag_target(out_diag_json, sys.stdout) as fh:
			json.dump(doc, fh, indent=2, sort_keys=True, ensure_ascii=False)
			fh.write("\n")


def _command_info_message(command: str) -> str:
	return {
		"add-server": "adding a server registry entry",
		"del-server": "removing a server registry entry",
		"list-servers": "listing registered servers",
		"ping-servers": "pinging registered servers",
		"gen-token": "generating a bearer token",
		"revoke-token": "revoking a bearer token",
		"verify-token": "verifying a bearer token",
		"list-tokens": "listing bearer tokens",
	}.get(command, f"running subcommand '{command}'")


def _add_diag_args(parser: argparse.ArgumentParser) -> None:
	parser.add_argument(
		"--out-diag",
		help=f"Write tracer diagnostics to PATH, {DIAG_TARGET_STDOUT}, or {DIAG_TARGET_STDERR}. Use {DIAG_TARGET_STDERR} to keep command output on standard output.",
	)
	parser.add_argument(
		"--out-diag-json",
		help=f"Write tracer diagnostics in machine-readable JSON format to PATH, {DIAG_TARGET_STDOUT}, or {DIAG_TARGET_STDERR}. Use {DIAG_TARGET_STDERR} to keep command output on standard output.",
	)


def _split_diag_args(argv: list[str]) -> tuple[list[str], str | None, str | None]:
	diag_parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
	_add_diag_args(diag_parser)
	diag_args, remainder = diag_parser.parse_known_args(argv)
	return remainder, diag_args.out_diag, diag_args.out_diag_json


def _admin_request_headers(entry: ServerEntry) -> dict[str, str]:
	return {"Host": entry.host_port()}


def _hard_wrap_text(text: object, width: int = TABLE_CELL_WRAP_WIDTH) -> str:
	raw = str(text)
	if width <= 0:
		return raw
	lines: list[str] = []
	for line in raw.splitlines() or [""]:
		if not line:
			lines.append("")
			continue
		for start in range(0, len(line), width):
			lines.append(line[start : start + width])
	return "\n".join(lines)


def _request_json(
	method: str,
	url: str,
	payload: dict[str, Any] | None = None,
	extra_headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
	headers = {
		"Origin": DEFAULT_ORIGIN,
		"Accept": "application/json, text/event-stream",
	}
	if extra_headers:
		headers.update(extra_headers)
	data = None
	if payload is not None:
		headers["Content-Type"] = "application/json"
		data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
	req = Request(url, data=data, headers=headers, method=method)
	try:
		with urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
			raw = resp.read().decode("utf-8")
			status = resp.status
			content_type = resp.headers.get_content_type()
	except HTTPError as exc:
		raw = exc.read().decode("utf-8")
		status = exc.code
		content_type = exc.headers.get_content_type() if exc.headers is not None else ""
	except TimeoutError as exc:
		raise AdminCliError("MCPA-004", f"request to {url} timed out after {DEFAULT_TIMEOUT:.1f}s") from exc
	except URLError as exc:
		raise AdminCliError("MCPA-004", str(exc)) from exc
	obj = _parse_json_or_sse(raw, url=url, status=status, content_type=content_type)
	if not isinstance(obj, dict):
		raise AdminCliError("MCPA-004", f"expected a JSON object response from {url} (status {status}, content-type {content_type or 'unknown'})")
	return status, obj


def _body_preview(raw: str, width: int = 220) -> str:
	text = " ".join(raw.strip().split())
	if len(text) <= width:
		return text
	return text[: width - 1] + "…"


def _parse_json_or_sse(raw: str, *, url: str, status: int, content_type: str) -> Any:
	text = raw.strip()
	if not text:
		return {}
	if text.startswith("{"):
		return json.loads(text)
	data_lines: list[str] = []
	for line in text.splitlines():
		if line.startswith("data:"):
			data_lines.append(line.split(":", 1)[1].lstrip())
	if not data_lines:
		preview = _body_preview(text)
		raise AdminCliError(
			"MCPA-004",
			f"could not find JSON content in response from {url} "
			f"(status {status}, content-type {content_type or 'unknown'}, body starts with {preview!r})"
		)
	return json.loads("\n".join(data_lines))


# There are two categories of routes on the server side:
# 1. The MCP endpoint, which is used by clients to communicate with the server.
# 2. The admin endpoint, which is used by administrators to manage the server and its tokens.
# Both are subject to our ping and status checks.
def _ping_admin(entry: ServerEntry) -> tuple[str, str, str]:
	try:
		with _admin_access(entry) as access:
			status, data = _request_json(
				"GET",
				_server_url(access.base_url, entry.admin_endpoint),
				extra_headers=_admin_request_headers(entry),
			)
	except Exception as exc:
		return _admin_access_mode(entry), f"error: {exc}", ""
	if status == 200:
		return access.mode, _format_admin_status(data), str(data.get("identity") or "").strip()
	return access.mode, _format_status(status), ""


def _ping_client(entry: ServerEntry) -> str:
	payload = {
		"jsonrpc": "2.0",
		"id": 1,
		"method": "initialize",
		"params": {
			"protocolVersion": DEFAULT_PROTOCOL_VERSION,
			"capabilities": {},
			"clientInfo": {"name": "wtrl_mcp_admin", "version": "0.0.0"},
		},
	}
	try:
		status, _ = _request_json("POST", _server_url(entry.url, entry.mcp_endpoint), payload)
	except Exception as exc:
		return f"error: {exc}"
	return _format_status(status)


def _format_status(status: int) -> str:
	if status == 200:
		return "ok"
	if status == 401:
		return "auth-required (401)"
	if status == 403:
		return "forbidden (403)"
	return f"http {status}"


def _format_verify_status(status: int) -> str:
	if status == 200:
		return "ok"
	if status == 401:
		return "invalid token (401)"
	if status == 403:
		return "forbidden (403)"
	if status == 404:
		return "not found (404)"
	return _format_status(status)

def _format_admin_status(data: dict[str, Any]) -> str:
	if not bool(data.get("auth_enabled")):
		return "auth-disabled"
	return "auth-enabled"


def _format_admin_token_operation_error(entry: ServerEntry, operation: str, status: int, endpoint: str) -> str:
	if status == 404:
		return f"server '{entry.label}' does not expose token administration at '{endpoint}' (404)"
	if status == 401:
		return f"server '{entry.label}' rejected {operation} (invalid or missing admin credentials, 401)"
	if status == 403:
		return f"server '{entry.label}' rejected {operation} (forbidden, 403)"
	return f"server '{entry.label}' failed to {operation} via '{endpoint}' (HTTP {status})"


def _format_add_server_message(entry: ServerEntry) -> str:
	return f"registered server '{entry.label}' at {entry.host_port()}"


def _format_del_server_message(label: str) -> str:
	return f"removed server '{label}'"


def _cmd_add_server(args: argparse.Namespace, tr: tracer | None = None) -> int:
	registry_path = _registry_path(args.registry)
	data = _load_registry(registry_path)
	base_url = _base_url_from_args(args.url, args.host, args.port)
	entry = ServerEntry(
		identity="",
		label=_normalize_label(args.label),
		url=base_url,
		mcp_endpoint=_normalize_path(args.mcp_endpoint, DEFAULT_MCP_ENDPOINT),
		admin_endpoint=_normalize_path(args.admin_endpoint, DEFAULT_ADMIN_ENDPOINT),
		description=str(args.description or "").strip(),
	)
	_save_registry(registry_path, _store_server_entry(data, entry))
	if tr is not None:
		tr.add_info(_format_add_server_message(entry), "tool")
	return 0


def _cmd_del_server(args: argparse.Namespace, tr: tracer | None = None) -> int:
	registry_path = _registry_path(args.registry)
	data = _load_registry(registry_path)
	label = _normalize_label(args.label)
	if not _remove_server_entry(data, label):
		raise AdminCliError("MCPA-001", f"unknown server label: {label}")
	_save_registry(registry_path, data)
	if tr is not None:
		tr.add_info(_format_del_server_message(label), "tool")
	return 0


def _cmd_list_servers(args: argparse.Namespace, tr: tracer | None = None) -> int:
	registry_path = _registry_path(args.registry)
	data = _load_registry(registry_path)
	entries = [
		ServerEntry(
			identity=_normalize_identity(entry.get("identity")),
			label=str(entry.get("label", "")).strip(),
			url=str(entry.get("url") or "").strip(),
			mcp_endpoint=_normalize_path(entry.get("mcp_endpoint", DEFAULT_MCP_ENDPOINT), DEFAULT_MCP_ENDPOINT),
			admin_endpoint=_normalize_path(entry.get("admin_endpoint", DEFAULT_ADMIN_ENDPOINT), DEFAULT_ADMIN_ENDPOINT),
			description=str(entry.get("description") or ""),
		)
		for entry in _server_entries(data)
	]
	report = TableReport(
		kind="servers",
		columns=(
			TableColumn("label", "Label"),
			TableColumn("identity", "Identity"),
			TableColumn("host_port", "Host:Port"),
			TableColumn("mcp_endpoint", "MCP path"),
			TableColumn("admin_endpoint", "Admin path"),
			TableColumn("description", "Description"),
		),
		rows=[
			{
				"label": entry.label,
				"identity": entry.identity,
				"host_port": entry.host_port(),
				"mcp_endpoint": entry.mcp_endpoint,
				"admin_endpoint": entry.admin_endpoint,
				"description": entry.description,
			}
			for entry in entries
		],
	)
	if not report.rows:
		if args.out is not None or args.out_json is not None:
			_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
			return 0
		print("No servers registered.")
		return 0
	_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
	return 0


def _cmd_ping_servers(args: argparse.Namespace, tr: tracer | None = None) -> int:
	registry_path = _registry_path(args.registry)
	data = _load_registry(registry_path)
	entries = [
		ServerEntry(
			identity=_normalize_identity(entry.get("identity")),
			label=str(entry.get("label", "")).strip(),
			url=str(entry.get("url") or "").strip(),
			mcp_endpoint=_normalize_path(entry.get("mcp_endpoint", DEFAULT_MCP_ENDPOINT), DEFAULT_MCP_ENDPOINT),
			admin_endpoint=_normalize_path(entry.get("admin_endpoint", DEFAULT_ADMIN_ENDPOINT), DEFAULT_ADMIN_ENDPOINT),
			description=str(entry.get("description") or ""),
		)
		for entry in _server_entries(data)
	]
	rows: list[dict[str, str]] = []
	for entry in entries:
		admin_access, admin_status, discovered_identity = _ping_admin(entry)
		client_status = _ping_client(entry)
		identity = discovered_identity or entry.identity or entry.label
		rows.append(
			{
				"label": entry.label,
				"identity": identity,
				"host": entry.host_port(),
				"admin_access": admin_access,
				"admin_status": admin_status,
				"client_status": client_status,
			}
		)
	report = TableReport(
		kind="ping",
		columns=(
			TableColumn("label", "Label"),
			TableColumn("identity", "Identity"),
			TableColumn("host", "Host"),
			TableColumn("admin_access", "Admin access"),
			TableColumn("admin_status", "Admin status"),
			TableColumn("client_status", "Client status"),
		),
		rows=rows,
	)
	if not report.rows:
		if args.out is not None or args.out_json is not None:
			_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
			return 0
		print("No servers registered.")
		return 0
	_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
	return 0


def _build_token_id(args: argparse.Namespace) -> str:
	if args.token_id:
		return _normalize_label(args.token_id)
	user = args.user or "any"
	client = args.client or "any"
	location = args.location or "any"
	return _normalize_label(f"{user}-{client}-{location}")


def _cmd_gen_token(args: argparse.Namespace, tr: tracer | None = None) -> int:
	entry = _read_server_entry(_load_registry(_registry_path(args.registry)), _normalize_label(args.server))
	token_id = _build_token_id(args)
	token_endpoint = f"{entry.admin_endpoint}/tokens"
	payload = {
		"token_id": token_id,
		"expires_at": args.expires_at,
		"notes": args.notes,
	}
	with _admin_access(entry) as access:
		status, data = _request_json(
			"POST",
			_server_url(access.base_url, token_endpoint),
			payload,
			_admin_request_headers(entry),
		)
	if status != 201:
		raise AdminCliError("MCPA-006", _format_admin_token_operation_error(entry, "token generation", status, token_endpoint))
	print(json.dumps(data, indent=2, sort_keys=True))
	return 0


def _cmd_revoke_token(args: argparse.Namespace, tr: tracer | None = None) -> int:
	entry = _read_server_entry(_load_registry(_registry_path(args.registry)), _normalize_label(args.server))
	token_id = _build_token_id(args)
	token_endpoint = f"{entry.admin_endpoint}/tokens/{token_id}"
	with _admin_access(entry) as access:
		status, _ = _request_json(
			"DELETE",
			_server_url(access.base_url, token_endpoint),
			extra_headers=_admin_request_headers(entry),
		)
	if status != 204:
		raise AdminCliError("MCPA-005", _format_admin_token_operation_error(entry, "token revocation", status, token_endpoint))
	if tr is not None:
		tr.add_info(f"revoked bearer token '{token_id}'", "tool")
	return 0


def _cmd_verify_token(args: argparse.Namespace, tr: tracer | None = None) -> int:
	entry = _read_server_entry(_load_registry(_registry_path(args.registry)), _normalize_label(args.server))
	token = str(args.token or "").strip()
	if not token:
		raise ValueError("token must not be empty")
	payload = {
		"jsonrpc": "2.0",
		"id": 1,
		"method": "initialize",
		"params": {
			"protocolVersion": DEFAULT_PROTOCOL_VERSION,
			"capabilities": {},
			"clientInfo": {"name": "wtrl_mcp_admin", "version": "0.0.0"},
		},
	}
	with _admin_access(entry) as access:
		status, _ = _request_json(
			"POST",
			_server_url(access.base_url, entry.mcp_endpoint),
			payload,
			{"Authorization": f"Bearer {token}", **_admin_request_headers(entry)},
		)
	if status != 200:
		raise AdminCliError("MCPA-005" if status == 401 else "MCPA-004", _format_verify_status(status))
	if tr is not None:
		tr.add_info(_format_verify_status(status), "tool")
	return 0


def _cmd_list_tokens(args: argparse.Namespace, tr: tracer | None = None) -> int:
	entry = _read_server_entry(_load_registry(_registry_path(args.registry)), _normalize_label(args.server))
	token_endpoint = f"{entry.admin_endpoint}/tokens"
	with _admin_access(entry) as access:
		status, data = _request_json(
			"GET",
			_server_url(access.base_url, token_endpoint),
			extra_headers=_admin_request_headers(entry),
		)
	if status != 200:
		raise AdminCliError("MCPA-004", _format_admin_token_operation_error(entry, "token listing", status, token_endpoint))
	tokens = data.get("tokens", [])
	if not isinstance(tokens, list):
		raise AdminCliError("MCPA-004", f"server '{entry.label}' returned a malformed token list")
	rows: list[dict[str, str]] = []
	for token in tokens:
		if not isinstance(token, dict):
			continue
		rows.append(
			{
				"token_id": str(token.get("token_id") or ""),
				"user": str(token.get("user") or ""),
				"client": str(token.get("client") or ""),
				"location": str(token.get("location") or ""),
				"created_at": str(token.get("created_at") or ""),
				"expires_at": str(token.get("expires_at") or ""),
				"revoked_at": str(token.get("revoked_at") or ""),
			}
		)
	report = TableReport(
		kind="tokens",
		columns=(
			TableColumn("token_id", "Token ID"),
			TableColumn("user", "User"),
			TableColumn("client", "Client"),
			TableColumn("location", "Location"),
			TableColumn("created_at", "Created at"),
			TableColumn("expires_at", "Expires at"),
			TableColumn("revoked_at", "Revoked at"),
		),
		rows=rows,
	)
	if not report.rows:
		if args.out is not None or args.out_json is not None:
			_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
			return 0
		print("No tokens registered.")
		return 0
	_write_report(report, out=args.out, out_json=args.out_json, default_stream=sys.stdout)
	return 0


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(prog="wtrl_mcp_admin", description="Waterloo MCP admin helper")
	parser.add_argument(
		"--registry",
		help=f"Registry JSON file (default: {DEFAULT_REGISTRY_PATH})",
	)
	_add_diag_args(parser)
	subparsers = parser.add_subparsers(dest="command", required=True)

	prsr_add = subparsers.add_parser("add-server", help="Register a managed MCP server without contacting it yet.")
	prsr_add.add_argument("--label", required=True)
	prsr_add.add_argument("--url")
	prsr_add.add_argument("--host")
	prsr_add.add_argument("--port", type=int)
	prsr_add.add_argument("--mcp-endpoint", default=DEFAULT_MCP_ENDPOINT)
	prsr_add.add_argument("--admin-endpoint", default=DEFAULT_ADMIN_ENDPOINT)
	prsr_add.add_argument("--description", default="")
	prsr_add.set_defaults(func=_cmd_add_server)

	prsr_del = subparsers.add_parser("del-server", help="Remove a managed MCP server from the registry.")
	prsr_del.add_argument("--label", required=True)
	prsr_del.set_defaults(func=_cmd_del_server)

	prsr_list = subparsers.add_parser("list-servers", help="List registered MCP servers.")
	prsr_list.add_argument("--out", help='Write the human-readable table to FILE, "-" or "@STDOUT".')
	prsr_list.add_argument("--out-json", help='Write the JSON report to FILE, "-" or "@STDOUT".')
	prsr_list.set_defaults(func=_cmd_list_servers)

	prsr_ping = subparsers.add_parser("ping-servers", help="Ping registered MCP servers and report discovered identities.")
	prsr_ping.add_argument("--out", help='Write the human-readable table to FILE, "-" or "@STDOUT".')
	prsr_ping.add_argument("--out-json", help='Write the JSON report to FILE, "-" or "@STDOUT".')
	prsr_ping.set_defaults(func=_cmd_ping_servers)

	prsr_gen = subparsers.add_parser("gen-token", help="Generate a bearer token on a managed server.")
	prsr_gen.add_argument("--server", required=True)
	prsr_gen.add_argument("--token-id")
	prsr_gen.add_argument("--user")
	prsr_gen.add_argument("--client")
	prsr_gen.add_argument("--location")
	prsr_gen.add_argument("--expires-at")
	prsr_gen.add_argument("--notes")
	prsr_gen.set_defaults(func=_cmd_gen_token)

	prsr_revoke = subparsers.add_parser("revoke-token", help="Revoke a bearer token on a managed server.")
	prsr_revoke.add_argument("--server", required=True)
	prsr_revoke.add_argument("--token-id")
	prsr_revoke.add_argument("--user")
	prsr_revoke.add_argument("--client")
	prsr_revoke.add_argument("--location")
	prsr_revoke.set_defaults(func=_cmd_revoke_token)

	prsr_verify = subparsers.add_parser("verify-token", help="Verify a bearer token against a managed MCP server.")
	prsr_verify.add_argument("--server", required=True)
	prsr_verify.add_argument("--token", required=True)
	prsr_verify.set_defaults(func=_cmd_verify_token)

	prsr_tokens = subparsers.add_parser("list-tokens", help="List bearer tokens on a managed server.")
	prsr_tokens.add_argument("--server", required=True)
	prsr_tokens.add_argument("--out", help='Write the human-readable table to FILE, "-" or "@STDOUT".')
	prsr_tokens.add_argument("--out-json", help='Write the JSON report to FILE, "-" or "@STDOUT".')
	prsr_tokens.set_defaults(func=_cmd_list_tokens)

	return parser


def main(argv: list[str] | None = None) -> int:
	parser = build_parser()
	raw_argv = list(sys.argv[1:] if argv is None else argv)
	parsed_argv, out_diag, out_diag_json = _split_diag_args(raw_argv)
	args = parser.parse_args(parsed_argv)
	args.out_diag = out_diag
	args.out_diag_json = out_diag_json
	tr = tracer()
	try:
		tr.add_info(_command_info_message(str(args.command)))
		result = int(args.func(args, tr))
		if args.out_diag is not None or args.out_diag_json is not None:
			_emit_admin_diagnostics(tr, args.out_diag, args.out_diag_json)
		else:
			stderr = cast(io.TextIOBase, sys.stderr)
			emit_diagnostics(tr, stderr, debug=False, strip_ansi=_strip_ansi_for_stream(stderr))
		return result
	except AdminCliError as exc:
		tr.add_error(exc.rule_id, "tool", exc.message)
		if args.out_diag is not None or args.out_diag_json is not None:
			_emit_admin_diagnostics(tr, args.out_diag, args.out_diag_json)
		else:
			stderr = cast(io.TextIOBase, sys.stderr)
			emit_diagnostics(tr, stderr, debug=False, strip_ansi=_strip_ansi_for_stream(stderr))
		return exc.exit_code
	except ValueError as exc:
		_print_err(str(exc))
		return 2
	except RuntimeError as exc:
		tr.add_error("MCPA-003", "tool", str(exc))
		if args.out_diag is not None or args.out_diag_json is not None:
			_emit_admin_diagnostics(tr, args.out_diag, args.out_diag_json)
		else:
			_print_err(str(exc))
		return 1


if __name__ == "__main__":
	raise SystemExit(main())
