This launches the MCP server with the bundled default configuration. The
package installs a ready-to-use `wtrl_mcp.toml` next to the server code inside
`site-packages/sdv/doc/waterloo/mcp/`, so the default startup command works
without any repository checkout.

If you want to inspect or customize the configuration, point `--config` to a
copy of that file and adjust the roots, host, port, and allowed origins as
needed.
