Model Context Protocol
======================

Model Context Protocol, usually abbreviated MCP, is a simple way for an
application to expose tools and structured data to an LLM-based client.
Instead of asking the model to inspect files directly, the client talks to a
server that offers named tools such as discovery, lookup, and read-only data
access.

From the user's point of view, MCP is mostly an interoperability layer:
the client knows which tools exist, how to call them, and how to interpret
the results. The server keeps the actual data and behavior behind a small,
documented interface.

For Waterloo, that interface is used to expose JSON-based documentation data
and a small set of helper tools that make large documentation trees easier to
navigate from an LLM agent or a visual inspector.

The Waterloo MCP-Server
-----------------------

The Waterloo MCP-server applies that pattern to Waterloo documents in JSON
format. It gives LLM-agents a simple, standardized way to access and query the
documentation without loading the whole data set into the context window.
The server is implemented as a simple HTTP server that listens for JSON-RPC
requests and responds with JSON data. It can be integrated with LLM-agents
that support JSON-RPC.

Executable and configuration
----------------------------

The Waterloo package includes a ready-to-use configuration file for the MCP
server at :wtrl_file:`etc/wtrl_mcp.http.toml`.
Once the package is installed, the server can be started in a terminal with
the following command:

.. code-block:: bash

	wtrl_mcp --config etc/wtrl_mcp.http.toml

If the argument to :wtrl_cmd:`--config` is an absolute path, it is used as is.
If it is a relative path, :wtrl_cmd:`wtrl_mcp` first looks for the file
relative to the current working directory and then relative to the installed
Waterloo package root. The usual package-local configuration path is therefore
prefixed with :wtrl_file:`etc/`. If neither candidate exists, the server reports a
clear configuration error and exits.

The following configuration attributes are supported:

Server- and security-related
............................

.. rubric:: :wtrl_attr:`transport`\: :wtrl_type:`string`

Transport mode for the server. The current package supports
:wtrl_lit:`stdio` for local execution and editor-integrated clients such
as VS Code, and :wtrl_value:`streamable-http` for browser- and
Inspector-based access.

.. rubric:: :wtrl_attr:`host`\: :wtrl_type:`string`

Bind host for the MCP server. The HTTP transport usually binds to
:wtrl_value:`0.0.0.0`, which listens on all interfaces, so that local
clients, browser frontends, and container port mappings can reach it.
For stdio transport the host setting is not used in practice.

.. rubric:: :wtrl_attr:`port`\: :wtrl_type:`int`

Bind port for the HTTP transport. The default development port is
:wtrl_value:`13316`.

.. rubric:: :wtrl_attr:`streamable_http_path`\: :wtrl_type:`string`

Path component used for the HTTP endpoint. The current server uses
:wtrl_file:`/mcp`, so the resulting URL is typically
:wtrl_url:`http://127.0.0.1:13316/mcp` during local development.

.. rubric:: :wtrl_attr:`allowed_hosts`\: :wtrl_type:`List[string]`

Host allowlist used together with the HTTP transport. This protects the
server against DNS rebinding in browser-based deployments and is the
main knob for Inspector-based setups and containerized deployments.
When omitted, the server uses the configured values from the TOML file.

.. rubric:: :wtrl_attr:`allowed_origins`\: :wtrl_type:`List[string]`

Origin allowlist used for browser clients and CORS negotiation. This is
primarily relevant for the MCP Inspector and similar browser-based
frontends.

Authentication
..............

The server can optionally require Bearer-token authentication for MCP
requests. When auth is enabled, the server also exposes loopback-only
``/admin`` routes for token management.

.. warning::

   In the current implementation, bearer tokens are transmitted over plain
   HTTP. This is acceptable only on trusted networks, loopback connections,
   or SSH-tunneled setups. It is not sufficient for an internet-exposed
   server unless you add transport-layer protection elsewhere.

.. rubric:: :wtrl_attr:`enabled`\: :wtrl_type:`bool`

Toggle bearer-token verification for MCP requests. The default is
:wtrl_lit:`false`.

