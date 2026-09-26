.. _html_output_layer:

The HTML Output Layer
=====================

Subsections in this chapter are informative unless normativity is explicitly stated.

Introduction
------------

The command :wtrl_cmd:`waterlint render-html5` converts a Waterloo JSON document
into a bundled, human-readable HTML5 artifact.
The input is therefore not a Python module and not a Waterloo docstring directly,
but a JSON document as described in chapter :doc:`json_io`.

The result is a single HTML file.
CSS and JavaScript are embedded directly into that file, so no additional assets
need to be deployed alongside it.
In practice, this has proven to be very convenient, because the generated
documentation can be opened, shared, and used offline without further setup.

At the moment, the HTML5 renderer is part of the reference tooling.
Conceptually, however, it should be understood as an output layer.
It is therefore possible that this functionality will later evolve toward
a plugin-like architecture with interchangeable renderers.

Rendering HTML5 Documentation
-----------------------------

The basic call is

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`path/to/input.json`
		| :wtrl_opt:`--out` :wtrl_file:`path/to/output.html`

Instead of :wtrl_opt:`--out`, option :wtrl_opt:`--out-dir` may be used:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`path/to/input.json`
		| :wtrl_opt:`--out-dir` :wtrl_file:`path/to/output-dir/`

In this case, :wtrl_cmd:`waterlint` generates a filename based on the input metadata,
in particular the scope and flavour stored in the JSON document.

The following options are particularly relevant:

	:wtrl_opt:`--css` :wtrl_file:`path/to/custom.css`
	:wtrl_opt:`--additional-css` :wtrl_file:`path/to/additional.css`
	:wtrl_opt:`--pygments-theme` :wtrl_value:`theme-name`
	:wtrl_opt:`--pygments-dark-theme` :wtrl_value:`theme-name`
	:wtrl_opt:`--no-render-preamble`

Option :wtrl_opt:`--css` replaces the built-in default stylesheet with a custom CSS file.
This is useful if the full visual presentation should be controlled externally.
If :wtrl_opt:`--additional-css` is also given, the additional stylesheet is appended
after the CSS provided via :wtrl_opt:`--css`.

Option :wtrl_opt:`--additional-css` appends the given CSS file after the primary stylesheet.
If :wtrl_opt:`--css` is not given, the built-in default stylesheet acts as the primary stylesheet.
This is useful if a shared base stylesheet should be adapted to a project-specific visual style.

Option :wtrl_opt:`--pygments-theme` selects the syntax-highlighting theme used for
embedded code examples in light mode.
Option :wtrl_opt:`--pygments-dark-theme` selects the corresponding theme for dark mode.
When the page theme is set to :wtrl_value:`auto`, the generated CSS follows the
system color-scheme preference.

Option :wtrl_opt:`--no-render-preamble` suppresses the section :wtrl_label:`Preamble:`
in the generated HTML output.
This can be useful when the output is intended primarily for human readers who do not
need to see the full structural metadata of the underlying Waterloo document.

Diagnostics are written in human-readable form by default.
The output locations for human- and machine-readable diagnostics are specified by

	:wtrl_opt:`--out-diag` :wtrl_file:`path/to/diagnostics`
	:wtrl_opt:`--out-diag-json` :wtrl_file:`path/to/diagnostics.json`

A summary of these options is displayed by

	:wtrl_cmd:`waterlint help` :wtrl_opt:`--topic` :wtrl_value:`render-html5`

.. rubric:: Example

Assume the JSON document from chapter :doc:`json_io` has already been generated
and is located at

	:wtrl_file:`doc/output-json/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.json`

