Reference - Rendering Showcase
##############################

This chapter is primarily a reference showcase for the Sphinx rendering
layer. The Waterloo project itself is best understood as a toolkit
consisting of :wtrl_cmd:`waterlint`, the Pygments lexer, the MCP server,
and the VSCode extension.

Most users will not import the internal :wtrl_file:`docitem*.py` modules
directly in their own projects. Those modules are implementation details
of the toolkit and are documented here mainly so the rendered API can be
inspected in a structured form.

.. wtrl_push_current_scope:: core

.. wtrl_push_current_module:: sdv.doc.waterloo

Module :wtrl_mod:`docitem`
===========================

.. wtrl_autodoc_module:: docitem

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem

Fundamental helpers
-------------------

:wtrl_func:`get_obj_name`
...........................

.. wtrl_autodoc_function:: get_obj_name

:wtrl_func:`get_obj_fully_qualified_name`
.........................................

.. wtrl_autodoc_function:: get_obj_fully_qualified_name

:wtrl_func:`get_obj_path`
...........................

.. wtrl_autodoc_function:: get_obj_path

:wtrl_func:`get_obj_docstring`
..............................

.. wtrl_autodoc_function:: get_obj_docstring

:wtrl_func:`get_obj_annotations`
................................

.. wtrl_autodoc_function:: get_obj_annotations

:wtrl_func:`is_obj_module`
............................................

.. wtrl_autodoc_function:: is_obj_module

:wtrl_func:`is_obj_class`
............................................

.. wtrl_autodoc_function:: is_obj_class

:wtrl_func:`is_obj_function`
............................................

.. wtrl_autodoc_function:: is_obj_function

:wtrl_func:`is_obj_method_like`
............................................

.. wtrl_autodoc_function:: is_obj_method_like

:wtrl_func:`is_obj_documentable`
................................

.. wtrl_autodoc_function:: is_obj_documentable

:wtrl_func:`is_obj_named_value`
............................................

.. wtrl_autodoc_function:: is_obj_named_value

:wtrl_func:`get_func_obj_from_callable`
............................................

.. wtrl_autodoc_function:: get_func_obj_from_callable

Typechecking helpers
--------------------

:wtrl_func:`is_attr_annotated`
..............................

.. wtrl_autodoc_function:: is_attr_annotated

:wtrl_func:`is_attr_final`
..............................

.. wtrl_autodoc_function:: is_attr_final

Tokenizer functions
-------------------

:wtrl_func:`get_num_indent`
...........................

.. wtrl_autodoc_function:: get_num_indent

:wtrl_func:`parse_indent_docstring`
...................................

.. wtrl_autodoc_function:: parse_indent_docstring

:wtrl_func:`resolve_object`
...................................

.. wtrl_autodoc_function:: resolve_object

AST properties
--------------

:wtrl_func:`get_status`
...................................

.. wtrl_autodoc_function:: get_status

Per-object validators
---------------------

:wtrl_func:`validate_docstring_method`
......................................


.. wtrl_autodoc_function:: validate_docstring_method

:wtrl_func:`validate_docstring_class`
.....................................

.. wtrl_autodoc_function:: validate_docstring_class

:wtrl_func:`validate_docstring_module`
......................................

.. wtrl_autodoc_function:: validate_docstring_module

:wtrl_func:`validate_docstring`
...............................

.. wtrl_autodoc_function:: validate_docstring

Coverage validators
-------------------

:wtrl_func:`validate_class_class_coverage`
...........................................

.. wtrl_autodoc_function:: validate_class_class_coverage

:wtrl_func:`validate_class_method_coverage`
...........................................

.. wtrl_autodoc_function:: validate_class_method_coverage

:wtrl_func:`validate_class_constant_coverage`
.............................................

.. wtrl_autodoc_function:: validate_class_constant_coverage

:wtrl_func:`validate_class_coverage`
....................................