.. rubric:: :wtrl_attr:`token_store`\: :wtrl_type:`string`

Path to the JSON file with hashed token records. If this option is omitted,
the server uses ``${XDG_STATE_HOME:-~/.local/state}/wtrl_mcp/tokens.json`` for
user-mode operation. For system-wide service deployments, prefer an explicit
instance-specific path such as ``/var/lib/wtrl_mcp/<instance_label>/tokens.json``.

.. rubric:: :wtrl_attr:`realm`\: :wtrl_type:`string`

Stable label for auth responses and diagnostics. A good default is
:wtrl_value:`Waterloo MCP`.

Remote administration is expected to go through ``wtrl_mcp_admin`` and, when
needed, through an SSH tunnel to remote loopback. The admin API remains
loopback-only in v1; it is not meant to be exposed as a generally reachable
public interface.

Logging
.......

.. rubric:: :wtrl_attr:`level`\: :wtrl_type:`string`

Logging level for the server process. It controls how verbose the
Waterloo and Uvicorn log output should be.

.. rubric:: :wtrl_attr:`config_path`\: :wtrl_type:`string`

Optional path to a dedicated logging configuration file. When present,
the server loads that file instead of relying only on the built-in log
formatting defaults.

.. rubric:: :wtrl_attr:`access_log`\: :wtrl_type:`bool`

Toggle for the HTTP access log. This is useful when you want either a
quiet development console or a more detailed request trace.

Roots
.....

An arbitrary number of root entries can be provided.

Each root entry describes one Waterloo JSON document that the MCP server
offers to clients. The configured roots determine what the discovery,
lookup, and search tools can see.

.. rubric:: :wtrl_attr:`path`\: :wtrl_type:`string`

Path to the root document or root directory. Relative paths are resolved
against the configuration location; absolute paths are also supported.

.. rubric:: :wtrl_attr:`label`\: :wtrl_type:`string`

Human-readable label for the configured root. This label is used in MCP
responses and helps distinguish multiple roots.

.. rubric:: :wtrl_attr:`enabled`\: :wtrl_type:`bool`

Controls whether the root is active in the current server configuration.

.. rubric:: :wtrl_attr:`kind`\: :wtrl_type:`string`

Kind of root represented by the entry. The current server mainly uses
:wtrl_value:`wtrl-json`.



Tools
-----

The MCP-server supports the following tools:

The server is intentionally read-only in the current implementation.
It serves discovery, lookup, and inspection tools for Waterloo JSON
documentation roots. The same runtime also serves bundled prompt
templates and the ``wtrl-mcp://instructions`` resource that points
clients to the current package README.

.. rubric:: Tool discovery

- :wtrl_cmd:`describe_tool` — reads the Waterloo signature and docstring for one MCP tool.

.. rubric:: Root discovery and inventory

- :wtrl_cmd:`list_roots` — lists the configured Waterloo data roots.
- :wtrl_cmd:`get_root` — reads one configured Waterloo data root by :wtrl_var:`root_id`.
- :wtrl_cmd:`get_root_metadata` — reads only the compact header metadata of one configured Waterloo root by :wtrl_var:`root_id`.
- :wtrl_cmd:`list_objects` — lists all Waterloo objects in one configured root.

.. rubric:: Object content access

- :wtrl_cmd:`get_object` — reads one Waterloo object by :wtrl_var:`qid` from a configured root.
- :wtrl_cmd:`get_section` — reads one stored section of one Waterloo object.
- :wtrl_cmd:`get_subsection` — reads one stored subsection of one Waterloo object.
- :wtrl_cmd:`get_signature` — reads the stored signature block for one Waterloo object.

.. rubric:: Reference and graph lookup

- :wtrl_cmd:`get_references` — reads structured incoming :wtrl_label:`See_also` references for one Waterloo object.
- :wtrl_cmd:`search_related` — reads the star-shaped :wtrl_label:`See_also` neighborhood for one Waterloo object.

.. rubric:: Example lookup

