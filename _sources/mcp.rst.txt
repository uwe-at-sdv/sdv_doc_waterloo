Model Context Protocol
======================

Server error messages
---------------------

This section is normative.

The current lookup-oriented rule family is:

* [MCPS-001] -- unknown or missing ``root_id``.
* [MCPS-002] -- unknown ``qid``.
* [MCPS-003] -- unknown section name.
* [MCPS-004] -- unknown subsection name.
* [MCPS-005] -- root document too large for the ``get_root`` guardrail.

The current implementation already prefixes tool error messages with these
rule labels. A later version may map them more directly to structured
JSON-RPC error payloads if the MCP SDK exposes a better hook for that.

This section is intended as the normative source for MCP server lookup
errors.