.. wtrl_autodoc_function:: validate_class_coverage

:wtrl_func:`validate_module_class_coverage`
...........................................

.. wtrl_autodoc_function:: validate_module_class_coverage

:wtrl_func:`validate_module_function_coverage`
..............................................

.. wtrl_autodoc_function:: validate_module_function_coverage

:wtrl_func:`validate_module_type_coverage`
..........................................

.. wtrl_autodoc_function:: validate_module_type_coverage

:wtrl_func:`validate_module_constant_coverage`
..............................................

.. wtrl_autodoc_function:: validate_module_constant_coverage

:wtrl_func:`validate_module_variable_coverage`
..............................................

.. wtrl_autodoc_function:: validate_module_variable_coverage

:wtrl_func:`validate_module_coverage`
.....................................

.. wtrl_autodoc_function:: validate_module_coverage

Additional helpers
------------------

:wtrl_func:`gen_documentable_objects`
.....................................

.. wtrl_autodoc_function:: gen_documentable_objects

.. _example_gen_documentable_objects:

.. rubric:: Example

.. literalinclude:: ../examples/test_ref_gen_documentable_objects.py
	:language: python

:wtrl_func:`get_tree_of_section`
.....................................

.. wtrl_autodoc_function:: get_tree_of_section

:wtrl_func:`get_tree_of_subsection`
.....................................

.. wtrl_autodoc_function:: get_tree_of_subsection

:wtrl_func:`get_scopes_of_tree`
.....................................

.. wtrl_autodoc_function:: get_scopes_of_tree

:wtrl_func:`to_string_tree`
.....................................

.. wtrl_autodoc_function:: to_string_tree

:wtrl_func:`build_anchor`
.....................................

.. wtrl_autodoc_function:: build_anchor

Diagnostics helpers
----------------------

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem_diagnostics

:wtrl_func:`explain_try_self_for_section`
..........................................

.. wtrl_autodoc_function:: explain_try_self_for_section

:wtrl_func:`explain_try_self_for_subsection`
.............................................

.. wtrl_autodoc_function:: explain_try_self_for_subsection

:wtrl_func:`render_allowed_identifier`
......................................

.. wtrl_autodoc_function:: render_allowed_identifier

:wtrl_func:`render_allowed_identifiers`
.......................................

.. wtrl_autodoc_function:: render_allowed_identifiers

:wtrl_func:`render_base_method_docstring_details`
..................................................

.. wtrl_autodoc_function:: render_base_method_docstring_details

:wtrl_func:`render_base_method_reference_details`
.................................................

.. wtrl_autodoc_function:: render_base_method_reference_details

:wtrl_func:`render_constant_reference_details`
..............................................

.. wtrl_autodoc_function:: render_constant_reference_details

:wtrl_func:`render_deduplicated_identifiers`
............................................

.. wtrl_autodoc_function:: render_deduplicated_identifiers

:wtrl_func:`render_definition_reference_details`
.................................................

.. wtrl_autodoc_function:: render_definition_reference_details

:wtrl_func:`render_exactly_one_identifier_details`
..................................................

.. wtrl_autodoc_function:: render_exactly_one_identifier_details

:wtrl_func:`render_expected_identifier`
........................................

.. wtrl_autodoc_function:: render_expected_identifier

:wtrl_func:`render_expected_snippet`
.....................................

.. wtrl_autodoc_function:: render_expected_snippet

:wtrl_func:`render_identifier_lines`
....................................

.. wtrl_autodoc_function:: render_identifier_lines

:wtrl_func:`render_inherited_definition_details`
.................................................

.. wtrl_autodoc_function:: render_inherited_definition_details

:wtrl_func:`render_listed_object_missing_details`
..................................................

.. wtrl_autodoc_function:: render_listed_object_missing_details

:wtrl_func:`render_missing_entry_details`
.........................................

.. wtrl_autodoc_function:: render_missing_entry_details