- :wtrl_cmd:`get_examples` — reads structured example metadata for one Waterloo object.
- :wtrl_cmd:`get_example_source` — reads the source text for one canonical Waterloo example reference.

.. rubric:: Search tools

- :wtrl_cmd:`search_objects` — searches Waterloo objects by expression and structural filters.
- :wtrl_cmd:`search_sections` — searches Waterloo section and subsection labels by expression and structural filters.
- :wtrl_cmd:`search_text` — searches Waterloo text content by terms and structural filters.

.. rubric:: Authoring helper

- :wtrl_cmd:`gen_docstring` — generates a Waterloo docstring template for a given profile, with optional signature, template mode, and indentation mode.

Typical agent workflow
----------------------

The tools above are the catalog; the workflow below is a recommended way to
approach them when the agent does not already know the exact tool or target.
In practice there are two common starting points:

* discover the MCP tool set itself with :wtrl_cmd:`describe_tool`
* discover Waterloo content with :wtrl_cmd:`list_roots`

The lookup-oriented tools are then meant to be used in a simple progression.
This is only a recommended progression; agents that already know the target can
jump directly to the relevant :wtrl_cmd:`get_*` or :wtrl_cmd:`search_*` tool.

1. :wtrl_cmd:`list_roots` to discover available roots.
2. :wtrl_cmd:`describe_tool` when the agent wants to inspect the signature and Waterloo docstring of one MCP tool.
3. :wtrl_cmd:`list_objects` to inventory the objects in one root before drilling down.
4. :wtrl_cmd:`search_objects` to find candidate objects and obtain stable ``root_id`` / ``qid`` pairs.
5. :wtrl_cmd:`get_section` or :wtrl_cmd:`get_subsection` to inspect the relevant contract, notes, or other structured sections.
6. :wtrl_cmd:`search_sections` when the agent wants to find section or subsection labels rather than object names.
7. :wtrl_cmd:`get_signature` when the agent wants to inspect the canonical stored signature for one object.
8. :wtrl_cmd:`get_references` when the agent wants to inspect incoming structured See_also references for one object.
9. :wtrl_cmd:`search_related` when the agent wants a compact star-shaped See_also neighborhood around one object.
10. :wtrl_cmd:`get_examples` when the agent wants to inspect available example references for one object.
11. :wtrl_cmd:`get_example_source` when the agent wants to retrieve the raw source text for one canonical example reference.
12. :wtrl_cmd:`search_text` when the agent wants to search the actual content text with a small set of terms.
13. :wtrl_cmd:`gen_docstring` when the agent wants to draft or refine a Waterloo docstring template for a profile.

In practice this means that the agent can start with a vague name, narrow it
down to a canonical target, and then inspect the exact Waterloo text that
describes the object.


Using the MCP-server in VSCode
------------------------------

.. rubric:: HTTP transport

[Last tested with VSCode 1.115.0 on 2026-05-31]

With transport :wtrl_lit:`streamable-http`, the MCP-server is added to VSCode by:

	:wtrl_key:`Shift` + :wtrl_key:`Ctrl` + :wtrl_key:`P` and :wtrl_lit:`MCP: Open User Configuration`

The code to be added should look like

.. code-block:: json

	{
	    "servers": {
	    	"waterloo-docs": {
	        	"type": "http",
	        	"url": "http://127.0.0.1:13316/mcp"
	     	}
	    }
	}
	
where the :wtrl_attr:`url` is the URL of the MCP server. Use the host and port
from the running server configuration, and make sure the URL matches the
configured :wtrl_lit:`streamable-http` endpoint. The MCP server must be
running and accessible at that URL for the integration to work. As a smoke
test, open the MCP panel in VSCode and see whether it connects successfully.
Then ask Copilot to run :wtrl_cmd:`list_roots` and check whether it returns the
expected list of documents.

.. rubric:: Stdio transport

With transport :wtrl_lit:`stdio`, the setup is usually more convenient for
day-to-day use because no separate terminal and no TCP port are needed. If the
Waterloo extension and the Python package :wtrl_file:`sdv.doc.waterloo` are
installed, VSCode can talk to the MCP-server directly through the stdio
transport. The extension contributes the server automatically, so the user does
not need to add a JSON server definition by hand.

