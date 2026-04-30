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
	:wtrl_opt:`--no-render-preamble`

Option :wtrl_opt:`--css` replaces the built-in default stylesheet with a custom CSS file.
This is useful if the full visual presentation should be controlled externally.
If :wtrl_opt:`--additional-css` is also given, the additional stylesheet is appended
after the CSS provided via :wtrl_opt:`--css`.

Option :wtrl_opt:`--additional-css` appends the given CSS file after the primary stylesheet.
If :wtrl_opt:`--css` is not given, the built-in default stylesheet acts as the primary stylesheet.
This is useful if a shared base stylesheet should be adapted to a project-specific visual style.

Option :wtrl_opt:`--pygments-theme` selects the syntax-highlighting theme used for
embedded code examples.

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

	:wtrl_file:`doc/output-json/test_module_minimal.with_examples.wtrl.core.rfc-2119.json`

We can then render the interactive HTML5 output by

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/test_module_minimal.with_examples.wtrl.core.rfc-2119.html`

The generated artifact is then located at

	:wtrl_file:`doc/output-html/test_module_minimal.with_examples.wtrl.core.rfc-2119.html`

If the visual style should be adapted, an additional stylesheet can be embedded:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
		| :wtrl_opt:`--additional-css` :wtrl_file:`path/to/additional.css`

Adding a custom header
----------------------

The header area above the rendered documentation can also be customized by
passing an HTML fragment file:

	:wtrl_cmd:`waterlint render-html5`
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
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
		| :wtrl_opt:`--in` :wtrl_file:`doc/output-json/test_module_minimal.with_examples.wtrl.core.rfc-2119.json`
		| :wtrl_opt:`--out` :wtrl_file:`doc/output-html/test_module_minimal.with_examples.wtrl.core.rfc-2119.html`
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