:wtrl_func:`render_name_object_consistency_details`
...................................................

.. wtrl_autodoc_function:: render_name_object_consistency_details

:wtrl_func:`render_named_value_reference_details`
..................................................

.. wtrl_autodoc_function:: render_named_value_reference_details

:wtrl_func:`render_normative_section_details`
.............................................

.. wtrl_autodoc_function:: render_normative_section_details

:wtrl_func:`render_normativity_keyword_details`
...............................................

.. wtrl_autodoc_function:: render_normativity_keyword_details

:wtrl_func:`render_overview_missing_member_details`
...................................................

.. wtrl_autodoc_function:: render_overview_missing_member_details

:wtrl_func:`render_overview_requires_section_details`
.....................................................

.. wtrl_autodoc_function:: render_overview_requires_section_details

:wtrl_func:`render_parameter_signature_details`
...............................................

.. wtrl_autodoc_function:: render_parameter_signature_details

:wtrl_func:`render_profile_mismatch_details`
............................................

.. wtrl_autodoc_function:: render_profile_mismatch_details

:wtrl_func:`render_scope_relation_details`
..........................................

.. wtrl_autodoc_function:: render_scope_relation_details

:wtrl_func:`render_see_also_reference_details`
..............................................

.. wtrl_autodoc_function:: render_see_also_reference_details

:wtrl_func:`render_source_snippet`
...................................

.. wtrl_autodoc_function:: render_source_snippet

:wtrl_func:`render_suggestion`
...............................

.. wtrl_autodoc_function:: render_suggestion

:wtrl_func:`render_type_reference_details`
..........................................

.. wtrl_autodoc_function:: render_type_reference_details

:wtrl_func:`render_unique_identifiers`
......................................

.. wtrl_autodoc_function:: render_unique_identifiers

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem_diagnostics

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem

Enum classes
------------

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem_helper

:wtrl_type:`sdv.doc.waterloo.docitem_helper.Scope`
......................................................

.. wtrl_autodoc_class:: sdv.doc.waterloo.docitem_helper.Scope

:wtrl_type:`sdv.doc.waterloo.docitem_helper.Flavour`
......................................................

.. wtrl_autodoc_class:: sdv.doc.waterloo.docitem_helper.Flavour

:wtrl_type:`sdv.doc.waterloo.docitem_helper.Format`
......................................................

.. wtrl_autodoc_class:: sdv.doc.waterloo.docitem_helper.Format

:wtrl_type:`sdv.doc.waterloo.docitem_helper.Status`
......................................................

.. wtrl_autodoc_class:: sdv.doc.waterloo.docitem_helper.Status

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem_helper

Helper classes
--------------

:wtrl_type:`tracer`
.........................

.. wtrl_autodoc_class_full:: sdv.doc.waterloo.docitem_helper.tracer

:wtrl_type:`ConfigTraversal`
.............................

.. wtrl_autodoc_class_full:: sdv.doc.waterloo.docitem_helper.ConfigTraversal

Base classes
------------

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem

:wtrl_type:`docitem_base`
.........................

.. wtrl_autodoc_class_full:: docitem_base

:wtrl_type:`docitem_list_base`
..............................

.. wtrl_autodoc_class_full:: docitem_list_base

:wtrl_type:`docitem_map_base`
.............................

.. wtrl_autodoc_class_full:: docitem_map_base

:wtrl_type:`docitem_docstring_base`
.....................................

.. wtrl_autodoc_class_full:: docitem_docstring_base

:wtrl_type:`docitem_free_text_entry_base`
.........................................

.. wtrl_autodoc_class_full:: docitem_free_text_entry_base

:wtrl_type:`docitem_list_of_symbols_base`
.........................................

.. wtrl_autodoc_class_full:: docitem_list_of_symbols_base

Preamble node classes
---------------------

:wtrl_type:`docitem_profile`
.............................

