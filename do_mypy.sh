#!/bin/bash

# The script |must| apply mypy to a set of input files and report the results and further diagnostics according to the following specification.

# --- Environment / Preconditions ---
# The script |must| require Python 3.10 or higher for execution (sys.version_info >= (3,10)).
# The script |must| emit an error message to stderr and exit with code 2 if executed with Python 3.9 or lower.
#
# The script |must| ensure that mypy.ini is a readable regular file in the same directory as this script.
# The script |must| emit an error message to stderr and exit with code 2 if mypy.ini is missing, not a regular file, or not readable.

# --- Command line syntax ---
# The script |must| accept the following syntax on the command line:
#   <Option> ... <Option> <Input-File-Path> ... <Input-File-Path>
#
# IMPORTANT: The calling shell performs escaping and glob expansion. Therefore the script receives already-expanded
# path arguments. The script |must_not| perform any globbing on its own.
# Any wildcard characters (e.g. '*', '?', '[...]', '{...}', '**') that reach the script are treated as literal characters.
#
# The script |must| treat every <Input-File-Path> argument as a literal path string as received, without any transforms,
# normalization, rewriting, or path editing (including no realpath(), no resolving symlinks, no rewriting of separators).
#
# The script |must| emit an error message to stderr and exit with code 2 if any input path fails to resolve to an
# existing readable regular file.
# Concretely:
#   - if an input path does not exist -> exit 2
#   - if an input path exists but is not a regular file -> exit 2
#   - if an input file is not readable by the script -> exit 2
#
# The script |must| exit 2 if no input files are given.
#
# The script |must| de-duplicate the set of resolved input file paths using exact string equality of the resolved
# path arguments as received from the shell.
# The script |must| define a canonical input list by sorting the de-duplicated resolved paths in lexicographic order
# (bytewise / codepoint order of the path strings).
# The canonical input list |must| be used consistently for hashing and for invoking mypy.

# --- Parameter forwarding (Option A: argv-token forwarding) ---
# The script |must| accept a repeatable option:
#   --mypy-arg <ARG>
#
# Semantics:
# Each occurrence of --mypy-arg provides exactly one argv token for the mypy invocation.
# The script |must| forward each <ARG> value to mypy as exactly one argument, byte-for-byte identical to what the shell
# passed to the script (no additional parsing, splitting, unquoting, globbing, or interpretation).
#
# The script |must_not| attempt to interpret quoting characters inside <ARG> (such as single quotes or double quotes).
# Any quote characters inside <ARG> are treated as literal characters and are forwarded literally.
#
# The user (e.g. a Makefile author) is responsible for providing correct shell tokenization.
# Therefore, if a mypy option requires a value containing spaces, the value |must| be provided as its own --mypy-arg token,
# quoted at the call site so that it becomes one argv token, e.g.:
#   --mypy-arg --python-executable --mypy-arg "/path with spaces/python"
#
# Examples (normative):
# To forward: mypy --strict --ignore-missing-imports <inputs...>
# call:
#   <script> --mypy-arg --strict --mypy-arg --ignore-missing-imports <inputs...>
#
# To forward: mypy -a "val1 val2" -b val3 <inputs...>
# call:
#   <script> --mypy-arg -a --mypy-arg "val1 val2" --mypy-arg -b --mypy-arg val3 <inputs...>
#
# Validation:
# The script |must| treat the value of --mypy-arg as the immediately following argv token, regardless of whether that token
# starts with '-' or '--'.
# The script |must| emit an error message to stderr and exit with code 2 if --mypy-arg appears as the last command line
# token (i.e. there is no following token to consume as its value).

# --- Output directory ---
# The script |must| accept an option:
#   --out-dir <OUT-DIR>
# The value |must| be interpreted as:
#   - absolute if it starts with '/'
#   - otherwise relative to the current working directory at script start
#
# Default value for --out-dir is "/tmp".
# The resolved --out-dir |must| exist and be a directory.
# The script |must| emit an error message to stderr and exit with code 2 if --out-dir does not exist, is not a directory,
# or is not searchable and writable by the script.

# --- Outputs / paths ---
# The script |must| accept a switch:
#   --echo
#
# The script |must| accept an option:
#   --out-hash <OUT-HASH>
# <OUT-HASH> represents a relative output path for the hash as specified below in section "Hash analysis".
# Option --out-hash |must_not| have a default value.
#
# The script |must| accept an option:
#   --out-report <OUT-REPORT>
# <OUT-REPORT> represents an output path for mypy results.
# Default is /dev/stdout.
#
# The script |must| accept an option:
#   --out-ignore <OUT-IGNORE>
# <OUT-IGNORE> represents an output path for ignore-rules as found in the input.
# Default is /dev/stdout.
#
# <OUT-REPORT> and <OUT-IGNORE> |may| resolve to the same path.
# The script |must| write the report first and the ignore rules second.
#
# The script |must| emit an error message to stderr and exit with code 2 if an undefined option is passed.

