#!/bin/bash
set -euo pipefail

# The script is located in @main/pytest.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PACKAGE_MAIN=$(cd "$SCRIPT_DIR/.." && pwd)
PACKAGE_ROOT="$PACKAGE_MAIN/src/sdv/doc/waterloo"
ETC_DIR="$SCRIPT_DIR/etc"

cd "$SCRIPT_DIR"

export PYTHONPATH="$PACKAGE_MAIN/src${PYTHONPATH:+:$PYTHONPATH}"

NOAUTH_CONFIG_TEMPLATE="$ETC_DIR/wtrl_mcp.noauth.http.template.toml"
AUTH_CONFIG_TEMPLATE="$ETC_DIR/wtrl_mcp.auth.http.template.toml"
LOGGING_CONFIG="$ETC_DIR/logging.toml"

NOAUTH_CONFIG=""
AUTH_CONFIG=""
NOAUTH_LOG=""
AUTH_LOG=""
NOAUTH_PID=""
AUTH_PID=""
NOAUTH_MCP_URL=""
AUTH_BASE_URL=""

cleanup() {
	stop_server "${AUTH_PID:-}"
	stop_server "${NOAUTH_PID:-}"
	cleanup_config "${AUTH_CONFIG:-}"
	cleanup_config "${NOAUTH_CONFIG:-}"
	cleanup_log "${AUTH_LOG:-}"
	cleanup_log "${NOAUTH_LOG:-}"
}

stop_server() {
	local pid="${1:-}"
	if [ -z "$pid" ]; then
		return
	fi
	if kill -0 "$pid" 2>/dev/null; then
		kill "$pid"
		wait "$pid" 2>/dev/null || true
	fi
}

cleanup_config() {
	local path="${1:-}"
	if [ -n "$path" ] && [ -f "$path" ]; then
		rm -f "$path"
	fi
}

cleanup_log() {
	local path="${1:-}"
	if [ -n "$path" ] && [ -f "$path" ]; then
		rm -f "$path"
	fi
}

make_runtime_configs() {
	local result
	result=$(python3 "$SCRIPT_DIR/gen_auth_noauth_configs.py" "$NOAUTH_CONFIG_TEMPLATE" "$AUTH_CONFIG_TEMPLATE" "$LOGGING_CONFIG")
	eval "$result"
	echo "$result"
}

# Wait for the noauth-server by spinlock-querying its capabilities.
wait_for_noauth() {
	sleep 0.5
	local deadline=$((SECONDS + 10))
	local payload='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"run-sh","version":"0.0.0"}}}'
	while (( SECONDS < deadline )); do
		if curl -fsS -o /dev/null \
			-X POST "$NOAUTH_MCP_URL" \
			-H 'Origin: http://localhost:6274' \
			-H 'Content-Type: application/json' \
			-H 'Accept: application/json, text/event-stream' \
			-d "$payload"; then
			return
		fi
		sleep 0.2
	done
	echo "noauth MCP server did not become ready: $NOAUTH_MCP_URL" >&2
	[ -f "$NOAUTH_LOG" ] && { echo "----- noauth log -----" >&2; cat "$NOAUTH_LOG" >&2; }
	return 1
}

# Wait for the auth-server by spinlock-querying the admin/token path.
wait_for_auth() {
	sleep 0.5
	local deadline=$((SECONDS + 10))
	while (( SECONDS < deadline )); do
		if curl -fsS "$AUTH_BASE_URL/tokens" >/dev/null; then
			return
		fi
		sleep 0.2
	done
	echo "auth MCP server did not become ready: $AUTH_BASE_URL" >&2
	[ -f "$AUTH_LOG" ] && { echo "----- auth log -----" >&2; cat "$AUTH_LOG" >&2; }
	return 1
}

trap cleanup EXIT INT TERM

make_runtime_configs

python3 -m sdv.doc.waterloo.mcp.wtrl_server --config "$NOAUTH_CONFIG" >"$NOAUTH_LOG" 2>&1 &
NOAUTH_PID=$!

python3 -m sdv.doc.waterloo.mcp.wtrl_server --config "$AUTH_CONFIG" >"$AUTH_LOG" 2>&1 &
AUTH_PID=$!

wait_for_noauth
wait_for_auth

export WTRL_MCP_URL="$NOAUTH_MCP_URL"
export WTRL_MCP_NOAUTH_MCP_URL="$NOAUTH_MCP_URL"
export WTRL_MCP_ADMIN_URL="$AUTH_BASE_URL"
export WTRL_MCP_LAUNCHED=1

if [ "$#" -eq 0 ]; then
	set -- \
		pytest_mcp_about.py \
		pytest_mcp_auth.py \
		pytest_mcp_auth_live.py \
		pytest_mcp_extra.py \
		pytest_mcp_http.py \
		pytest_mcp_search.py \
		pytest_mcp_waterlint_qids.py \
		pytest_wtrl_server_security.py
fi

pytest "$@"
