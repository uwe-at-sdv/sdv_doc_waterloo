.. _chapter_test_showcase_authoring_json:

Test: Showcase Authoring JSON
-----------------------------

This chapter presents the current profile-specific Waterloo Authoring JSON
showcases in their rendered docstring form. A showcase is an editable syntax
reference: it demonstrates the sections and content blocks that an Authoring
JSON document can use for one profile, including paragraphs, nested lists,
tables, and profile-specific sections where applicable.

Generate a showcase with :wtrl_cmd:`waterlint` before authoring or revising a
docstring, for example:

.. code-block:: console

	waterlint gen-showcase-authoring-json --profile function --out function-showcase.json

The generated JSON is a starting point for learning the format, not a template
to copy verbatim. Replace its placeholder identifiers, descriptions, and
normative statements with documentation appropriate for the actual object.
Use :wtrl_cmd:`validate-json` to validate the edited Authoring JSON and
:wtrl_cmd:`render-docstring` to produce the raw Waterloo docstring.

This page is intended as feedback for human readers. It makes the currently
distributed showcases visible in the documentation, so their practical shape
and coverage can be reviewed without first generating and rendering the JSON
files locally.

Profile: :wtrl_value:`module`
................................

.. literalinclude:: ../output-python/showcase_authoring_json_module.py
	:language: python
	:tab-width: 4

Profile: :wtrl_value:`class`
................................

.. literalinclude:: ../output-python/showcase_authoring_json_class.py
	:language: python
	:tab-width: 4

Profile: :wtrl_value:`function`
................................

.. literalinclude:: ../output-python/showcase_authoring_json_function.py
	:language: python
	:tab-width: 4

Profile: :wtrl_value:`method`
................................

.. literalinclude:: ../output-python/showcase_authoring_json_method.py
	:language: python
	:tab-width: 4

Profile: :wtrl_value:`inherited_method`
........................................

.. literalinclude:: ../output-python/showcase_authoring_json_inherited_method.py
	:language: python
	:tab-width: 4
