Test: Scopes
================================================================

This chapter demonstrates the effect of subsection :wtrl_label:`Preamble.scope`
in combination with the scope state stack. The goal is to render a Sphinx
document for a given target audience, according to the rules defined in
:ref:`chapter_scopes_and_visibility`.

To this end, the objects of module :wtrl_mod:`test_scope_mix` are rendered
once for each target scope, each within its own section of this chapter.
The scope is set at the beginning of each section using the directive
``.. wtrl_push_current_scope::``.

The active scope determines which objects are rendered at all, and which
references in the resulting HTML artifact are clickable. In this way,
a consistent subgraph of the complete set of docstrings of the module
is obtained.

The three sections below illustrate how the visible subset of objects
changes with increasing scope.

.. _scope_public:

Scope: Public
----------------------------------------------------------------

.. wtrl_push_current_scope:: public

.. wtrl_autodoc_module:: test_scope_mix

.. wtrl_push_current_module:: test_scope_mix

.. wtrl_autodoc_function:: f_public
.. wtrl_autodoc_function:: f_extension
.. wtrl_autodoc_function:: f_core

.. wtrl_autodoc_class_full:: X_public
.. wtrl_autodoc_class_full:: X_extension
.. wtrl_autodoc_class_full:: X_core

.. wtrl_pop_current_module:: test_scope_mix

.. wtrl_pop_current_scope:: public

.. _scope_extension:

Scope: Extension
----------------------------------------------------------------

.. wtrl_push_current_scope:: extension

.. wtrl_autodoc_module:: test_scope_mix

.. wtrl_push_current_module:: test_scope_mix

.. wtrl_autodoc_function:: f_public
.. wtrl_autodoc_function:: f_extension
.. wtrl_autodoc_function:: f_core

.. wtrl_autodoc_class_full:: X_public
.. wtrl_autodoc_class_full:: X_extension
.. wtrl_autodoc_class_full:: X_core

.. wtrl_pop_current_module:: test_scope_mix

.. wtrl_pop_current_scope:: extension

.. _scope_core:

Scope: Core
----------------------------------------------------------------

.. wtrl_push_current_scope:: core

.. wtrl_autodoc_module:: test_scope_mix

.. wtrl_push_current_module:: test_scope_mix

.. wtrl_autodoc_function:: f_public
.. wtrl_autodoc_function:: f_extension
.. wtrl_autodoc_function:: f_core

.. wtrl_autodoc_class_full:: X_public
.. wtrl_autodoc_class_full:: X_extension
.. wtrl_autodoc_class_full:: X_core

.. wtrl_pop_current_module:: test_scope_mix

.. wtrl_pop_current_scope:: core
