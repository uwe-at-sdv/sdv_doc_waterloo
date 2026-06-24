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
		|Must| provide a function |func|`render_docker` that serves as\
		the main entry point for the |cmd|`waterlint render-docker` subcommand.
Public_functions:
	render_docker, build_parser
"""

from __future__ import annotations

import argparse
import hashlib
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, TypedDict, cast

try:
	import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
	import tomli as tomllib

import sdv.doc.waterloo.waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import WTRL_TRACER_JSON_SCHEMA_VERSION, tracer

# Not relevant yet, but in case we set up a plugin concept,
# vendors should be encouraged to follow semantic versioning
# for their plugins.
__version__ = "0.1.1"
# Changelog:
# 0.1.1 [2026-06-09]: Fix the default build script GitHub token path to be outside the repository.
# 0.1.0 [2026-06-06]: Initial version.

#===== Typing ================================================#

class RenderServerConfig_t(TypedDict):
	transport: str
	host: str
	port: int
	streamable_http_path: str


class RenderLoggingConfig_t(TypedDict, total=False):
	level: str
	access_log: bool
	config_path: str


@dataclass(frozen=True)
class DockerRootPlan:
	index: int
	label: str
	kind: str
	enabled: bool
	source_path: Path
	canonical_path: Path
	root_id: str
	baked_path: Path
	run_path: Path
	render_name: str


@dataclass(frozen=True)
class DockerRenderPlan:
	source_path: Path
	base_dir: Path
	bake_roots: bool
	public_port: int | None
	allowed_hosts: list[str] | None
	server: RenderServerConfig_t
	logging: RenderLoggingConfig_t | None
	security: Mapping[str, Any] | None
	roots: list[DockerRootPlan]
	out_path: Path
	build_script_path: Path
	launch_script_path: Path | None


def _emit_tracer(tr: tracer, out_path: str | None, out_json_path: str | None = None, debug: bool = False) -> None:
	wl_common.emit_tracer(
		tr,
		out_path,
		out_json_path,
		debug=debug,
		callback_build_json_doc=lambda tr_: wl_common.build_tracer_json_doc(
			tr_,
			schema_version=WTRL_TRACER_JSON_SCHEMA_VERSION,
			waterloo_version=wl_common.WTRL_DOCITEM_VERSION,
			id_prefix="urn:waterlint:wtrl-tracer-json:render-docker",
			include_debug=False,
		),
	)


def _load_toml(path: Path) -> Mapping[str, object]:
	with path.open("rb") as fh:
		return cast(Mapping[str, object], tomllib.load(fh))


def _canonical_root_path(path_text: str) -> Path:
	return Path(path_text).expanduser().resolve()


def _root_id_for_path(path_text: str) -> str:
	canonical_path = _canonical_root_path(path_text)
	digest = hashlib.blake2s(str(canonical_path).encode("utf-8"), digest_size=6).hexdigest()
	return f"root:{digest}"


def _require_dict(val: object, ctx: str, tr: tracer, rule_id: str) -> Mapping[str, object] | None:
	if not isinstance(val, dict):
		tr.add_error(rule_id, "tool", f"{ctx} must be an object.")
		return None
	return val


def _require_str(val: object, ctx: str, tr: tracer, rule_id: str) -> str | None:
	if not isinstance(val, str) or not val:
		tr.add_error(rule_id, "tool", f"{ctx} must be a non-empty string.")
		return None
	return val


def _require_bool(val: object, ctx: str, tr: tracer, rule_id: str) -> bool | None:
	if not isinstance(val, bool):
		tr.add_error(rule_id, "tool", f"{ctx} must be a boolean.")
		return None
	return val


def _render_name_for_root(root_path: Path, root_id: str, seen_names: dict[str, int]) -> str:
	name = root_path.name
	digest = root_id.split(":", 1)[-1]
	if name.endswith(".json"):
		base = name[:-5]
		suffix = ".json"
	else:
		base = root_path.stem
		suffix = root_path.suffix
	candidate = f"{base}.{digest}{suffix}"
	count = seen_names.get(candidate, 0)
	seen_names[candidate] = count + 1
	if count == 0:
		return candidate
	return f"{base}.{digest}.{count}{suffix}"


def _normalize_roots(
	roots_raw: list[object],
	base_dir: Path,
	bake_roots: bool,
	tr: tracer,
) -> list[DockerRootPlan]:
	plans: list[DockerRootPlan] = []
	seen_names: dict[str, int] = {}
	for idx, root_raw in enumerate(roots_raw):
		root = _require_dict(root_raw, f"[[roots]].{idx}", tr, "DCKR-001")
		if root is None:
			continue
		path_text = _require_str(root.get("path"), f"[[roots]].{idx}.path", tr, "DCKR-001")
		label = _require_str(root.get("label"), f"[[roots]].{idx}.label", tr, "DCKR-001")
		kind = _require_str(root.get("kind"), f"[[roots]].{idx}.kind", tr, "DCKR-001")
		enabled_raw = root.get("enabled", True)
		enabled = _require_bool(enabled_raw, f"[[roots]].{idx}.enabled", tr, "DCKR-001")
		if path_text is None or label is None or kind is None or enabled is None:
			continue
		source_path = Path(path_text)
		if not source_path.is_absolute():
			source_path = (base_dir / source_path).resolve()
		else:
			source_path = source_path.expanduser().resolve()
		if not source_path.is_file():
			tr.add_error("DCKR-002", "tool", f"Root file does not exist: {source_path}")
			continue
		canonical_path = source_path
		root_id = _root_id_for_path(str(canonical_path))
		render_name = _render_name_for_root(canonical_path, root_id, seen_names)
		baked_path = Path("/shared/doc") / render_name
		if bake_roots:
			run_path = baked_path
		else:
			run_path = Path("/shared/doc") / f"{render_name}.mount" / source_path.name
		plans.append(
			DockerRootPlan(
				index=idx,
				label=label,
				kind=kind,
				enabled=enabled,
				source_path=source_path,
				canonical_path=canonical_path,
				root_id=root_id,
				baked_path=baked_path,
				run_path=run_path,
				render_name=render_name,
			)
		)
	return plans


def _toml_escape(text: str) -> str:
	return text.replace("\\", "\\\\").replace('"', '\\"')


def _toml_value(value: object) -> str:
	if isinstance(value, str):
		return f'"{_toml_escape(value)}"'
	if isinstance(value, bool):
		return "true" if value else "false"
	if isinstance(value, int) and not isinstance(value, bool):
		return str(value)
	if isinstance(value, float):
		return repr(value)
	if isinstance(value, list):
		return "[ " + ", ".join(_toml_value(item) for item in value) + " ]"
	raise TypeError(f"unsupported TOML value type: {type(value).__name__}")


def _render_root_toml(root: DockerRootPlan) -> list[str]:
	return [
		"[[roots]]",
		f"path = {_toml_value(str(root.run_path))}",
		f"label = {_toml_value(root.label)}",
		f"enabled = {_toml_value(root.enabled)}",
		f"kind = {_toml_value(root.kind)}",
	]


def _render_logging_toml(logging_cfg: RenderLoggingConfig_t | None, config_path_text: str | None = None) -> list[str]:
	if logging_cfg is None:
		return []
	lines = ["[logging]"]
	if "config_path" in logging_cfg:
		lines.append(f"config_path = {_toml_value(config_path_text or 'logging.toml')}")
	else:
		lines.append(f"level = {_toml_value(logging_cfg['level'])}")
		lines.append(f"access_log = {_toml_value(logging_cfg['access_log'])}")
	return lines


def _effective_allowed_hosts(plan: DockerRenderPlan) -> list[str] | None:
	if plan.allowed_hosts is not None:
		if plan.public_port is None:
			raise ValueError("--allowed-hosts requires --public-port.")
		return [f"{host}:{plan.public_port}" for host in plan.allowed_hosts]
	if plan.public_port is not None:
		return [f"localhost:{plan.public_port}", f"127.0.0.1:{plan.public_port}"]
	if plan.security is None:
		return None
	allowed_hosts = plan.security.get("allowed_hosts")
	if not isinstance(allowed_hosts, list):
		return None
	return [str(item) for item in allowed_hosts]


def _effective_security_cfg(plan: DockerRenderPlan) -> Mapping[str, Any] | None:
	if plan.security is None and plan.public_port is None and plan.allowed_hosts is None:
		return None
	effective = dict(plan.security or {})
	allowed_hosts = _effective_allowed_hosts(plan)
	if allowed_hosts is not None:
		effective["allowed_hosts"] = allowed_hosts
	return effective


def _render_security_toml(security_cfg: Mapping[str, Any] | None) -> list[str]:
	if security_cfg is None:
		return []
	lines = ["[security]"]
	for key, value in security_cfg.items():
		if value is None:
			continue
		lines.append(f"{key} = {_toml_value(value)}")
	return lines


def _render_client_urls(security_cfg: Mapping[str, Any] | None, streamable_http_path: str) -> list[str]:
	if security_cfg is None:
		return []
	allowed_hosts = security_cfg.get("allowed_hosts")
	if not isinstance(allowed_hosts, list):
		return []
	path = streamable_http_path if streamable_http_path.startswith("/") else f"/{streamable_http_path}"
	urls: list[str] = []
	for host in allowed_hosts:
		if not isinstance(host, str) or not host:
			continue
		base = host if host.startswith(("http://", "https://")) else f"http://{host}"
		urls.append(f"{base}{path}")
	return urls


def _render_config_text(plan: DockerRenderPlan) -> str:
	lines: list[str] = [
		"# Rendered Waterloo MCP server configuration.",
		"# Generated by waterlint render-docker.",
		"",
		"[server]",
		f"transport = {_toml_value(plan.server['transport'])}",
		f"host = {_toml_value('0.0.0.0')}",
		f"port = {_toml_value(plan.server['port'])}",
		f"streamable_http_path = {_toml_value(plan.server['streamable_http_path'])}",
		"",
	]
	effective_security = _effective_security_cfg(plan)
	lines.extend(_render_security_toml(effective_security))
	if effective_security is not None:
		lines.append("")
	if plan.logging is not None:
		lines.extend(_render_logging_toml(plan.logging, config_path_text="logging.toml"))
		lines.append("")
	for root in plan.roots:
		lines.extend(_render_root_toml(root))
		lines.append("")
	return "\n".join(lines).rstrip() + "\n"


def _render_dockerfile_text(plan: DockerRenderPlan) -> str:
	lines = [
		"# syntax=docker/dockerfile:1.7",
		"",
		"FROM\t\tpython:3.14.5-slim-trixie",
		"",
		"RUN\t\tapt-get update \\",
		"   \t\t && apt-get install -y --no-install-recommends bash git ca-certificates \\",
		"   \t\t && rm -rf /var/lib/apt/lists/*",
		"",
		"ENV\t\tPIP_DISABLE_PIP_VERSION_CHECK=1 \\",
		"\t\tPIP_NO_CACHE_DIR=1 \\",
		"\t\tGIT_TERMINAL_PROMPT=0",
		"",
		"WORKDIR\t\t/workspace",
		"",
		"# Set by render-docker.",
		"ARG\t\tWATERLOO_GIT_URL=https://github.com/uwe-at-sdv/sdv_doc_waterloo.git",
		"ARG\t\tWATERLOO_GIT_REF=main",
		"",
		"RUN\t\t--mount=type=secret,id=github_token,required=false \\",
		"\t\tset -eu; \\",
		"\t\tif [ -f /run/secrets/github_token ]; then \\",
		"\t\t\ttoken=\"$(cat /run/secrets/github_token)\"; \\",
		"\t\t\tgit config --global url.\"https://x-access-token:${token}@github.com/\".insteadOf \"https://github.com/\"; \\",
		"\t\tfi; \\",
		"\t\tpython -m pip install \"sdv_doc_waterloo @ git+${WATERLOO_GIT_URL}@${WATERLOO_GIT_REF}\"; \\",
		"\t\tpython - <<'PY'",
		"import sdv.doc.waterloo",
		"print(sdv.doc.waterloo.__file__)",
		"PY",
		"",
		"COPY\t\tetc/wtrl_mcp.http.toml /workspace/etc/wtrl_mcp.http.toml",
	]
	if plan.logging is not None and "config_path" in plan.logging:
		lines.append("COPY\t\tetc/logging.toml /workspace/etc/logging.toml")
	if plan.bake_roots:
		lines.append("COPY\t\tshared/doc/ /shared/doc/")
	lines.extend(
		[
			"",
			f"EXPOSE\t\t{plan.server['port']}",
			"",
			"ENTRYPOINT\t[\"wtrl_mcp\", \"--config\", \"/workspace/etc/wtrl_mcp.http.toml\"]",
			"",
			f"# Run with: docker run --rm -p {plan.server['port']}:{plan.server['port']} wtrl-mcp-{plan.out_path.stem}",
			f"# Extra wtrl_mcp args can be appended after the image name, for example:",
			f"#   docker run --rm -p {plan.server['port']}:{plan.server['port']} wtrl-mcp-{plan.out_path.stem} --allowed-hosts localhost gilgamesh",
		]
	)
	return "\n".join(lines) + "\n"


def _script_header(kind: str, plan: DockerRenderPlan) -> list[str]:
	mode = "bake-roots" if plan.bake_roots else "no-bake-roots"
	return [
		"#!/bin/sh",
		"set -eu",
		"",
		f"# Generated {kind} script for {plan.out_path.name}.",
		f"# Active mode: {mode}.",
	]


def _render_build_script_text(plan: DockerRenderPlan) -> str:
	lines = _script_header("build", plan)
	lines.extend(
		[
			"SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)",
			f"DOCKERFILE=\"$SCRIPT_DIR/{plan.out_path.name}\"",
			f"IMAGE_TAG=\"wtrl-mcp-{plan.out_path.stem}\"",
			# Only required as long as our github repository is private. We can remove this when
			# the repository is public. The secret is not part of the github repository and must
			# be provided by the user in a file at the specified path on the machine where the
			# build script is executed.
			"GITHUB_TOKEN_FILE=\"/server/devel/sdv/privat/uwe/source/sdv_doc_waterloo/etc/secrets/github.token\"",
			"# Docker layer caching is off by default; pass --cache to enable it.",
			'CACHE_FLAG="--no-cache"',
			'while [ "$#" -gt 0 ]; do',
			'\tcase "$1" in',
			'\t\t--cache)',
			'\t\t\tCACHE_FLAG=""',
			'\t\t\tshift',
			'\t\t\t;;',
			'\t\t--no-cache)',
			'\t\t\tCACHE_FLAG="--no-cache"',
			'\t\t\tshift',
			'\t\t\t;;',
			'\t\t*)',
			'\t\t\techo "Usage: $0 [--cache|--no-cache]" >&2',
			'\t\t\texit 2',
			'\t\t\t;;',
			'\tesac',
			'done',
			"",
			'BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/wtrl-mcp-build.XXXXXX")',
			'trap \'rm -rf "$BUILD_DIR"\' EXIT HUP INT TERM',
			'mkdir -p "$BUILD_DIR/etc"',
			'cp "$DOCKERFILE" "$BUILD_DIR/Dockerfile"',
			"cat <<'EOF' > \"$BUILD_DIR/etc/wtrl_mcp.http.toml\"",
			_render_config_text(plan).rstrip("\n"),
			"EOF",
		]
	)
	if plan.logging is not None and "config_path" in plan.logging:
		logging_source = plan.logging["config_path"]
		lines.extend(
			[
				f'cp {shlex.quote(logging_source)} "$BUILD_DIR/etc/logging.toml"',
			]
		)
	if plan.bake_roots:
		lines.extend(
			[
				'mkdir -p "$BUILD_DIR/shared/doc"',
			]
		)
		for root in plan.roots:
			lines.append(f'cp {shlex.quote(str(root.source_path))} "$BUILD_DIR/shared/doc/{root.render_name}"')
	lines.extend(
		[
			"",
			'if [ -f "$GITHUB_TOKEN_FILE" ]; then',
			'\texec docker build \\',
			'\t\t$CACHE_FLAG \\',
			'\t\t--build-arg WATERLOO_GIT_URL=https://github.com/uwe-at-sdv/sdv_doc_waterloo.git \\',
			'\t\t--build-arg WATERLOO_GIT_REF=main \\',
			'\t\t--secret id=github_token,src="$GITHUB_TOKEN_FILE" \\',
			'\t\t-t "$IMAGE_TAG" \\',
			'\t\t-f "$BUILD_DIR/Dockerfile" \\',
			'\t\t"$BUILD_DIR"',
			'fi',
			'exec docker build \\',
			'\t$CACHE_FLAG \\',
			'\t--build-arg WATERLOO_GIT_URL=https://github.com/uwe-at-sdv/sdv_doc_waterloo.git \\',
			'\t--build-arg WATERLOO_GIT_REF=main \\',
			'\t-t "$IMAGE_TAG" \\',
			'\t-f "$BUILD_DIR/Dockerfile" \\',
			'\t"$BUILD_DIR"',
		]
	)
	return "\n".join(lines) + "\n"


def _render_launch_script_text(plan: DockerRenderPlan) -> str:
	lines = _script_header("launch", plan)
	container_port = plan.server["port"]
	host_port = plan.public_port or container_port
	lines.extend(
		[
			"SCRIPT_DIR=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)",
			f"IMAGE_TAG=\"wtrl-mcp-{plan.out_path.stem}\"",
			"",
			f"exec docker run --rm -i -p {host_port}:{container_port} \\",
		]
	)
	for root in plan.roots:
		lines.append(
			f"\t-v {shlex.quote(str(root.source_path))}:{shlex.quote(str(root.run_path))} \\",
		)
	lines.extend(
		[
			'\t"$IMAGE_TAG" "$@"',
		]
	)
	return "\n".join(lines) + "\n"


def _write_executable_text(path: Path, text: str) -> None:
	path.write_text(text, encoding="utf-8")
	mode = path.stat().st_mode | 0o775
	path.chmod(mode)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _load_render_docker_plan(args: argparse.Namespace, tr: tracer) -> DockerRenderPlan | None:
	in_path = getattr(args, "input_file", None)
	out_path = getattr(args, "out_file", None)
	public_port = getattr(args, "public_port", None)
	allowed_hosts_arg = getattr(args, "allowed_hosts", None)
	if not in_path:
		tr.add_error("DCKR-000", "tool", "--in is required.")
		return None
	if not out_path:
		tr.add_error("DCKR-000", "tool", "--out is required.")
		return None
	if public_port is not None:
		if not isinstance(public_port, int) or not (1 <= public_port <= 65535):
			tr.add_error("DCKR-001", "tool", "--public-port must be an integer between 1 and 65535.")
			return None
	allowed_hosts: list[str] | None = None
	if allowed_hosts_arg is not None:
		if public_port is None:
			tr.add_error("DCKR-001", "tool", "--allowed-hosts requires --public-port.")
			return None
		allowed_hosts = []
		for idx, host in enumerate(allowed_hosts_arg):
			host_text = str(host).strip()
			if not host_text or ":" in host_text:
				tr.add_error("DCKR-001", "tool", f"--allowed-hosts entry {idx} must be a host name without a port.")
				return None
			allowed_hosts.append(host_text)
	src_path = Path(str(in_path)).expanduser().resolve()
	if not src_path.is_file():
		tr.add_error("DCKR-003", "tool", f"Input TOML file does not exist: {src_path}")
		return None
	try:
		raw = _load_toml(src_path)
	except Exception as exc:
		tr.add_error("DCKR-003", "tool", f"Cannot load TOML file: {exc}")
		return None
	server_raw = _require_dict(raw.get("server"), "[server]", tr, "DCKR-001")
	if server_raw is None:
		return None
	transport = _require_str(server_raw.get("transport"), "[server].transport", tr, "DCKR-001")
	host = _require_str(server_raw.get("host"), "[server].host", tr, "DCKR-001")
	port_raw = server_raw.get("port")
	if not isinstance(port_raw, int):
		tr.add_error("DCKR-001", "tool", "[server].port must be an integer.")
		port = None
	else:
		port = port_raw
	streamable_http_path = _require_str(server_raw.get("streamable_http_path"), "[server].streamable_http_path", tr, "DCKR-001")
	if transport is None or host is None or port is None or streamable_http_path is None:
		return None
	if transport != "streamable-http":
		tr.add_error("DCKR-001", "tool", "[server].transport must be streamable-http.")
		return None
	logging_raw_obj = raw.get("logging")
	logging_cfg: RenderLoggingConfig_t | None = None
	if logging_raw_obj is not None:
		logging_raw = _require_dict(logging_raw_obj, "[logging]", tr, "DCKR-001")
		if logging_raw is None:
			return None
		has_level = "level" in logging_raw or "access_log" in logging_raw
		has_config = "config_path" in logging_raw
		if has_config:
			cfg_text = _require_str(logging_raw.get("config_path"), "[logging].config_path", tr, "DCKR-001")
			if cfg_text is None:
				return None
			cfg_path = Path(cfg_text)
			if not cfg_path.is_absolute():
				cfg_path = (src_path.parent / cfg_path).resolve()
			else:
				cfg_path = cfg_path.expanduser().resolve()
			if not cfg_path.is_file():
				tr.add_error("DCKR-002", "tool", f"Logging config file does not exist: {cfg_path}")
				return None
			logging_cfg = {"config_path": str(cfg_path)}
			if has_level:
				level = logging_raw.get("level")
				access_raw = logging_raw.get("access_log")
				if isinstance(level, str):
					logging_cfg["level"] = level
				if isinstance(access_raw, bool):
					logging_cfg["access_log"] = access_raw
		else:
			level = _require_str(logging_raw.get("level"), "[logging].level", tr, "DCKR-001")
			access_raw = logging_raw.get("access_log")
			if level is None or not isinstance(access_raw, bool):
				tr.add_error("DCKR-001", "tool", "[logging] must provide level and access_log when config_path is absent.")
				return None
			logging_cfg = {"level": level, "access_log": access_raw}
	security_raw_obj = raw.get("security")
	security_cfg: Mapping[str, Any] | None = None
	if security_raw_obj is not None:
		security_raw = _require_dict(security_raw_obj, "[security]", tr, "DCKR-001")
		if security_raw is None:
			return None
		security_cfg = security_raw
	roots_raw_obj = raw.get("roots")
	if not isinstance(roots_raw_obj, list) or not roots_raw_obj:
		tr.add_error("DCKR-001", "tool", "[[roots]] must be a non-empty list.")
		return None
	bake_roots = bool(getattr(args, "bake_roots", True))
	roots = _normalize_roots(list(roots_raw_obj), src_path.parent, bake_roots, tr)
	if tr.has_errors():
		return None
	out_path_obj = Path(str(out_path)).expanduser().resolve()
	build_script_path = out_path_obj.with_name(f"build.{out_path_obj.name}.sh")
	launch_script_path = None if bake_roots else out_path_obj.with_name(f"launch.{out_path_obj.name}.sh")
	return DockerRenderPlan(
		source_path=src_path,
		base_dir=src_path.parent,
		bake_roots=bake_roots,
		public_port=public_port,
		allowed_hosts=allowed_hosts,
		server={"transport": transport, "host": host, "port": port, "streamable_http_path": streamable_http_path},
		logging=logging_cfg,
		security=security_cfg,
		roots=roots,
		out_path=out_path_obj,
		build_script_path=build_script_path,
		launch_script_path=launch_script_path,
	)

#=============================================================#

def render_docker(args: argparse.Namespace) -> int:
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
			|Must| read the Waterloo MCP server configuration from the TOML file passed via |opt|`--in`.
			|Must| validate the configuration and any files referenced by it before rendering.
			|Must| treat the directory containing the input TOML file as the base directory for resolving relative paths.
			|Must| render a Dockerfile that can start |cmd|`wtrl_mcp` with the validated configuration.
			|Must| expose the configured server port in the rendered builder.
			|Must| support a baking mode that copies the configured roots into a shared image directory such as |file|`/shared/doc`.
			|Must| use flat file names in that directory so that the copied roots remain easy to recognize in server logs.
			|Must| apply a deterministic deduplication strategy if two roots would otherwise map to the same file name.
			|Must| rewrite the |label|`[[roots]]` paths in the rendered configuration to point at the in-image copy locations.
			|Must| preserve the existing path-based root identity model, even if the resulting root identifiers differ between host and container deployments.
			|Must| support a non-baking mode that keeps the configured roots external and documents the required runtime mounts.
			|Must| describe a shared mount directory for non-baking mode such as |file|`/shared/doc`.
			|Must| mount each root file individually in non-baking mode, using a deterministic file path layout that keeps the roots easy to read in the server logs.
			|Must| emit a companion build script next to the rendered Dockerfile in all modes.
			|Must| derive the build script name from the |opt|`--out` path so that |file|`my_build.docker` produces |file|`build.my_build.docker.sh`.
			|Must| make the build script executable with mode |lit|`0o775`, or the closest equivalent on the target platform.
			|Must| have the build script invoke |cmd|`docker build` for the rendered Dockerfile.
			|Must| have the non-baking launch script start the container with the documented runtime mounts and enumerate them explicitly in the generated script.
			|Must| emit a companion launch script next to the rendered Dockerfile in non-baking mode.
			|Must| derive the launch script name from the |opt|`--out` path so that |file|`my_build.docker` produces |file|`launch.my_build.docker.sh`.
			|Must| make the launch script executable with mode |lit|`0o775`, or the closest equivalent on the target platform.
			|Must| have the launch script start the container in the foreground and propagate the container exit status.
			|Must| omit the launch script in baking mode.
			|Must| start each generated script with a short comment block that identifies the generated Dockerfile and the active mode.
			|Must| write one or more informative tracer messages that point at the rendered Dockerfile and the generated helper scripts.
			|Must| write human-readable diagnostic output to |opt|`--out-diag` when requested, with enough detail for an operator to see what was rendered and where helper scripts were written.
			|Must| write JSON diagnostic output to |opt|`--out-diag-json` when requested, with enough detail for downstream tooling to inspect the rendered artefacts and the selected mode.
			|Must| treat |opt|`--bake-roots` as the default mode and |opt|`--no-bake-roots` as the alternative.
			|Must| write the rendered builder to the file passed via |opt|`--out`.
			|Should| use a current slim Python 3.14 base image in the rendered Dockerfile.
			|Should| install |mod|`sdv.doc.waterloo` from GitHub at build time in the rendered Dockerfile.
	Parameters:
		args:
			The parsed command-line arguments for the |cmd|`waterlint render-docker` subcommand.
			|must| include the following attributes:
			* |attr|`in`: Path to the input TOML file containing the server configuration.
			* |attr|`out`: Path to the output file where the rendered Dockerfile should be written.
			It |may| include:
			* |attr|`fail_on_warning`: Whether warnings should influence the exit code.
			* |attr|`bake_roots`: Boolean switch indicating that the roots from the input TOML file are baked into the image. This is the default.
			* |attr|`no_bake_roots`: Boolean switch indicating that the roots from the input TOML file are not baked into the image.
			* |attr|`public_port`: Optional external port number used for generated host allowlists.
			* |attr|`allowed_hosts`: Optional list of hostnames used together with |attr|`public_port` to generate the host allowlist.
			* |attr|`out_diag`: Optional path to a human-readable diagnostics file. Default is |lit|`stdout`.
			* |attr|`out_diag_json`: Optional path to a JSON diagnostics file. Default is not to write JSON diagnostics.
			* |attr|`debug`: Reserved global flag for debug output.
	Returns:
		An integer exit code, where 0 indicates success and any non-zero value indicates an error.
	Raises:
	Notes:
		Concept:
			The idea is to wrap a functioning MCP server configuration in a Docker image,
			so that it can be easily deployed and run in a consistent environment.
			The input TOML file provides the necessary configuration for the MCP server,
			including transport settings, logging configuration, and roots.
			The output is a Dockerfile that can be used to build
			a Docker image with the specified configuration.
		Todo:
			An eventual |opt|`--target` option could render platform-specific helper scripts.
			The current mental model is:
			* |lit|`posix` remains the default target and would keep producing shell scripts such as
			* |file|`build.<out>.sh` and, in non-bake mode, |file|`launch.<out>.sh`.
			* |lit|`macos` would stay in the shell-script family and could add macOS-specific launch hints,
			* while still producing files such as |file|`build.<out>.sh` and, in non-bake mode, |file|`launch.<out>.sh`.
			* |lit|`windows` would instead produce PowerShell-oriented helper files such as
			* |file|`build.<out>.ps1` and, in non-bake mode, |file|`launch.<out>.ps1`.
			The Dockerfile itself would remain platform-neutral in both targets.
			The target would only affect the helper script syntax, mount syntax, quoting, and any
			host-side path adaptation that is needed for the launch path.
			For bake mode the generated Dockerfile and the build helper would still be the main artefacts;
			for non-bake mode the launch helper would remain the place where the host/container mapping is spelled out.
			Windows-specific details such as PowerShell line continuation, environment-variable access,
			and host path formatting should be handled there rather than in the Dockerfile.
			Target selection could start in an |lit|`automatic` mode and later be overridden explicitly
			with |opt|`--target` when the user wants to force a particular rendering style.
	"""
	tr = tracer()
	out_diag = getattr(args, "out_diag", None)
	out_diag_json = getattr(args, "out_diag_json", None)
	debug = bool(getattr(args, "debug", False))
	try:
		plan = _load_render_docker_plan(args, tr)
		if plan is None:
			_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
			return _final_exit_code(1, tr, getattr(args, "fail_on_warning", False))
		effective_security = _effective_security_cfg(plan)
		if plan.public_port is not None:
			tr.add_info(f"render-docker: public port {plan.public_port}")
		effective_allowed_hosts = _effective_allowed_hosts(plan)
		if effective_allowed_hosts is not None and (
			plan.public_port is not None or plan.allowed_hosts is not None
		):
			tr.add_info("render-docker: host allowlist " + ", ".join(effective_allowed_hosts))
		tr.add_info(f"render-docker: source config {plan.source_path}")
		tr.add_info(f"render-docker: mode {'bake-roots' if plan.bake_roots else 'no-bake-roots'}")
		tr.add_info(f"render-docker: build script {plan.build_script_path}")
		if plan.launch_script_path is not None:
			tr.add_info(f"render-docker: launch script {plan.launch_script_path}")
		for root in plan.roots:
			tr.add_info(
				"render-docker: ● "
				f"{root.root_id} -> {root.render_name} "
				f"[{root.label}, {'enabled' if root.enabled else 'disabled'}, {root.kind}]"
			)
		client_urls = _render_client_urls(effective_security, plan.server["streamable_http_path"])
		if client_urls:
			tr.add_info("render-docker: MCP client URL(s):")
			for url in client_urls:
				tr.add_info(f"render-docker: ● {url}")
		plan.out_path.parent.mkdir(parents=True, exist_ok=True)
		plan.out_path.write_text(_render_dockerfile_text(plan), encoding="utf-8")
		_write_executable_text(plan.build_script_path, _render_build_script_text(plan))
		if plan.launch_script_path is not None:
			_write_executable_text(plan.launch_script_path, _render_launch_script_text(plan))
		tr.add_info("render-docker: SUGGESTED NEXT STEPS:")
		tr.add_info(f"render-docker: ● Run the build script: {plan.build_script_path}")
		if plan.launch_script_path is not None:
			tr.add_info(f"render-docker: ● Run the launch script: {plan.launch_script_path}")
		if plan.bake_roots:
			image_tag = f"wtrl-mcp-{plan.out_path.stem}"
			container_port = plan.server["port"]
			host_port = plan.public_port or container_port
			tr.add_info("render-docker: ● Launch the container, for example:")
			tr.add_info(f"render-docker:   ○ docker run --rm -p {host_port}:{container_port} {image_tag}")
			if host_port != container_port:
				tr.add_info(
					f"render-docker:   ○ docker run --rm -p {host_port}:{container_port} {image_tag} --public-port {host_port} --allowed-hosts localhost gilgamesh"
				)
			else:
				tr.add_info(
					f"render-docker:   ○ docker run --rm -p {host_port}:{container_port} {image_tag} --allowed-hosts localhost gilgamesh"
				)
			tr.add_info(f"render-docker:   ○ docker run -d --name {image_tag} -p {host_port}:{container_port} {image_tag}")
		tr.add_info("render-docker: ● Inform your agents about the new MCP server URL.")
	except Exception as exc:
		tr.add_error("DCKR-999", "tool", f"Unexpected render-docker failure: {exc}")
		if not out_diag:
			wl_common.add_traceback(tr)
		_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
		return _final_exit_code(1, tr, getattr(args, "fail_on_warning", False))
	_emit_tracer(tr, out_diag, out_diag_json, debug=debug)
	return _final_exit_code(0, tr, getattr(args, "fail_on_warning", False))

