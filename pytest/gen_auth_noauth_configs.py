#!/usr/bin/env python3
"""Generate temporary MCP launcher configs for the pytest run.sh wrapper."""

from __future__ import annotations

import argparse
import shlex
import socket
import tempfile
from pathlib import Path


def _free_port(used: set[int] | None = None) -> int:
	used_ports: set[int] = set(used or set())
	try:
# This is in principle a robust test in order to identify a free port.
# The only drawback is a tiny racing situation after closing the socket,
# since another process could bind to the port.
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.bind(("127.0.0.1", 0))
			port = sock.getsockname()[1]
			if port not in used_ports:
				return port
	except OSError:
		pass
	for proc_net in (Path("/proc/net/tcp"), Path("/proc/net/tcp6")):
		if not proc_net.exists():
			continue
		lines = proc_net.read_text(encoding="utf-8").splitlines()[1:]
		for line in lines:
			columns = line.split()
			if len(columns) > 1 and ":" in columns[1]:
				used_ports.add(int(columns[1].split(":", 1)[1], 16))
	for port in range(7950, 8000):
		if port not in used_ports:
			return port
	raise RuntimeError("could not find a free port")


def _write_config(template: Path, port: int, *, logging_config: Path) -> Path:
	text = template.read_text(encoding="utf-8")
	text = text.replace("_IDENTITY_", f'identity = "wtrl-mcp-{port}"')
	text = text.replace("_PORT_", f"port = {port}")
	text = text.replace(
		"_ALLOWED_HOSTS_",
		f'allowed_hosts = ["127.0.0.1:{port}", "localhost:{port}"]',
	)
	text = text.replace("_CONFIG_PATH_", f'config_path = "{logging_config}"')
	token_store = Path.home() / ".local" / "state" / "wtrl_mcp" / f"tokens.{port}.json"
	text = text.replace("_TOKEN_STORE_", f'token_store = "{token_store}"')
	handle = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False)
	with handle:
		handle.write(text)
	return Path(handle.name)


def main() -> int:
	parser = argparse.ArgumentParser()
	parser.add_argument("noauth_template", type=Path)
	parser.add_argument("auth_template", type=Path)
	parser.add_argument("logging_config", type=Path)
	args = parser.parse_args()

	logging_config = args.logging_config.resolve()
	noauth_port = _free_port()
	auth_port = _free_port({noauth_port})
	noauth_path = _write_config(args.noauth_template, noauth_port, logging_config=logging_config)
	auth_path = _write_config(args.auth_template, auth_port, logging_config=logging_config)
	noauth_log = tempfile.NamedTemporaryFile(delete=False).name
	auth_log = tempfile.NamedTemporaryFile(delete=False).name

	print(f"NOAUTH_MCP_URL=http://127.0.0.1:{noauth_port}/mcp")
	print(f"AUTH_BASE_URL=http://127.0.0.1:{auth_port}/admin")
	print(f"NOAUTH_CONFIG={shlex.quote(str(noauth_path))}")
	print(f"AUTH_CONFIG={shlex.quote(str(auth_path))}")
	print(f"NOAUTH_LOG={shlex.quote(noauth_log)}")
	print(f"AUTH_LOG={shlex.quote(auth_log)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