The default configuration lives in :wtrl_file:`etc/wtrl_mcp.stdio.toml`. If you
want to customize the roots or other settings, make a copy of that file and
point VSCode to the copy. Open the command palette with
:wtrl_key:`Shift` + :wtrl_key:`Ctrl` + :wtrl_key:`P`, choose :wtrl_lit:`MCP: Open User Configuration`, and
then set :wtrl_lit:`waterloo.mcpConfigPath` to your copied stdio configuration.
The path may be absolute (recommended) or relative; if it is relative, the extension also
looks in the open workspace and in the installed Waterloo package root.

If you want to disable the automatic MCP server contribution entirely, set
:wtrl_lit:`waterloo.mcpProvideServer` to ``false``. Otherwise the extension will
use the configured command and configuration path, with sensible defaults when
no custom path is given.

After saving the settings, open the MCP panel in VSCode and check whether the
server appears. As a smoke test, ask Copilot to run :wtrl_cmd:`list_roots` and
verify that the expected roots are returned.

Server error messages
---------------------

This section is normative.

The MCP implementation currently returns textual tool errors through the
FastMCP transport path. The Waterloo-specific error payload classes are kept
as a draft in :wtrl_file:`mcp/wtrl_error.py`, but the wire-level structure is
not normative yet.

The current lookup-oriented rule family is:

* [MCPS-001] -- unknown or missing ``root_id``.
* [MCPS-002] -- unknown ``qid``.
* [MCPS-003] -- unknown section name.
* [MCPS-004] -- unknown subsection name.
* [MCPS-005] -- root document too large for the ``get_root`` guardrail.
* [MCPS-006] -- unknown example reference.
* [MCPS-007] -- unknown tool name.

The current implementation already prefixes tool error messages with these
rule labels. A later version may map them more directly to structured
JSON-RPC error payloads if the MCP SDK exposes a better hook for that.


Running the MCP Server in a Docker Container
--------------------------------------------

To provide an MCP server in a platform-independent way,
:wtrl_cmd:`waterlint` can generate a Dockerfile and, depending on the selected mode,
one or two helper scripts from an MCP server configuration.

The generated container provides a complete deployment unit
for a Waterloo MCP server, including configuration and, optionally,
the referenced root documents.

The corresponding subcommand is :wtrl_cmd:`render-docker`.
The basic invocation syntax is:

.. code-block:: bash

	waterlint render-docker --in /path/to/mcp.toml --out /path/to/dockerfile

Two operating modes are available:

* :wtrl_opt:`--no-bake-roots` -- Root documents are mounted into the container at runtime.
* :wtrl_opt:`--bake-roots` (default) -- Root documents are embedded into the Docker image.

Additional options are described in the :wtrl_cmd:`waterlint` online help.
In particular, :wtrl_cmd:`render-docker` accepts :wtrl_opt:`--public-port`
to describe the externally published container port and
:wtrl_opt:`--allowed-hosts` to name the hosts that should be allowed for that
port in the generated configuration.

During development, or while actively extending a project's documentation,
the :wtrl_opt:`--no-bake-roots` mode is typically preferred. This avoids
rebuilding the Docker image whenever documentation changes; restarting the
container is sufficient.

Starting such a container manually would be inconvenient because the required
document roots must be mounted explicitly. Therefore,
:wtrl_cmd:`waterlint render-docker` additionally generates a launch script
for this mode. The script starts the container in the foreground and forwards
logging output to :wtrl_lit:`stdout`.

For deployment, the :wtrl_opt:`--bake-roots` mode is usually preferred,
because only a single artifact -- the Docker image itself -- needs to be distributed.

After generating the Dockerfile and scripts,
:wtrl_cmd:`waterlint render-docker` prints a number of example Docker commands,
including commands for running the container as a daemon.

The generated Docker image acts as a deployable Waterloo documentation service.
The overall workflow is illustrated in the following diagram:

