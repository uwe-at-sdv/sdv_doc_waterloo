r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
Contract:
	general:
		|Must| provide a mechanism to create, list, revoke, and verify authentication tokens.
Public_classes:
	FileTokenVerifier
Public_functions:
	create_token, list_tokens, revoke_token, verify_token
Class_overview:
	FileTokenVerifier:
		Verify Bearer tokens against the file-based Waterloo token store and return MCP access-token records.
Function_overview:
	create_token:
		Create a new authentication token.
	list_tokens:
		List all authentication tokens.
	revoke_token:
		Revoke an existing authentication token.
	verify_token:
		Verify an authentication token.
"""
from __future__ import annotations

from copy import deepcopy
import fcntl
import hashlib
import json
import os
import secrets
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import re
from threading import RLock
from typing import Iterator

from mcp.server.auth.provider import AccessToken, TokenVerifier


_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z_0-9]*$")
_STORE_CACHE_LOCK = RLock()
_STORE_CACHE: dict[Path, tuple[int, int, dict[str, object]]] = {}


class AuthTokenError(ValueError):
	pass


class AuthTokenValidationError(AuthTokenError):
	pass


class AuthTokenConflictError(AuthTokenError):
	pass


class AuthTokenNotFoundError(AuthTokenError):
	pass


class FileTokenVerifier(TokenVerifier):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_variables, Public_methods
	Contract:
		general:
			|Must| verify Bearer tokens against the file-based Waterloo token store.
			|Must| return an MCP |type|`AccessToken` record for valid active tokens.
		constructor:
			|Must| take the path to the token store file.
	Public_variables:
		token_store_path:
			Path to the JSON token store file.
	Public_methods:
		verify_token:
			Verify one plaintext Bearer token and return an MCP access-token record if it is valid and active.
	"""

	def __init__(self, token_store_path: Path) -> None:
		self.token_store_path = token_store_path

	async def verify_token(self, token: str) -> AccessToken | None:
		record = verify_token(self.token_store_path, token)
		if record is None:
			return None
		token_id = record.get("token_id")
		if not isinstance(token_id, str) or not token_id:
			raise AuthTokenValidationError("Active token record is missing token_id.")
		expires_at = _parse_iso8601(record.get("expires_at"))
		expires_at_ts = None if expires_at is None else int(expires_at.timestamp())
		return AccessToken(
			token=token,
			client_id=token_id,
			scopes=[],
			expires_at=expires_at_ts,
		)


def _utc_now_iso() -> str:
	return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso8601(value: object) -> datetime | None:
	if value is None:
		return None
	if not isinstance(value, str):
		raise AuthTokenValidationError("expires_at must be a string or null.")
	text = value.strip()
	if not text:
		return None
	if text.endswith("Z"):
		text = text[:-1] + "+00:00"
	try:
		dt = datetime.fromisoformat(text)
	except ValueError as exc:
		raise AuthTokenValidationError("expires_at must be a valid ISO 8601 timestamp.") from exc
	if dt.tzinfo is None:
		raise AuthTokenValidationError("expires_at must include a timezone.")
	return dt.astimezone(timezone.utc)


def _validate_identifier(name: str, value: str, *, allow_any: bool) -> str:
	text = value.strip()
	if not text:
		raise AuthTokenValidationError(f"{name} must not be empty.")
	if allow_any and text == "any":
		return text
	if not _IDENTIFIER_RE.fullmatch(text):
		raise AuthTokenValidationError(
			f"{name} must match [a-zA-Z_][a-zA-Z_0-9]*" + (" or be 'any'." if allow_any else ".")
		)
	return text


def _normalize_token_identity(token_id: str) -> tuple[str, str, str, str]:
	token_id_text = str(token_id).strip()
	parts = token_id_text.split("-")
	if len(parts) != 3:
		raise AuthTokenValidationError("token_id must have the form <user>-<client>-<location>.")
	derived_user = _validate_identifier("token_id user segment", parts[0], allow_any=False)
	derived_client = _validate_identifier("token_id client segment", parts[1], allow_any=True)
	derived_location = _validate_identifier("token_id location segment", parts[2], allow_any=True)

	return token_id_text, derived_user, derived_client, derived_location


def _lock_path(path: Path) -> Path:
	return path.with_name(path.name + ".lock")