.. wtrl_autodoc_class_full:: docitem_profile

:wtrl_type:`docitem_normative_sections`
........................................

.. wtrl_autodoc_class_full:: docitem_normative_sections

:wtrl_type:`docitem_status`
........................................

.. wtrl_autodoc_class_full:: docitem_status

:wtrl_type:`docitem_scope`
..........................

.. wtrl_autodoc_class_full:: docitem_scope

:wtrl_type:`docitem_preamble`
.............................

.. wtrl_autodoc_class_full:: docitem_preamble

Contract node classes
---------------------

:wtrl_type:`docitem_constructor`
................................

.. wtrl_autodoc_class_full:: docitem_constructor

:wtrl_type:`docitem_general`
.............................

.. wtrl_autodoc_class_full:: docitem_general

:wtrl_type:`docitem_invariants`
...............................

.. wtrl_autodoc_class_full:: docitem_invariants

:wtrl_type:`docitem_requires`
...............................

.. wtrl_autodoc_class_full:: docitem_requires

:wtrl_type:`docitem_ensures`
...............................

.. wtrl_autodoc_class_full:: docitem_ensures

:wtrl_type:`docitem_traits`
...........................

.. wtrl_autodoc_class_full:: docitem_traits

:wtrl_type:`docitem_contract_module`
....................................

.. wtrl_autodoc_class_full:: docitem_contract_module

:wtrl_type:`docitem_contract_class`
....................................

.. wtrl_autodoc_class_full:: docitem_contract_class

:wtrl_type:`docitem_contract_method`
....................................

.. wtrl_autodoc_class_full:: docitem_contract_method

:wtrl_type:`docitem_class_overview_entry`
...........................................

.. wtrl_autodoc_class_full:: docitem_class_overview_entry

Related objects node classes
----------------------------

:wtrl_type:`docitem_class_overview`
...................................

.. wtrl_autodoc_class_full:: docitem_class_overview

:wtrl_type:`docitem_public_classes`
...................................

.. wtrl_autodoc_class_full:: docitem_public_classes

:wtrl_type:`docitem_public_functions`
.....................................

.. wtrl_autodoc_class_full:: docitem_public_functions

:wtrl_type:`docitem_public_methods`
...................................

.. wtrl_autodoc_class_full:: docitem_public_methods

:wtrl_type:`docitem_public_types_entry`
...........................................

.. wtrl_autodoc_class_full:: docitem_public_types_entry

:wtrl_type:`docitem_public_types`
...................................

.. wtrl_autodoc_class_full:: docitem_public_types

:wtrl_type:`docitem_public_assignables_entry`
..................................................

.. wtrl_autodoc_class_full:: docitem_public_assignables_entry

:wtrl_type:`docitem_public_assignables_base`
............................................

.. wtrl_autodoc_class_full:: docitem_public_assignables_base

:wtrl_type:`docitem_method_overview_entry`
.............................................

.. wtrl_autodoc_class_full:: docitem_method_overview_entry

:wtrl_type:`docitem_method_overview`
.....................................

.. wtrl_autodoc_class_full:: docitem_function_overview

:wtrl_type:`docitem_function_overview_entry`
.............................................

.. wtrl_autodoc_class_full:: docitem_function_overview_entry

:wtrl_type:`docitem_function_overview`
......................................

.. wtrl_autodoc_class_full:: docitem_function_overview

Other sections node classes
---------------------------

:wtrl_type:`docitem_returns`
...................................

.. wtrl_autodoc_class_full:: docitem_returns

:wtrl_type:`docitem_parameters_entry`
.....................................

.. wtrl_autodoc_class_full:: docitem_parameters_entry

:wtrl_type:`docitem_parameters`
.....................................

.. wtrl_autodoc_class_full:: docitem_parameters

:wtrl_type:`docitem_raises_entry`
.....................................

