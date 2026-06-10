r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide custom logging formatter classes for the Waterloo MCP server.
Public_classes:
	GroupingFormatter, GroupingAccessFormatter
Class_overview:
	GroupingFormatter:
		A log formatter that suppresses repeated timestamps within a burst of consecutive log records while also exposing the current request id to the format string.
	GroupingAccessFormatter:
		A Uvicorn access-log formatter that adds the current request id as a bracketed prefix before the normal access-log line.
Public_functions:
	allocate_request_id, set_request_id, reset_request_id, set_log_group_key, reset_log_group_key
Function_overview:
	allocate_request_id:
		Return a fresh request identifier for log prefixes.
	set_request_id:
		Store the current request identifier in request-local context for later log formatting.
	reset_request_id:
		Restore the previous request identifier after a request finishes.
	set_log_group_key:
		Store the current log-group key in request-local context for timestamp suppression.
	reset_log_group_key:
		Restore the previous log-group key after a request finishes.
"""

from __future__ import annotations

import contextvars
import itertools
import logging

from uvicorn.logging import AccessFormatter as _UvicornAccessFormatter
from uvicorn.logging import DefaultFormatter as _UvicornDefaultFormatter

_REQUEST_ID_SEQ = itertools.count(1)
_LOG_REQUEST_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("wtrl_log_request_id", default=None)
_LOG_GROUP_KEY: contextvars.ContextVar[str | None] = contextvars.ContextVar("wtrl_log_group_key", default=None)


def set_log_group_key(group_key: str | None) -> contextvars.Token[str | None]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
		scope:
			extension
	Contract:
		general:
			|Must| set the current log-group key in request-local context.
			|Must| make the value visible to the timestamp-grouping formatter for the current request task.
			|May| accept |value|`None` to clear the active request-local group key.
	Returns:
		A context token that can be passed to |func|`reset_log_group_key`.
	"""
	return _LOG_GROUP_KEY.set(group_key)


def reset_log_group_key(token: contextvars.Token[str | None]) -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
		scope:
			extension
	Contract:
		general:
			|Must| restore the previous log-group key in request-local context.
			|Must| accept a token previously returned by |func|`set_log_group_key`.
	Returns:
		No return value.
	"""
	_LOG_GROUP_KEY.reset(token)


def allocate_request_id() -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
		scope:
			extension
	Contract:
		general:
			|Must| return a fresh short request identifier for log prefixes.
			|Must| generate identifiers in a monotonically increasing sequence for the lifetime of the process.
	Returns:
		A short request identifier such as |value|`req-0001`.
	"""
	return f"req-{next(_REQUEST_ID_SEQ):04d}"


def set_request_id(request_id: str | None) -> contextvars.Token[str | None]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
		scope:
			extension
	Contract:
		general:
			|Must| set the current request identifier in request-local context.
			|Must| make the identifier visible to log formatters that emit request prefixes.
			|May| accept |value|`None` to clear the active request id.
	Returns:
		A context token that can be passed to |func|`reset_request_id`.
	"""
	return _LOG_REQUEST_ID.set(request_id)


def reset_request_id(token: contextvars.Token[str | None]) -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Returns
		scope:
			extension
	Contract:
		general:
			|Must| restore the previous request identifier in request-local context.
			|Must| accept a token previously returned by |func|`set_request_id`.
	Returns:
		No return value.
	"""
	_LOG_REQUEST_ID.reset(token)


class _RequestIdFormatterMixin:
	"""Inject the current request identifier into the log record."""

	def format(self, record: logging.LogRecord) -> str:
		request_id = _LOG_REQUEST_ID.get()
		if request_id is None:
			request_id = "-"
		record.wtrl_request_id = request_id
		return super().format(record)


class GroupingFormatter(_RequestIdFormatterMixin, _UvicornDefaultFormatter):
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
			|Must| extend |type|`uvicorn.logging.DefaultFormatter` with grouping timestamp suppression.
			|Must| emit the full formatted timestamp for the first log record in a group.
			|Must| replace the timestamp with an equal-width blank string for each subsequent record
			whose Unix creation time lies within |attr|`timestamp_window` seconds of the last
			record for which the timestamp was emitted.
			|Must| resume emitting the full timestamp when the configured time window has elapsed.
	Notes:
		Purpose:
			When several log records are emitted in a short burst, the timestamp repeats on
			every line and adds visual noise. Suppressing it within a configurable time window
			makes bursts easier to read at a glance without depending on timestamp precision.
			If a request-local log-group key is available, the suppression is tracked per group
			so interleaved requests do not borrow each other's timestamp window.
			The request id is always added as a bracketed prefix so adjacent log bursts can be
			correlated quickly.
		Thread_safety:
			The last-emission state is per-instance and not protected by a lock.
			For the typical single-process MCP server writing to stderr this is not an issue,
			but callers sharing one formatter instance across threads may occasionally see a
			full timestamp where suppression would have been correct.
	"""

	"""	constructor:
			|Must| accept the arguments of the underlying Uvicorn default formatter.
			|Must| accept |attr|`timestamp_window` as a positive floating-point number that controls the suppression window.
    """
	def __init__(
		self,
		fmt: str | None = None,
		datefmt: str | None = None,
		use_colors: bool = False,
		timestamp_window: float = 0.5,
	) -> None:
		if timestamp_window <= 0:
			raise ValueError("timestamp_window must be greater than zero")
		super().__init__(fmt=fmt, datefmt=datefmt, use_colors=use_colors)
		self.timestamp_window = timestamp_window
		self._last_timestamp_emission_by_group: dict[str, float] = {}

	def _current_group_key(self, record: logging.LogRecord) -> str:
		request_id = _LOG_REQUEST_ID.get()
		if request_id is not None:
			return request_id
		group_key = getattr(record, "wtrl_log_group_key", None)
		if group_key is None:
			group_key = _LOG_GROUP_KEY.get()
		if group_key is None:
			group_key = f"{record.name}:{record.process}:{record.thread}"
		return str(group_key)

	def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
		ts = super().formatTime(record, datefmt)
		group_key = self._current_group_key(record)
		last_ts = self._last_timestamp_emission_by_group.get(group_key)
		if last_ts is not None and 0 <= record.created - last_ts < self.timestamp_window:
			return " " * len(ts)
		self._last_timestamp_emission_by_group[group_key] = record.created
		return ts


class GroupingAccessFormatter(_RequestIdFormatterMixin, _UvicornAccessFormatter):
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
			|Must| extend |type|`uvicorn.logging.AccessFormatter`.
			|Must| inject the current request id into the log record before formatting.
			|Must| preserve the normal Uvicorn access-log fields and line structure apart from the additional request-id prefix.
		constructor:
			|Must| accept the same constructor arguments as the underlying Uvicorn access formatter.
	Notes:
		Purpose:
			The access formatter mirrors the request-id prefix used by the other Waterloo log lines so the entire request can be grouped visually.
		Behavior:
			If no request id is active, the formatter emits a placeholder prefix instead of failing.
	"""