@contextmanager
def _exclusive_store_lock(path: Path) -> Iterator[None]:
	path.parent.mkdir(parents=True, exist_ok=True)
	lock_path = _lock_path(path)
	with lock_path.open("a+", encoding="utf-8") as fh:
		fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
		try:
			yield
		finally:
			fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def _empty_store() -> dict[str, object]:
	return {"tokens": []}


def _store_cache_key(path: Path) -> Path:
	return path.expanduser().resolve()


def _invalidate_store_cache(path: Path) -> None:
	key = _store_cache_key(path)
	with _STORE_CACHE_LOCK:
		_STORE_CACHE.pop(key, None)


def _load_store(path: Path) -> dict[str, object]:
	if not path.exists():
		_invalidate_store_cache(path)
		return _empty_store()
	cache_key = _store_cache_key(path)
	try:
		stat = path.stat()
	except OSError:
		return _empty_store()
	with _STORE_CACHE_LOCK:
		cached = _STORE_CACHE.get(cache_key)
		if cached is not None and cached[0] == stat.st_mtime_ns and cached[1] == stat.st_size:
			return deepcopy(cached[2])
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
	except json.JSONDecodeError as exc:
		raise AuthTokenValidationError(f"Token store is not valid JSON: {path}") from exc
	if not isinstance(data, dict):
		raise AuthTokenValidationError(f"Token store root must be a JSON object: {path}")
	tokens = data.get("tokens")
	if not isinstance(tokens, list):
		raise AuthTokenValidationError(f"Token store must contain a 'tokens' list: {path}")
	for entry in tokens:
		if not isinstance(entry, dict):
			raise AuthTokenValidationError(f"Token store contains a non-object token record: {path}")
	with _STORE_CACHE_LOCK:
		_STORE_CACHE[cache_key] = (stat.st_mtime_ns, stat.st_size, deepcopy(data))
	return data


def _write_store(path: Path, store: dict[str, object]) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	tmp_path = path.with_name(f"{path.name}.tmp.{os.getpid()}")
	tmp_path.write_text(json.dumps(store, indent=2, sort_keys=True) + "\n", encoding="utf-8")
	tmp_path.replace(path)
	_invalidate_store_cache(path)


def _token_records(store: dict[str, object]) -> list[dict[str, object]]:
	tokens = store.get("tokens")
	if not isinstance(tokens, list):
		raise AuthTokenValidationError("Token store must contain a 'tokens' list.")
	return [entry for entry in tokens if isinstance(entry, dict)]


def _is_active(record: dict[str, object], now: datetime | None = None) -> bool:
	now_dt = now or datetime.now(timezone.utc)
	revoked_at = record.get("revoked_at")
	if revoked_at not in (None, ""):
		return False
	expires_at = _parse_iso8601(record.get("expires_at"))
	if expires_at is not None and expires_at <= now_dt:
		return False
	return True


def _public_token_record(record: dict[str, object]) -> dict[str, object]:
	return {
		"token_sha256": record.get("token_sha256"),
		"token_id": record.get("token_id"),
		"user": record.get("user"),
		"client": record.get("client"),
		"location": record.get("location"),
		"created_at": record.get("created_at"),
		"expires_at": record.get("expires_at"),
		"revoked_at": record.get("revoked_at"),
		"notes": record.get("notes"),
	}