.. wtrl_autodoc_class_full:: docitem_raises_entry

:wtrl_type:`docitem_raises`
.....................................

.. wtrl_autodoc_class_full:: docitem_raises

:wtrl_type:`docitem_derived_from`
....................................

.. wtrl_autodoc_class_full:: docitem_derived_from

:wtrl_type:`docitem_factory_functions`
......................................

.. wtrl_autodoc_class_full:: docitem_factory_functions

:wtrl_type:`docitem_factory`
............................

.. wtrl_autodoc_class_full:: docitem_factory

:wtrl_type:`docitem_definitions_entry`
......................................

.. wtrl_autodoc_class_full:: docitem_definitions_entry

:wtrl_type:`docitem_inherited_defitems`
.......................................

.. wtrl_autodoc_class_full:: docitem_inherited_defitems

:wtrl_type:`docitem_definitions`
.....................................

.. wtrl_autodoc_class_full:: docitem_definitions

:wtrl_type:`docitem_terminology_entry`
......................................

.. wtrl_autodoc_class_full:: docitem_terminology_entry

:wtrl_type:`docitem_terminology`
.....................................

.. wtrl_autodoc_class_full:: docitem_terminology

:wtrl_type:`docitem_description`
.....................................

.. wtrl_autodoc_class_full:: docitem_description

:wtrl_type:`docitem_notes_entry`
......................................

.. wtrl_autodoc_class_full:: docitem_notes_entry

:wtrl_type:`docitem_notes`
.....................................

.. wtrl_autodoc_class_full:: docitem_notes

:wtrl_type:`docitem_see_also`
.....................................

.. wtrl_autodoc_class_full:: docitem_see_also

Top-level node classes
----------------------

:wtrl_type:`docitem_docstring_module`
.....................................

.. wtrl_autodoc_class_full:: docitem_docstring_module

:wtrl_type:`docitem_docstring_class`
.....................................

.. wtrl_autodoc_class_full:: docitem_docstring_class

:wtrl_type:`docitem_docstring_method`
.....................................

.. wtrl_autodoc_class_full:: docitem_docstring_method

:wtrl_type:`docitem_docstring_inherited_method`
...............................................

.. wtrl_autodoc_class_full:: docitem_docstring_inherited_method

Factories
---------

:wtrl_func:`make_docitem_tree`
...........................................

.. wtrl_autodoc_function:: make_docitem_tree
.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem

Module :wtrl_mod:`docitem_sphinx`
==================================

.. wtrl_autodoc_module:: docitem_sphinx

Functions
---------

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem_sphinx

:wtrl_func:`build_sphinx_nodes`
...................................

.. wtrl_autodoc_function:: build_sphinx_nodes

:wtrl_func:`build_sphinx_nodes_full`
....................................

.. wtrl_autodoc_function:: build_sphinx_nodes_full

:wtrl_func:`resolve_qualified_name`
...................................

.. wtrl_autodoc_function:: resolve_qualified_name

Directives for docstring rendering
----------------------------------

:wtrl_func:`wtrl_build_autodoc_module_nodes`
............................................

.. wtrl_autodoc_function:: wtrl_build_autodoc_module_nodes

:wtrl_func:`wtrl_build_autodoc_function_nodes`
..............................................

.. wtrl_autodoc_function:: wtrl_build_autodoc_function_nodes

:wtrl_func:`wtrl_build_autodoc_class_full_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_autodoc_class_full_nodes

:wtrl_func:`wtrl_build_autodoc_class_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_autodoc_class_nodes

Directives for setting default module and class
-----------------------------------------------

:wtrl_func:`wtrl_build_push_current_module_nodes`
.................................................

.. wtrl_autodoc_function:: wtrl_build_push_current_module_nodes

:wtrl_func:`wtrl_build_push_current_class_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_push_current_class_nodes

:wtrl_func:`wtrl_build_push_current_scope_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_push_current_scope_nodes

