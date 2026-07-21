### Sitemap

#### Public documentation

* Human-readable documentation
  * [https://uwe-at-sdv.github.io/sdv_doc_waterloo/](https://uwe-at-sdv.github.io/sdv_doc_waterloo/)
* Example for an interactive presentation (HTML)
  * [https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-html5/docitem_helper.wtrl.core.rfc-2119.html](https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-html5/docitem_helper.wtrl.core.rfc-2119.html)
* Example for LLM-ready documentation, best consumed either directly by a coding agent or through an MCP server
  * [https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-json/docitem_helper.wtrl.core.rfc-2119.json](https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-json/docitem_helper.wtrl.core.rfc-2119.json)
* Test/showcase for semantic markup (HTML)
  * [https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-html5/showcase_roles.wtrl.core.rfc-2119.html](https://uwe-at-sdv.github.io/sdv_doc_waterloo/doc-html5/showcase_roles.wtrl.core.rfc-2119.html)


#### Core package

* JSON-Schema
  * ``src/sdv/doc/waterloo/schema/wtrl-*-json-*.*.*.schema.json``
* Waterloo parser and linter source code
  * ``src/sdv/doc/waterloo``
* Documentation source (reST)
  * ``src/sdv/doc/waterloo/doc``
* MCP configuration and server code
  * ``src/sdv/doc/waterloo/mcp``
* Pytests orchestration and sample code
  * ``src/sdv/doc/waterloo/pytest``
  * ``src/sdv/doc/waterloo/examples-python``
  * ``src/sdv/doc/waterloo/examples-diagnostics-python``
* Images for public presentation (logos)
  * ``src/sdv/doc/waterloo/img``
* Tools (not well-documented)
  * ``src/sdv/doc/waterloo/tools``

#### IDE extras

* Additional utilities
  * Clone directly:
    * ``git clone --branch ide-plugins --single-branch https://github.com/uwe-at-sdv/sdv_doc_waterloo.git``
  * Lexer for ``pygments``
    * ``pygments/python_waterloo_lexer.py``
  * Extension for ``vscode``
    * Waterloo syntax highlighting
    * Context menu commands for docstring generation and validation
