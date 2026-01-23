Examples
########

This section covers cases which are not contained in the referenc documentation,
such as

* classes within classes
* constants in classes
* maybe types in classes

Class within class
==================

.. wtrl_push_current_module:: test_docitem_class_class

.. literalinclude:: ../examples/test_docitem_class_class.py
	:language: python

.. wtrl_autodoc_class_full:: X
.. wtrl_autodoc_class_full:: X.Y

.. wtrl_pop_current_module:: test_docitem_class_class
