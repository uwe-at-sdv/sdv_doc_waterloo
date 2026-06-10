"""Minimal JSON-RPC echo server for stdio transport debugging."""

from __future__ import annotations

import json
import sys


def main() -> int:
	print("jsonrpc_echo: ready", file=sys.stderr, flush=True)
	for line in sys.stdin:
		text = line.rstrip("\n")
		if not text:
			continue
		try:
			payload = json.loads(text)
		except json.JSONDecodeError as exc:
			reply = {
				"jsonrpc": "2.0",
				"id": None,
				"error": {
					"code": -32700,
					"message": f"Parse error: {exc.msg}",
				},
			}
		else:
			reply = {
				"jsonrpc": "2.0",
				"id": payload.get("id"),
				"result": {
					"echo": payload,
				},
			}
		print(json.dumps(reply), flush=True)
	print("jsonrpc_echo: eof", file=sys.stderr, flush=True)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
