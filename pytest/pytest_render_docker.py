#!/usr/bin/env python3
"""Pytests for the waterlint render-docker subcommand."""

from __future__ import annotations

from pathlib import Path
import shutil

from pytest_common import PATH_MODULE, run_waterlint

CONFIG = PATH_MODULE / "etc" / "wtrl_mcp.http.toml"
LOGGING_CONFIG = PATH_MODULE / "etc" / "logging.toml"
ROOT_JSON = PATH_MODULE / "mcp" / "doc-json" / "wtrl_mcp.wtrl.core.rfc-2119.json"


def _write_modified_config(tmp_path: Path, *, transport: str | None = None) -> Path:
	text = CONFIG.read_text(encoding="utf-8")
	text = text.replace('../mcp/doc-json/wtrl_mcp.wtrl.core.rfc-2119.json', str(ROOT_JSON))
	if transport is not None:
		text = text.replace('transport = "streamable-http"', f'transport = "{transport}"')
	path = tmp_path / "wtrl_mcp.http.toml"
	path.write_text(text, encoding="utf-8")
	shutil.copy2(LOGGING_CONFIG, tmp_path / "logging.toml")
	return path


def test_render_docker_bake_smoke_generates_dockerfile_and_build_script(tmp_path: Path) -> None:
	"""The default bake mode renders a Dockerfile and a build script."""
	cfg = _write_modified_config(tmp_path)
	out_file = tmp_path / "my_build.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), f"expected file not found: {out_file}"
	build_script = tmp_path / "build.my_build.docker.sh"
	assert build_script.exists(), f"expected file not found: {build_script}"
	assert build_script.stat().st_mode & 0o111, "build script is not executable"
	dockerfile = out_file.read_text(encoding="utf-8")
	assert "FROM\t\tpython:3.14.5-slim-trixie" in dockerfile
	assert "COPY\t\tshared/doc/ /shared/doc/" in dockerfile
	assert 'CMD\t\t["wtrl_mcp", "--config", "/workspace/etc/wtrl_mcp.http.toml"]' in dockerfile
	build_text = build_script.read_text(encoding="utf-8")
	assert "docker build" in build_text
	assert "Generated build script for my_build.docker." in build_text
	assert "--no-cache" in build_text
	assert "--cache" in build_text
	assert "wtrl-mcp-my_build" in build_text
	assert "http://127.0.0.1:13316/mcp" in res.stderr
	assert "http://localhost:13316/mcp" in res.stderr


def test_render_docker_public_port_overrides_allowed_hosts(tmp_path: Path) -> None:
	"""A public port without an explicit host list rewrites allowed_hosts to localhost and 127.0.0.1."""
	cfg = _write_modified_config(tmp_path)
	out_file = tmp_path / "public_port.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
		"--public-port",
		"12345",
	)
	assert res.returncode == 0, res.stderr
	build_script = tmp_path / "build.public_port.docker.sh"
	build_text = build_script.read_text(encoding="utf-8")
	assert 'allowed_hosts = [ "localhost:12345", "127.0.0.1:12345" ]' in build_text
	assert "render-docker: public port 12345" in res.stderr
	assert "http://localhost:12345/mcp" in res.stderr
	assert "http://127.0.0.1:12345/mcp" in res.stderr


def test_render_docker_public_port_and_allowed_hosts(tmp_path: Path) -> None:
	"""An explicit host list is combined with the public port."""
	cfg = _write_modified_config(tmp_path)
	out_file = tmp_path / "public_hosts.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
		"--public-port",
		"12345",
		"--allowed-hosts",
		"localhost",
		"127.0.0.1",
		"gilgamesh",
	)
	assert res.returncode == 0, res.stderr
	build_script = tmp_path / "build.public_hosts.docker.sh"
	build_text = build_script.read_text(encoding="utf-8")
	assert 'allowed_hosts = [ "localhost:12345", "127.0.0.1:12345", "gilgamesh:12345" ]' in build_text
	assert "render-docker: host allowlist localhost:12345, 127.0.0.1:12345, gilgamesh:12345" in res.stderr


def test_render_docker_rejects_allowed_hosts_without_public_port(tmp_path: Path) -> None:
	"""Explicit host names require an explicit public port."""
	cfg = _write_modified_config(tmp_path)
	out_file = tmp_path / "no_public_port.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
		"--allowed-hosts",
		"localhost",
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}"
	assert "DCKR-001" in res.stderr, res.stderr
	assert "--allowed-hosts requires --public-port" in res.stderr, res.stderr


def test_render_docker_no_bake_smoke_generates_launch_script(tmp_path: Path) -> None:
	"""The non-bake mode renders a build script and a foreground launch script."""
	cfg = _write_modified_config(tmp_path)
	out_file = tmp_path / "my_nobake.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
		"--no-bake-roots",
	)
	assert res.returncode == 0, res.stderr
	build_script = tmp_path / "build.my_nobake.docker.sh"
	launch_script = tmp_path / "launch.my_nobake.docker.sh"
	assert build_script.exists(), f"expected file not found: {build_script}"
	assert launch_script.exists(), f"expected file not found: {launch_script}"
	assert launch_script.stat().st_mode & 0o111, "launch script is not executable"
	launch_text = launch_script.read_text(encoding="utf-8")
	assert "docker run --rm -i -p 13316:13316" in launch_text
	assert "-v" in launch_text
	assert "wtrl-mcp-my_nobake" in launch_text
	assert "mount" in launch_text
	assert "http://127.0.0.1:13316/mcp" in res.stderr
	assert "http://localhost:13316/mcp" in res.stderr


def test_render_docker_rejects_non_http_transport(tmp_path: Path) -> None:
	"""A config with a non streamable-http transport fails with DCKR-001."""
	cfg = _write_modified_config(tmp_path, transport="stdio")
	out_file = tmp_path / "bad.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(cfg),
		"--out",
		str(out_file),
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}"
	assert "DCKR-001" in res.stderr, res.stderr
	assert "streamable-http" in res.stderr, res.stderr
	assert not out_file.exists(), "Dockerfile should not be created on invalid input"


def test_render_docker_rejects_missing_toml(tmp_path: Path) -> None:
	"""A missing input TOML fails with DCKR-003."""
	missing = tmp_path / "does_not_exist.toml"
	out_file = tmp_path / "missing.docker"
	res = run_waterlint(
		"render-docker",
		"--in",
		str(missing),
		"--out",
		str(out_file),
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}"
	assert "DCKR-003" in res.stderr, res.stderr
	assert "Input TOML file does not exist" in res.stderr, res.stderr