:wtrl_func:`wtrl_build_pop_current_module_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_pop_current_module_nodes

:wtrl_func:`wtrl_build_pop_current_class_nodes`
...............................................

.. wtrl_autodoc_function:: wtrl_build_pop_current_class_nodes

:wtrl_func:`wtrl_build_pop_current_scope_nodes`
...............................................

.. wtrl_autodoc_function:: wtrl_build_pop_current_scope_nodes

Directives for expanding callable signatures
--------------------------------------------

:wtrl_func:`wtrl_build_method_signature_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_method_signature_nodes

:wtrl_func:`wtrl_build_function_signature_nodes`
................................................

.. wtrl_autodoc_function:: wtrl_build_function_signature_nodes

:wtrl_func:`wtrl_build_method_signature_block_nodes`
....................................................

.. wtrl_autodoc_function:: wtrl_build_method_signature_block_nodes

:wtrl_func:`wtrl_build_function_signature_block_nodes`
......................................................

.. wtrl_autodoc_function:: wtrl_build_function_signature_block_nodes

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem_sphinx

Module :wtrl_mod:`docitem_convert`
===================================

.. wtrl_autodoc_module:: docitem_convert

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem_convert

Converter functions
-------------------

:wtrl_func:`to_node_legend_json`
......................................

.. wtrl_autodoc_function:: to_node_legend_json

:wtrl_func:`to_node_docstring_tree_json`
.............................................

.. wtrl_autodoc_function:: to_node_docstring_tree_json

:wtrl_func:`to_node_signature_json`
......................................

.. wtrl_autodoc_function:: to_node_signature_json

:wtrl_func:`build_node_json`
...................................

.. wtrl_autodoc_function:: build_node_json

:wtrl_func:`to_string_md`
...........................

.. wtrl_autodoc_function:: to_string_md

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem_convert

.. wtrl_pop_current_module:: sdv.doc.waterloo

Module :wtrl_mod:`docitem_genutil`
==================================

.. wtrl_push_current_module:: sdv.doc.waterloo.docitem_genutil

.. wtrl_autodoc_module:: sdv.doc.waterloo.docitem_genutil

:wtrl_func:`parse_source_fragment`
-----------------------------------

.. wtrl_autodoc_function:: parse_source_fragment

:wtrl_func:`infer_docstring_profile`
-----------------------------------------------

.. wtrl_autodoc_function:: infer_docstring_profile

:wtrl_func:`generate_minimal_docstring`
--------------------------------------------------

.. wtrl_autodoc_function:: generate_minimal_docstring

:wtrl_func:`generate_full_docstring`
-----------------------------------------

.. wtrl_autodoc_function:: generate_full_docstring

:wtrl_func:`generate_minimal_docstring_from_node`
----------------------------------------------------

.. wtrl_autodoc_function:: generate_minimal_docstring_from_node

:wtrl_func:`generate_full_docstring_from_node`
---------------------------------------------------

.. wtrl_autodoc_function:: generate_full_docstring_from_node

.. wtrl_pop_current_module:: sdv.doc.waterloo.docitem_genutil

Pygments Lexer
==============

.. wtrl_push_current_module:: python_waterloo_lexer

.. wtrl_autodoc_module:: python_waterloo_lexer

:wtrl_type:`PythonWaterlooLexer`
--------------------------------

.. wtrl_autodoc_class_full:: PythonWaterlooLexer

.. wtrl_pop_current_module:: python_waterloo_lexer

Output layer HTML5
==================

.. wtrl_push_current_module:: sdv.doc.waterloo.waterlint_render_html5

.. wtrl_autodoc_module:: sdv.doc.waterloo.waterlint_render_html5

.. wtrl_autodoc_function:: render_html5

.. wtrl_pop_current_module:: sdv.doc.waterloo.waterlint_render_html5


.. wtrl_pop_current_scope:: core
