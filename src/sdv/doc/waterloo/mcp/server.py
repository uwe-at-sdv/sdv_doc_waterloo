"""Waterloo MCP server entry point."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import uvicorn
from starlette.middleware.cors import CORSMiddleware

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import TransportSecuritySettings

try:
	from . import __version__
	from .tools import list_docs
except ImportError:  # pragma: no cover
	from sdv.doc.waterloo.mcp import __version__
	from sdv.doc.waterloo.mcp.tools import list_docs


def _read_package_readme() -> str:
	path = Path(__file__).resolve().with_name("README")
	try:
		return path.read_text(encoding="utf-8").strip()
	except Exception:
		return "Waterloo MCP server"


def build_parser() -> argparse.ArgumentParser:
	"""Build the CLI parser for the minimal stdio server."""
	prsr = argparse.ArgumentParser(prog="wtrl_mcp", description="Waterloo MCP server")
	prsr.add_argument(
		"--transport",
		choices=("stdio", "streamable-http"),
		default="stdio",
		help="Transport protocol to use (stdio or streamable-http).",
	)
	prsr.add_argument(
		"--host",
		default="127.0.0.1",
		help="Host for streamable-http transport.",
	)
	prsr.add_argument(
		"--port",
		type=int,
		default=8000,
		help="Port for streamable-http transport.",
	)
	prsr.add_argument(
		"--streamable-http-path",
		default="/mcp",
		metavar="PATH",
		help="HTTP path for streamable-http transport.",
	)
	prsr.add_argument(
		"--allowed-origin",
		action="append",
		default=[],
		metavar="ORIGIN",
		help="Allow one browser Origin for streamable-http transport (repeatable).",
	)
	prsr.add_argument(
		"roots",
		nargs="+",
		metavar="ROOT",
		help="One or more Waterloo data roots (files or directories).",
	)
	return prsr


def _read_configured_roots() -> list[str]:
	raw = os.environ.get("WTRL_MCP_ROOTS", "")
	if not raw:
		return [str(Path.cwd())]
	return [item.strip() for item in raw.split(",") if item.strip()]


def _read_configured_origins() -> list[str]:
	raw = os.environ.get("WTRL_MCP_ALLOWED_ORIGINS", "")
	if not raw:
		return []
	return [item.strip() for item in raw.split(",") if item.strip()]


def _read_configured_hosts() -> list[str]:
	raw = os.environ.get("WTRL_MCP_ALLOWED_HOSTS", "")
	if not raw:
		return []
	return [item.strip() for item in raw.split(",") if item.strip()]


def build_app(roots: list[str] | None = None) -> FastMCP:
	"""Build the Waterloo MCP app with the configured data roots."""
	if roots is None:
		roots = _read_configured_roots()
	mcp = FastMCP(
		name="wtrl_mcp",
		instructions=_read_package_readme(),
		debug=False,
	)

	@mcp.tool(name="list_docs", description="List configured Waterloo data roots.")
	def _list_docs() -> list[dict[str, Any]]:
		return list_docs(list(roots))

	return mcp


def _wrap_browser_cors(app: Any, origins: list[str]) -> Any:
	"""Wrap an ASGI app with permissive browser CORS for MCP Inspector use."""
	return CORSMiddleware(
		app,
		allow_origins=origins,
		allow_methods=["GET", "POST", "DELETE"],
		allow_headers=["*"],
		expose_headers=["Mcp-Session-Id"],
	)


app = build_app()


def main(argv: list[str] | None = None) -> int:
	"""Start the Waterloo MCP server."""
	args = build_parser().parse_args(argv)
	mcp = build_app(list(args.roots))

	if args.transport == "streamable-http":
		mcp.settings.host = args.host
		mcp.settings.port = args.port
		mcp.settings.streamable_http_path = args.streamable_http_path
		allowed_origins = _read_configured_origins() + list(args.allowed_origin)
		allowed_hosts = _read_configured_hosts()
		if allowed_origins or allowed_hosts:
			mcp.settings.transport_security = TransportSecuritySettings(
				enable_dns_rebinding_protection=True,
				allowed_hosts=allowed_hosts,
				allowed_origins=allowed_origins,
			)
		browser_origins = allowed_origins
		http_app = mcp.streamable_http_app()
		if browser_origins:
			http_app = _wrap_browser_cors(http_app, browser_origins)
		# Stdio stays the default development transport. Streamable HTTP is
		# exposed directly here so browser clients can negotiate CORS.
		uvicorn.run(http_app, host=args.host, port=args.port, log_level="info")
		return 0

	# Stdio is the default development transport. SSE stays out of v1.
	mcp.run(transport="stdio")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
