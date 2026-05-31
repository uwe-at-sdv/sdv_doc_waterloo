r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
	status:
		draft
	scope:
		extension
Contract:
	general:
		|Must| provide reusable Waterloo MCP error payload models and helpers.
Notes:
	Current_state:
		The structured error payloads are intentionally kept here as a draft for later use.
		The current FastMCP transport path still emits textual tool errors, so this module
		does not yet impose a normative wire format for structured MCP errors.
Public_classes:
	McpErrorData, InvalidParamMcpErrorData, CorruptRootMcpErrorData, LimitExceededMcpErrorData,
	McpToolError
Public_functions:
	mcp_error_data_json, make_invalid_param_error_data, make_corrupt_root_error_data, make_limit_exceeded_error_data
"""

from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel, ConfigDict

McpErrorKind_t = Literal["invalid_param", "corrupt_root", "limit_exceeded"]


class McpErrorData(BaseModel):
	"""
	Common structured metadata of one Waterloo MCP error.
	"""

	model_config = ConfigDict(extra="forbid")

	rule: str
	kind: McpErrorKind_t
	tool: str
	hint: str
	origin: str | None = None


class InvalidParamMcpErrorData(McpErrorData):
	"""Structured MCP payload for invalid-parameter errors."""

	model_config = ConfigDict(extra="forbid")

	kind: Literal["invalid_param"] = "invalid_param"
	field: str
	value: object
	expected: str


class CorruptRootMcpErrorData(McpErrorData):
	"""Structured MCP payload for damaged or unreadable root documents."""

	model_config = ConfigDict(extra="forbid")

	kind: Literal["corrupt_root"] = "corrupt_root"
	root_id: str
	root_path: str


class LimitExceededMcpErrorData(McpErrorData):
	"""Structured MCP payload for guardrail or size-limit conditions."""

	model_config = ConfigDict(extra="forbid")

	kind: Literal["limit_exceeded"] = "limit_exceeded"
	size_found: int
	size_allowed: int


def mcp_error_data_json(error: McpErrorData) -> dict[str, object]:
	"""Convert a structured Waterloo MCP error payload into a JSON-ready dict."""
	return cast(dict[str, object], error.model_dump(mode="python"))


class McpToolError(ValueError):
	"""Exception carrying a structured Waterloo MCP error payload."""

	def __init__(self, error_data: McpErrorData, detail: str) -> None:
		self.error_data = error_data
		self.detail = detail
		super().__init__(f"{error_data.rule}: {detail}")

	def to_json_data(self) -> dict[str, object]:
		"""Serialize the structured error payload to a JSON-ready dict."""
		return mcp_error_data_json(self.error_data)


def make_invalid_param_error_data(
	rule: str,
	tool: str,
	hint: str,
	field: str,
	value: object,
	expected: str,
	origin: str | None = None,
) -> InvalidParamMcpErrorData:
	"""Build structured error data for an invalid-parameter condition."""
	return InvalidParamMcpErrorData(
		rule=rule,
		tool=tool,
		hint=hint,
		origin=origin,
		field=field,
		value=value,
		expected=expected,
	)


def make_corrupt_root_error_data(
	rule: str,
	tool: str,
	hint: str,
	root_id: str,
	root_path: str,
	origin: str | None = None,
) -> CorruptRootMcpErrorData:
	"""Build structured error data for a damaged root document."""
	return CorruptRootMcpErrorData(
		rule=rule,
		tool=tool,
		hint=hint,
		origin=origin,
		root_id=root_id,
		root_path=root_path,
	)


def make_limit_exceeded_error_data(
	rule: str,
	tool: str,
	hint: str,
	size_found: int,
	size_allowed: int,
	origin: str | None = None,
) -> LimitExceededMcpErrorData:
	"""Build structured error data for a guardrail/size-limit condition."""
	return LimitExceededMcpErrorData(
		rule=rule,
		tool=tool,
		hint=hint,
		origin=origin,
		size_found=size_found,
		size_allowed=size_allowed,
	)
