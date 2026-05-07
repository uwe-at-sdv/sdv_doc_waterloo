<p align="center">
	<img src="img/wtrl_logo_color.svg" alt="Waterloo Logo" width="240">
</p>

## README

### Sitemap

#### Branch gh-pages

* Human-readable documentation
  * ``https://...``

#### Branch ide-plugins

* Additional utilities
  * Clone directly:
    * ``git clone --branch ide-plugins --single-branch https://github.com/uwe-at-sdv/sdv_doc_waterloo.git``
  * Lexer for ``pygments``
    * ``pygments/python_waterloo_lexer.py``
  * Extension for ``vscode``
    * Waterloo syntax highlighting
    * Context menu commands for docstring generation and validation

#### Branch main

* Machine-readable documentation
  * ``src/sdv/doc/waterloo/doc-json/docitem.wtrl.*.*.json``
  * ``src/sdv/doc/waterloo/doc-json/docitem_sphinx.wtrl.*.*.json``

* JSON-Schema
  * ``src/sdv/doc/waterloo/schema/wtrl-json-*.*.*.schema.json``

* Public modules:
  * ``src/sdv/doc/waterloo/docitem.py``
  * ``src/sdv/doc/waterloo/docitem_convert.py``
  * ``src/sdv/doc/waterloo/docitem_sphinx.py``

* Change logs:
  * ``src/sdv/doc/waterloo/docitem.py`` following the definition of ``__version__``
  * ``src/sdv/doc/waterloo/waterlint.py`` following the definition of ``__version__``