# --- Resolution rules for out-* paths ---
# Each of <OUT-HASH>, <OUT-REPORT>, <OUT-IGNORE> |must| be treated as a literal path string (no globbing).
#
# Relative paths at --out-hash, --out-report, --out-ignore |must| be resolved relative to the resolved --out-dir.
# Absolute paths |must| remain absolute.
#
# The script |must| validate that each resolved output path is writable as follows:
#   - If the path exists:
#       - it |must| be writable by the script (open for writing must succeed)
#   - If the path does not exist:
#       - its parent directory |must| exist and be writable by the script
#       - the script |must| be able to create the file
#
# Special case: if the resolved output path is /dev/stdout or /dev/stderr, it |must| be considered writable.
#
# The script |must| emit an error message to stderr and exit with code 2 if any of <OUT-HASH>, <OUT-REPORT>, <OUT-IGNORE>
# fails this writability validation.

# --- Echo rules ---
# If --echo is enabled, the script |must| ensure that the results written to <OUT-REPORT> and <OUT-IGNORE> are echoed to
# stdout in the calling terminal, according to the following rules:
#   - |Must| echo the content written to <OUT-REPORT> iff <OUT-REPORT> resolves to an existing or newly-created regular file,
#     otherwise |must_not| echo.
#   - |Must| echo the content written to <OUT-IGNORE> iff <OUT-IGNORE> resolves to an existing or newly-created regular file,
#     otherwise |must_not| echo.
#
# Note: If <OUT-REPORT> or <OUT-IGNORE> is /dev/stdout, the content is already on stdout; this |must_not| be duplicated.

# --- Hash analysis ---
# If --out-hash is passed, |must| apply a hash-based process-on-demand as described below.
# If --out-hash is not passed, |must| skip the hash analysis and always process.
#
# |Must| compute a single md5 hash over the concatenation of the bytes of all input files in canonical input order.
# |Must| read input files as bytes (no text decoding) for hashing.
#
# |Must| compare the computed hash to the content of the file specified by --out-hash.
# A missing hash file means: not equal.
# If the hash file exists but does not match the required format, it means: not equal.
#
# |Must| end with status 0 if hashes are equal (and |must_not| run mypy, and |must_not| update any outputs).
# Otherwise |must| go ahead with processing.
#
# Hash file format: exactly 32 lowercase hex characters [0-9a-f] followed by a single trailing newline (ASCII 0x0a).

# --- Processing ---
# |Must| use the mypy.ini found in the same directory as this script for static typechecking.
#
# Invocation rule:
# The script |must| invoke mypy as a module using the same Python interpreter that executes the script:
#   <this-python> -m mypy ...
# This avoids ambiguity of which mypy executable is used.
#
# |Must| perform static type checking with mypy on all input files and write mypy's combined output to the file specified by
# --out-report (or the default).
# "Combined output" means: stdout and stderr are both captured; the script |must| write stdout first and stderr second to <OUT-REPORT>
# (this is considered "without modification" of each stream, but stream order is defined here).
#
# |Must| forward the exit code of mypy to the calling shell.
#
# --- Ignore rule scan ---
# |Must| apply the regular expression "#\\s*type:.*$" using Python 're' syntax on each input file interpreted as UTF-8 text.
# For decoding errors, the script |must| use UTF-8 with replacement (errors='replace') to ensure scanning completes.
#
# |Must| search for ignore rule patterns in all inputs and write the results to the file specified by --out-ignore (or the default).
# The format for each detected ignore rule in any given file is:
#   one single line: <file-basename> ":" <line-number> SPACE <matched-expression>
# Line numbers |must| be 1-based.
#
# --- Hash update policy ---
# If --out-hash is passed and processing was executed (i.e. hashes were not equal):
#   - |Must| update the hash file only if mypy exits with code 0.
#   - |Must_not| update the hash file if mypy exits with a non-zero code.
# When updating, the script |must| write exactly the hash file format specified above.

set -u

ORIG_CWD="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

fail() {
	echo "$1" >&2
	exit 2
}

# Defaults
OUT_DIR="/tmp"
OUT_HASH=""
OUT_REPORT="/dev/stdout"
OUT_IGNORE="/dev/stdout"
ECHO_RESULTS=0
declare -a MYPY_ARGS=()
declare -a INPUT_PATHS=()