def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
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
	Parameters:
		subparsers:
			The subparsers object to which the |cmd|`waterlint render-docker` subcommand should be added.
		parser_parts:
			A dictionary containing common parser parts that can be reused across different subcommands.
	Returns:
		|Must| return the configured render_docker subparser.
	Raises:
	"""
	prsr = subparsers.add_parser(
		"render-docker",
		help="Render a Dockerfile and helper scripts for a Waterloo MCP configuration",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument(
		"--in",
		dest="input_file",
		required=True,
		metavar="FILE",
		help="Waterloo MCP TOML configuration file.",
	)
	prsr.add_argument(
		"--out",
		dest="out_file",
		required=True,
		metavar="FILE",
		help="Write the rendered Dockerfile to FILE.",
	)
	prsr.add_argument(
		"--public-port",
		dest="public_port",
		type=int,
		metavar="PORT",
		help="External published port used for generated host allowlists and example docker run commands.",
	)
	prsr.add_argument(
		"--allowed-hosts",
		dest="allowed_hosts",
		nargs="+",
		metavar="HOST",
		help="Hostnames to combine with --public-port when generating the host allowlist.",
	)
	prsr.add_argument(
		"--debug",
		action="store_true",
		help="Emit debugging data to stderr (reserved).",
	)
	bake_group = prsr.add_mutually_exclusive_group()
	bake_group.add_argument(
		"--bake-roots",
		dest="bake_roots",
		action="store_true",
		default=True,
		help="Bake configured roots into the image (default).",
	)
	bake_group.add_argument(
		"--no-bake-roots",
		dest="bake_roots",
		action="store_false",
		help="Keep configured roots external and generate a launch script.",
	)
	prsr.set_defaults(no_bake_roots=False)
	return prsr