.. image:: ../img/waterlint_pipeline_docker.svg
	:alt: Workflow for waterlint's Docker output
	:align: center

The package installation directory relevant for the following examples can be obtained using:

.. code-block:: bash

	python3 -c "import importlib.resources as r; print(r.files('sdv.doc.waterloo'))"

We refer to this path as :wtrl_file:`${ROOT}`.

Among other files, directory :wtrl_file:`${ROOT}/etc` contains an MCP server configuration
and a logging configuration referenced by that server configuration:

* :wtrl_file:`wtrl_mcp.http.toml`
* :wtrl_file:`logging.toml`

For example, the MCP server can be started with HTTP transport using:

.. code-block:: bash

	wtrl_mcp --config ${ROOT}/etc/wtrl_mcp.http.toml

This configuration defines an MCP server using transport
:wtrl_value:`streamable-http`, listening on port 13316.
The generated Docker image automatically exposes this port.

Bake Mode (:wtrl_opt:`--bake-roots`, default)
.............................................

We use the above configuration as an example for running the MCP server inside a Docker container:

.. code-block:: bash

	waterlint render-docker --in ${ROOT}/etc/wtrl_mcp.http.toml --out /tmp/my_wtrl_mcp

This generates Dockerfile :wtrl_file:`/tmp/my_wtrl_mcp`
and build script :wtrl_file:`/tmp/build.my_wtrl_mcp.sh`.
The build script uses :wtrl_opt:`--no-cache` by default and accepts
:wtrl_opt:`--cache` when you want to reuse Docker layers explicitly.
If the image will be published on a different port than the server listens on
inside the container, add for example
:wtrl_opt:`--public-port 13315 --allowed-hosts localhost 127.0.0.1`.

The Docker image is then built simply by executing:

.. code-block:: bash

	/tmp/build.my_wtrl_mcp.sh

Afterwards, Docker should list the image:

.. code-block:: bash

	docker image ls | grep my_wtrl_mcp

.. code-block:: text

	wtrl-mcp-my_wtrl_mcp    latest    bcd1f03f9682    34 seconds ago   274MB

The image can now be started in the foreground for testing.
It is important to forward the configured port number (13316 in this example):

.. code-block:: bash

	docker run --rm -p 13316:13316 wtrl-mcp-my_wtrl_mcp

The MCP server should report messages similar to the following
(line wrapping added for readability):

.. code-block:: text

	2026-06-06T06:29:03 INFO: WTRL Ready to serve via Uvicorn.
	2026-06-06T06:29:03 INFO: WTRL Loaded 1 configured roots.
	2026-06-06T06:29:03 INFO: WTRL Configured root:
	                          /shared/doc/wtrl_mcp.wtrl.core.rfc-2119.eb1497962ecf.json ...
	2026-06-06T06:29:03 INFO: WTRL Built reference index with 13 target entries
	                          and 39 source references.
	2026-06-06T06:29:03 INFO: Started server process [1] [_serve]
	2026-06-06T06:29:03 INFO: Waiting for application startup. [startup]
	2026-06-06T06:29:03 INFO: StreamableHTTP session manager started [run]
	2026-06-06T06:29:03 INFO: Application startup complete. [startup]
	2026-06-06T06:29:03 INFO: Uvicorn running on http://0.0.0.0:13316
	                          (Press CTRL+C to quit) [_log_started_message]

Alternatively, the container can be run as a daemon:

.. code-block:: bash

	docker run -d --name wtrl-mcp-my_wtrl_mcp -p 13316:13316 wtrl-mcp-my_wtrl_mcp

and stopped in the usual Docker way:

.. code-block:: bash

	docker stop wtrl-mcp-my_wtrl_mcp

No-Bake Mode (:wtrl_opt:`--no-bake-roots`)
..........................................

If the MCP server roots should not be embedded into the image,
generate the Dockerfile as follows:

.. code-block:: bash

	waterlint render-docker --in ${ROOT}/etc/wtrl_mcp.http.toml --out /tmp/my_wtrl_mcp --no-bake-roots