We can then render the interactive HTML5 output by

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.html`

The generated artifact is then located at

	:wtrl_file:`doc/output-html/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.html`

If the visual style should be adapted, an additional stylesheet can be embedded:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
		| :wtrl_opt:`--additional-css` :wtrl_file:`path/to/additional.css`

Adding a custom header
----------------------

The header area above the rendered documentation can also be customized by
passing an HTML fragment file:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
		| :wtrl_opt:`--header-html` :wtrl_file:`doc/input-html/test_header_minimal.html`

The fragment must contain an element with ID :wtrl_value:`wtrl-title`, see rule RTHM-008 in :ref:`rendering_html`.
This element is populated dynamically with the qualified identifier of the
currently selected object.
An element with ID :wtrl_value:`wtrl-sub` is optional and, if present, is used
for a subtitle.

For example:

.. literalinclude:: ../input-html/test_header_minimal.html
	:language: html

If the header fragment refers to external assets, for example via
:wtrl_tag:`img src="..."`, the single-file property of the generated HTML
documentation is lost.
If this property should be preserved, small assets such as project logos can be
embedded directly into the header fragment as :wtrl_value:`data:` URIs.
For binary formats such as PNG, this is typically done with
:wtrl_value:`data:image/png;base64,...`.

On Unix-like systems, the Base64 payload can conveniently be generated on the
command line.
This approach is practical for small logos and keeps the resulting
documentation self-contained and usable offline.

A more elaborate example with embedded logo and project link is shown in

	:wtrl_file:`doc/input-html/test_header_tde4.html`
	:wtrl_file:`doc/input-html/test_header_tde4.css`

and can be used as follows:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/mypkg.test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
		| :wtrl_opt:`--header-html` :wtrl_file:`doc/input-html/test_header_tde4.html`
		| :wtrl_opt:`--additional-css` :wtrl_file:`doc/input-html/test_header_tde4.css`

Header fragment:

.. literalinclude:: ../input-html/test_header_tde4.html
	:language: html

Additional CSS:

.. literalinclude:: ../input-html/test_header_tde4.css
	:language: css

Implementation Notes
--------------------

The current implementation is distributed across three components:

* the Python command implementation in :wtrl_file:`waterlint_render_html5.py`
* the JavaScript asset in :wtrl_file:`js/waterlint_render_html5.js`
* the CSS stylesheet in :wtrl_file:`css/wtrl-style.css`

The Python layer prepares the bundled HTML document and injects the data.
The JavaScript layer provides the interactive behaviour in the browser,
for example search, navigation, and dynamic rendering of object details.
The CSS layer defines the visual presentation.

This separation is intentional.
It keeps the current implementation maintainable and also makes a later transition
toward a more explicit plugin or renderer architecture easier.

CSS Reference
-------------

This informative section reflects the implementation as of 2026-09-24.

This section defines the supported CSS customization surface of the bundled
HTML5 output. It documents CSS custom properties and selected structural
classes that are intended as extension hooks. Other selectors in the bundled
stylesheets are implementation details and may change when the renderer evolves.

The built-in stylesheet is split into a common set of semantic variables in
:wtrl_file:`css/common_styles.css` and HTML5-specific layout rules in
:wtrl_file:`css/wtrl-style.css`. An additional stylesheet passed through
:wtrl_opt:`--additional-css` is the recommended way to override these values.

Theme selection
~~~~~~~~~~~~~~~

The generated document records the selected theme on its root HTML element:

* :wtrl_value:`html[data-wtrl-theme="light"]` selects the light palette.
* :wtrl_value:`html[data-wtrl-theme="dark"]` selects the dark palette.
* :wtrl_value:`html[data-wtrl-theme="auto"]` follows the browser's
  :wtrl_value:`prefers-color-scheme` setting.

Light-mode variables are the active variables used by the layout rules. Dark
mode rebinds these active variables to corresponding dark values. This allows
a customization stylesheet to either replace a palette value globally or to
override an active value only for a selected theme.

Custom property naming
~~~~~~~~~~~~~~~~~~~~~~

Semantic inline roles use the following family:

.. code-block:: css

	--wtrl-<role>-color
	--wtrl-<role>-font-weight
	--wtrl-<role>-font-style
	--wtrl-dark-<role>-color

The role names currently are :wtrl_value:`plain`, :wtrl_value:`attr`,
:wtrl_value:`class`, :wtrl_value:`cmd`, :wtrl_value:`dfn`, :wtrl_value:`file`,
:wtrl_value:`func`, :wtrl_value:`key`, :wtrl_value:`label`, :wtrl_value:`lit`,
:wtrl_value:`mod`, :wtrl_value:`norm`, :wtrl_value:`op`, :wtrl_value:`opt`,
:wtrl_value:`pkg`, :wtrl_value:`tag`, :wtrl_value:`term`, :wtrl_value:`type`,
:wtrl_value:`url`, :wtrl_value:`url-schema`, :wtrl_value:`value`, and
:wtrl_value:`var`. The special :wtrl_value:`url-schema` role currently has a
color variable only.

For semantic roles with a dark palette entry, the light color
:wtrl_value:`--wtrl-<role>-color` is active by default. Dark-mode selectors
replace it with :wtrl_value:`--wtrl-dark-<role>-color`. Font weights and styles
are currently shared by both themes. The generic :wtrl_value:`plain` role uses
:wtrl_value:`currentColor` and has no dark counterpart.

HTML5-specific variables use a closely related, but intentionally distinct,
naming convention:

.. code-block:: css

	--wtrl-html-<name>
	--wtrl-html-dark-<name>

The active light-mode names and their purposes are listed below. Each has a
dark counterpart formed by inserting :wtrl_value:`dark-` after
:wtrl_value:`html-`.

.. list-table:: HTML5 color custom properties
	:widths: 42 58
	:header-rows: 1

	* - Light-mode property
	  - Purpose
	* - :wtrl_value:`--wtrl-html-page-bg`
	  - Page background.
	* - :wtrl_value:`--wtrl-html-page-color`
	  - Default foreground text color.
	* - :wtrl_value:`--wtrl-html-panel-bg`
	  - Sidebar and main-panel background.
	* - :wtrl_value:`--wtrl-html-panel-border-color`
	  - Sidebar, panel, and code-block borders.
	* - :wtrl_value:`--wtrl-html-debug-bg`
	  - Debug reference area background.
	* - :wtrl_value:`--wtrl-html-muted-color`
	  - De-emphasized text such as metadata.
	* - :wtrl_value:`--wtrl-html-subtle-color`
	  - Secondary metadata text.
	* - :wtrl_value:`--wtrl-html-control-bg`
	  - Input and button background.
	* - :wtrl_value:`--wtrl-html-control-color`
	  - Input and button foreground.
	* - :wtrl_value:`--wtrl-html-control-border-color`
	  - Input and button borders.
	* - :wtrl_value:`--wtrl-html-control-disabled-bg`
	  - Disabled control background.
	* - :wtrl_value:`--wtrl-html-search-border-color`
	  - Search field border.
	* - :wtrl_value:`--wtrl-html-hitlist-bg`
	  - Search-result list background.
	* - :wtrl_value:`--wtrl-html-hit-border-color`
	  - Search-result separators.
	* - :wtrl_value:`--wtrl-html-hit-hover-bg`
	  - Hovered search result and theme-control background.
	* - :wtrl_value:`--wtrl-html-section-bg`
	  - Section background.
	* - :wtrl_value:`--wtrl-html-section-border-color`
	  - Section borders.
	* - :wtrl_value:`--wtrl-html-section-head-color`
	  - Section heading color.
	* - :wtrl_value:`--wtrl-html-subsection-head-color`
	  - Subsection heading and table-group-title color.
	* - :wtrl_value:`--wtrl-html-code-bg`
	  - Embedded example-code background.
	* - :wtrl_value:`--wtrl-html-key-border-color`
	  - Border for rendered keyboard keys.
	* - :wtrl_value:`--wtrl-html-grid-border-color`
	  - Table cell grid lines.
	* - :wtrl_value:`--wtrl-html-fallback-color`
	  - Fallback color for objects without a more specific kind.

The common stylesheet also provides
:wtrl_value:`--wtrl-monospace-font-family` for code-like text and the three
theme-symbol variables :wtrl_value:`--wtrl-theme-light-symbol`,
:wtrl_value:`--wtrl-theme-auto-symbol`, and :wtrl_value:`--wtrl-theme-dark-symbol`.
Their dark-mode counterparts are named :wtrl_value:`--wtrl-dark-theme-<mode>-symbol`.

.. rubric:: Minimal customization example

The following stylesheet adjusts only the panel and table-grid palette while
leaving all layout rules intact:

.. code-block:: css

	:root {
		--wtrl-html-panel-bg: #fcfcf8;
		--wtrl-html-grid-border-color: #c8c8bb;
	}

	html[data-wtrl-theme="dark"] {
		--wtrl-html-panel-bg: #20231f;
		--wtrl-html-grid-border-color: #536050;
	}

Structural class hooks
~~~~~~~~~~~~~~~~~~~~~~

The following classes are intended for project-specific layout adjustments:

* :wtrl_value:`.wtrl-app`, :wtrl_value:`.wtrl-side`, :wtrl_value:`.wtrl-main`,
  and :wtrl_value:`.wtrl-block` identify the overall application layout.
* :wtrl_value:`.wtrl-section`, :wtrl_value:`.wtrl-section-head`,
  :wtrl_value:`.wtrl-subsection`, and :wtrl_value:`.wtrl-subsection-head`
  identify generated documentation structure.
* :wtrl_value:`.wtrl-text` and :wtrl_value:`.wtrl-list` identify free-form
  textual content and generated lists.
* :wtrl_value:`.wtrl-table`, :wtrl_value:`.wtrl-table-group-title`,
  :wtrl_value:`.wtrl-table-header`, and :wtrl_value:`.wtrl-table-row`
  identify Waterloo table blocks.

The renderer also attaches semantic role classes such as
:wtrl_value:`.wtrl-func`, :wtrl_value:`.wtrl-type`, and :wtrl_value:`.wtrl-var`
to inline markup. Prefer the custom properties above for global role styling;
use role classes only when a local selector is required.

Visual reference
~~~~~~~~~~~~~~~~

.. todo::

	Screenshots are useful as examples of the intended visual result, especially
	for comparing light and dark themes or documenting a project-specific
	stylesheet. They are not normative and do not replace the custom-property and
	class contracts above. A small, annotated set of screenshots is preferable to
	trying to catalogue every renderer state.