def create_token(path: Path,*,token_id: str,expires_at: object | None,notes: object | None) -> dict[str, object]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| create a new authentication token with the specified parameters.
			|Must| normalize token identity from token_id.
			|Must| ensure that the token_id is unique among active tokens.
			|Must| update the token store file atomically.
			|Must| return the plaintext token and the public token record.
		requires:
			Caller |Must| ensure that token_id has the form |lit|`<user>-<client>-<location>`.
			Caller |Must| ensure that |lit|`<user>` matches |lit|`[a-zA-Z_][a-zA-Z_0-9]*`.
			Caller |Must| ensure that |lit|`<client>` and |lit|`<location>` each match |lit|`[a-zA-Z_][a-zA-Z_0-9]*` or are exactly |lit|`any`.
	Parameters:
		path:
			Path to the token store file.
		token_id:
			Token id in the form <user>-<client>-<location>.
		expires_at:
			Optional expiration time in ISO 8601 format with timezone. Null or blank string means no expiry.
		notes:
			Optional notes for the token. Blank text is stored as null.
	Returns:
		A dictionary containing the plaintext token and the public token record.
	Raises:
		AuthTokenValidationError:
			|Must| raise if token_id or expires_at is invalid.
		AuthTokenConflictError:
			|Must| raise if an active token with the same token_id already exists.
	"""
	normalized_token_id, user_text, client_text, location_text = _normalize_token_identity(token_id)
	expires_at_dt = _parse_iso8601(expires_at)
	expires_at_text = None if expires_at_dt is None else expires_at_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
	notes_text = None if notes is None else str(notes).strip() or None

	with _exclusive_store_lock(path):
		store = _load_store(path)
		records = _token_records(store)
		active_matches = [record for record in records if record.get("token_id") == normalized_token_id and _is_active(record)]
		if active_matches:
			raise AuthTokenConflictError(f"An active token with id '{normalized_token_id}' already exists.")

		plaintext_token = secrets.token_urlsafe(32)
		token_sha256 = hashlib.sha256(plaintext_token.encode("utf-8")).hexdigest()
		record: dict[str, object] = {
			"token_sha256": token_sha256,
			"token_id": normalized_token_id,
			"user": user_text,
			"client": client_text,
			"location": location_text,
			"created_at": _utc_now_iso(),
			"expires_at": expires_at_text,
			"revoked_at": None,
			"notes": notes_text,
		}
		records.append(record)
		store["tokens"] = records
		_write_store(path, store)

	return {
		"token": plaintext_token,
		**_public_token_record(record),
	}


def list_tokens(path: Path) -> list[dict[str, object]]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| return a list of all authentication tokens in the store, sorted by token_id.
	Parameters:
		path:
			Path to the token store file.
	Returns:
		A list of dictionaries, each representing a public token record, sorted by token_id.
	Raises:
		AuthTokenValidationError:
			|Must| raise if the token store file is invalid.
	"""
	store = _load_store(path)
	records = [_public_token_record(record) for record in _token_records(store)]
	records.sort(key=lambda record: str(record.get("token_id") or ""))
	return records


def revoke_token(path: Path, token_id: str) -> dict[str, object]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| revoke the authentication token with the specified ID\
			by setting its revoked_at timestamp to the current UTC time.
			|Must| update the token store file atomically.
			|Must| return the public token record of the revoked token.
	Parameters:
		path:
			Path to the token store file.
		token_id:
			ID of the token to revoke.
	Returns:
		A dictionary representing the public token record of the revoked token.
	Raises:
		AuthTokenValidationError:
			|Must| raise if the provided token_id is empty or whitespace only.
		AuthTokenNotFoundError:
			|Must| raise if no active token with the provided ID exists.
		AuthTokenConflictError:
			|Must| raise if more than one active token with the provided ID exists.
	"""
	token_id_text = str(token_id).strip()
	if not token_id_text:
		raise AuthTokenValidationError("token_id must not be empty.")

	with _exclusive_store_lock(path):
		store = _load_store(path)
		records = _token_records(store)
		active_matches = [record for record in records if record.get("token_id") == token_id_text and _is_active(record)]
		if not active_matches:
			raise AuthTokenNotFoundError(f"No active token with id '{token_id_text}' exists.")
		if len(active_matches) > 1:
			raise AuthTokenConflictError(f"More than one active token with id '{token_id_text}' exists.")
		record = active_matches[0]
		record["revoked_at"] = _utc_now_iso()
		store["tokens"] = records
		_write_store(path, store)
		return _public_token_record(record)


def verify_token(path: Path, token: str) -> dict[str, object] | None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| verify the provided authentication token.
			|Must| return the public token record if the token is active, otherwise None.
	Parameters:
		path:
			Path to the token store file.
		token:
			Authentication token to verify.
	Returns:
		A dictionary representing the public token record of the active token, or None if the token is inactive or does not exist.
	Raises:
		AuthTokenValidationError:
			|Must| raise if the token store content is invalid.
	"""
	token_sha256 = hashlib.sha256(token.encode("utf-8")).hexdigest()
	store = _load_store(path)
	for record in _token_records(store):
		if record.get("token_sha256") != token_sha256:
			continue
		if not _is_active(record):
			return None
		return _public_token_record(record)
	return None