Unlike Bake Mode, an additional launch script
:wtrl_file:`/tmp/launch.my_wtrl_mcp.sh` is generated.

This script is required because manually starting the container becomes
impractical once the MCP server roots are supplied externally.

The image is built and started using:

.. code-block:: bash

	/tmp/build.my_wtrl_mcp.sh
	/tmp/launch.my_wtrl_mcp.sh

Logging is written to :wtrl_lit:`stdout`.

The container runs in the foreground and can be stopped with
:wtrl_key:`CTRL C`.


Authentication
--------------

The current implementation of :wtrl_cmd:`wtrl_mcp` supports
Bearer-token authentication for MCP requests.
:wtrl_cmd:`wtrl_mcp_admin` is used to manage the server and issue tokens.
Administrative access is intentionally loopback-only: the admin reaches the
server host over SSH and, when needed, opens an SSH tunnel to the remote
loopback interface. This keeps the admin path separate from normal client
access while still making remote administration practical.

In practice, the workflow can look like this:

1. The admin registers the server in the local admin configuration file:

.. code-block:: bash

	wtrl_mcp_admin add-server --label my_smart_server --url http://my_host:my_port

2. Once the MCP server is running, the admin generates a token:

.. code-block:: bash

	wtrl_mcp_admin gen-token --server my_smart_server --user alice --client vscode --location notebook


The server may respond with a JSON object such as

.. code-block:: json

	{
	  "client": "vscode",
	  "created_at": "2026-07-07T14:28:09Z",
	  "expires_at": null,
	  "location": "notebook",
	  "notes": null,
	  "revoked_at": null,
	  "token": "rGd3Gjts4zgRnqBELoCY7xuIQ_74P7Gm4OFmIXT0qgk",
	  "token_id": "alice-vscode-notebook",
	  "token_sha256": "b89321eda7bbdd9d7cdc2e2829aa6fe433d1c108205d7db647e7224d4c84984c",
	  "user": "alice"
	}

3. The admin sends the token
   :wtrl_value:`rGd3Gjts4zgRnqBELoCY7xuIQ_74P7Gm4OFmIXT0qgk`
   to the user through a secure channel, and the user stores it in the
   client configuration. From that point on, the client can authenticate
   against the MCP server.

Configuring the token in Codex
..............................

Codex can send the bearer token directly in the MCP server configuration.

.. code-block:: toml

	[mcp_servers.my_server]
	url = "http://<my_host>:<my_port>/mcp"
	http_headers = {
		Accept = "application/json, text/event-stream",
		Authorization = "Bearer rGd3Gjts4zgRnqBELoCY7xuIQ_74P7Gm4OFmIXT0qgk"
		}

Configuring the token in Claude
................................

Claude Code follows the same basic idea: configure the MCP server entry so
that outgoing requests include an :wtrl_lit:`Authorization: Bearer ...`
header. The exact file or dialog depends on the Claude integration version,
but the token value itself is the same.

.. code-block:: json

	{
	  "mcpServers": {
	    "my_smart_server": {
              "type": "http",
              "url": "http://<my_host>:<my_port>/mcp",
              "headers": {
        	"Authorization": "Bearer rGd3Gjts4zgRnqBELoCY7xuIQ_74P7Gm4OFmIXT0qgk"
              }
	    }
	  }
	}


Configuring the token in VS Code
................................

VS Code can also use the same bearer token, provided the MCP server entry
supports custom HTTP headers. Add an :wtrl_lit:`Authorization: Bearer ...`
header to the server configuration and point the client at the MCP URL.
The following pattern has been tested successfully with VS Code version 1.115.0:

.. code-block:: json

	{
	  "servers": {
	    "my_smart_server": {
	      "url": "http://<my_host>:<my_port>/mcp",
	      "type": "http",
	      "headers": {
	        "Authorization": "Bearer rGd3Gjts4zgRnqBELoCY7xuIQ_74P7Gm4OFmIXT0qgk"
	      }
	    }
	  },
	"inputs": []
	}