# Option parsing
while [[ $# -gt 0 ]]; do
	case "$1" in
		--mypy-arg)
			[[ $# -ge 2 ]] || fail "missing argument after --mypy-arg"
			MYPY_ARGS+=("$2")
			shift 2
			;;
		--out-dir)
			[[ $# -ge 2 ]] || fail "missing argument after --out-dir"
			OUT_DIR="$2"
			shift 2
			;;
		--out-hash)
			[[ $# -ge 2 ]] || fail "missing argument after --out-hash"
			OUT_HASH="$2"
			shift 2
			;;
		--out-report)
			[[ $# -ge 2 ]] || fail "missing argument after --out-report"
			OUT_REPORT="$2"
			shift 2
			;;
		--out-ignore)
			[[ $# -ge 2 ]] || fail "missing argument after --out-ignore"
			OUT_IGNORE="$2"
			shift 2
			;;
		--echo)
			ECHO_RESULTS=1
			shift
			;;
		--*)
			fail "unknown option: $1"
			;;
		*)
			INPUT_PATHS+=("$1")
			shift
			;;
	esac
done

[[ ${#INPUT_PATHS[@]} -gt 0 ]] || fail "no input files provided"

# Resolve OUT_DIR
if [[ "$OUT_DIR" != /* ]]; then
	OUT_DIR="$ORIG_CWD/$OUT_DIR"
fi
[[ -d "$OUT_DIR" && -x "$OUT_DIR" && -w "$OUT_DIR" ]] || fail "out-dir not accessible: $OUT_DIR"

resolve_path() {
	local p="$1"
	if [[ "$p" == "/dev/stdout" || "$p" == "/dev/stderr" ]]; then
		printf '%s\n' "$p"
		return
	fi
	if [[ "$p" != /* ]]; then
		printf '%s\n' "$OUT_DIR/$p"
	else
		printf '%s\n' "$p"
	fi
}

OUT_REPORT_RESOLVED="$(resolve_path "$OUT_REPORT")"
OUT_IGNORE_RESOLVED="$(resolve_path "$OUT_IGNORE")"
OUT_HASH_RESOLVED=""
if [[ -n "$OUT_HASH" ]]; then
	OUT_HASH_RESOLVED="$(resolve_path "$OUT_HASH")"
fi

validate_writable_file() {
	local p="$1"
	if [[ "$p" == "/dev/stdout" || "$p" == "/dev/stderr" ]]; then
		return 0
	fi
	if [[ -e "$p" ]]; then
		[[ -f "$p" && -w "$p" ]] || fail "output path not writable file: $p"
	else
		local parent
		parent="$(dirname "$p")"
		[[ -d "$parent" && -w "$parent" ]] || fail "parent dir not writable: $parent"
	fi
}

validate_writable_file "$OUT_REPORT_RESOLVED"
validate_writable_file "$OUT_IGNORE_RESOLVED"
if [[ -n "$OUT_HASH_RESOLVED" ]]; then
	validate_writable_file "$OUT_HASH_RESOLVED"
fi

# Validate inputs: existence, regular file, readable; dedup then sort
declare -A SEEN=()
declare -a INPUT_DEDUP=()
for p in "${INPUT_PATHS[@]}"; do
	[[ -e "$p" ]] || fail "input does not exist: $p"
	[[ -f "$p" ]] || fail "input not a regular file: $p"
	[[ -r "$p" ]] || fail "input not readable: $p"
	if [[ -z "${SEEN[$p]+x}" ]]; then
		SEEN["$p"]=1
		INPUT_DEDUP+=("$p")
	fi
done
IFS=$'\n' INPUTS_SORTED=($(printf '%s\n' "${INPUT_DEDUP[@]}" | LC_ALL=C sort))
unset IFS

# Ensure mypy.ini exists in script directory
MYPY_INI="$SCRIPT_DIR/mypy.ini"
[[ -f "$MYPY_INI" && -r "$MYPY_INI" ]] || fail "mypy.ini missing or unreadable: $MYPY_INI"

# Python interpreter selection and version check
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	fail "python interpreter not found: $PYTHON_BIN"
fi
"$PYTHON_BIN" - <<'PY' >/dev/null || exit 2
import sys
sys.exit(0 if sys.version_info >= (3, 10) else 1)
PY
if [[ $? -ne 0 ]]; then
	fail "Python 3.10 or higher required"
fi

# Default mypy package-root handling for the editable-install layout.
# This avoids double-discovery of the same module both as a top-level file
# and as a namespace package member under package_main/src/sdv/...
PKG_MAIN_SRC="$SCRIPT_DIR/package_main/src"
if [[ -d "$PKG_MAIN_SRC" ]]; then
	if [[ -z "${MYPYPATH:-}" ]]; then
		export MYPYPATH="$PKG_MAIN_SRC"
	fi

	has_namespace_packages=0
	has_explicit_package_bases=0
	for arg in "${MYPY_ARGS[@]}"; do
		if [[ "$arg" == "--namespace-packages" ]]; then
			has_namespace_packages=1
		fi
		if [[ "$arg" == "--explicit-package-bases" ]]; then
			has_explicit_package_bases=1
		fi
	done

	if [[ $has_namespace_packages -eq 0 ]]; then
		MYPY_ARGS+=("--namespace-packages")
	fi
	if [[ $has_explicit_package_bases -eq 0 ]]; then
		MYPY_ARGS+=("--explicit-package-bases")
	fi
fi

compute_hash() {
	"$PYTHON_BIN" - "$@" <<'PY'
import hashlib, sys
hash_obj = hashlib.md5()
for path in sys.argv[1:]:
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            hash_obj.update(chunk)
print(hash_obj.hexdigest())
PY
}

# Hash analysis
if [[ -n "$OUT_HASH_RESOLVED" ]]; then
	NEW_HASH="$(compute_hash "${INPUTS_SORTED[@]}")"
	HASH_MATCH=0
	if [[ -f "$OUT_HASH_RESOLVED" ]]; then
		if [[ $(wc -l <"$OUT_HASH_RESOLVED") -eq 1 ]]; then
			if [[ $(head -n1 "$OUT_HASH_RESOLVED") =~ ^[0-9a-f]{32}$ ]]; then
				if [[ "$NEW_HASH" == "$(head -n1 "$OUT_HASH_RESOLVED")" ]]; then
					HASH_MATCH=1
				fi
			fi
		fi
	fi
	if [[ $HASH_MATCH -eq 1 ]]; then
		exit 0
	fi
fi

# Temporary files
TMP_OUT="$(mktemp "$OUT_DIR/mypy.out.XXXXXX")"
TMP_ERR="$(mktemp "$OUT_DIR/mypy.err.XXXXXX")"
TMP_IGNORE="$(mktemp "$OUT_DIR/mypy.ignore.XXXXXX")"
cleanup() {
	rm -f "$TMP_OUT" "$TMP_ERR" "$TMP_IGNORE"
}
trap cleanup EXIT

# Run mypy
"$PYTHON_BIN" -m mypy --config-file "$MYPY_INI" "${MYPY_ARGS[@]}" "${INPUTS_SORTED[@]}" >"$TMP_OUT" 2>"$TMP_ERR"
MYPY_STATUS=$?

# Write combined report (stdout then stderr)
cat "$TMP_OUT" >"$OUT_REPORT_RESOLVED"
cat "$TMP_ERR" >>"$OUT_REPORT_RESOLVED"

# Ignore rule scan
"$PYTHON_BIN" - "$TMP_IGNORE" "${INPUTS_SORTED[@]}" <<'PY'
import os, re, sys
out_path = sys.argv[1]
inputs = sys.argv[2:]
pat_type = re.compile(r"#\s*type:.*$")
pat_pragma = re.compile(r"#\s*pragma:.*$")
lines_out = []
for path in inputs:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            m_type = pat_type.search(line)
            m_pragma = pat_pragma.search(line)
            if m_type:
                lines_out.append(f"{os.path.basename(path)}:{lineno} {m_type.group(0).strip()}")
            if m_pragma:
                lines_out.append(f"{os.path.basename(path)}:{lineno} {m_pragma.group(0).strip()}")
with open(out_path, "w", encoding="utf-8") as out:
    out.write("\n".join(lines_out))
    if lines_out:
        out.write("\n")
PY

cp "$TMP_IGNORE" "$OUT_IGNORE_RESOLVED"

# Echo rules
if [[ $ECHO_RESULTS -eq 1 ]]; then
	if [[ "$OUT_REPORT_RESOLVED" != "/dev/stdout" && "$OUT_REPORT_RESOLVED" != "/dev/stderr" && -f "$OUT_REPORT_RESOLVED" ]]; then
		cat "$OUT_REPORT_RESOLVED"
	fi
	if [[ "$OUT_IGNORE_RESOLVED" != "/dev/stdout" && "$OUT_IGNORE_RESOLVED" != "/dev/stderr" && -f "$OUT_IGNORE_RESOLVED" ]]; then
		cat "$OUT_IGNORE_RESOLVED"
	fi
fi

# Hash update
if [[ $MYPY_STATUS -eq 0 && -n "$OUT_HASH_RESOLVED" ]]; then
	NEW_HASH="${NEW_HASH:-$(compute_hash "${INPUTS_SORTED[@]}")}"
	printf '%s\n' "$NEW_HASH" >"$OUT_HASH_RESOLVED"
fi

exit $MYPY_STATUS
