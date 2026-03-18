Miscellaneous
=============

Inspecting JSON documents with :wtrl_cmd:`jq`
---------------------------------------------

In this section, we present a few examples of using the JSON
command-line processor :wtrl_cmd:`jq` with Waterloo JSON files.
You can try these examples with the accompanying file
:wtrl_var:`PATH` = :wtrl_file:`sdv/doc/waterloo/doc-json/docitem.wtrl.core.rfc-2119.json`,
which is shipped with this package.


* Extract a JSON node, in this case the list of documented modules:

	.. code-block:: bash
	
		jq .__WTRL_TOC_MODULES__ ${PATH}

* Extract a selected entry of a JSON object:

	.. code-block:: bash

		jq '.__WTRL_TOC_MODULES__["sdv.doc.waterloo.docitem"]' ${PATH}

* Extract the values (without keys) as JSON strings.
  When applied to an array, :wtrl_op:`[]` emits each element.
  When applied to an object, it emits each value.

	.. code-block:: bash
 
		jq '.__WTRL_TOC_MODULES__[]'	${PATH}
 
* Extract the values (without keys) as raw strings:

	.. code-block:: bash

		jq -r '.__WTRL_TOC_MODULES__[]'	${PATH}

* Extract the qualified identifiers of all classes (look for :wtrl_label:`profile` :wtrl_value:`class`).
  The filter :wtrl_func:`to_entries[]` converts the object into key-value pairs,
  which can then be accessed via :wtrl_var:`.key` and :wtrl_var:`.value`.
  The filter :wtrl_func:`select` passes through only those entries
  that satisfy the specified condition.


	.. code-block:: bash

		jq -r '.__WTRL_OBJECTS__	| to_entries[]
						| select(.value.doc.Preamble.profile == "class")
						| .key'	${PATH}

* Find the keys of all functions that are marked with the trait :wtrl_value:`generator`:

	.. code-block:: bash

		jq -r '.__WTRL_OBJECTS__	| to_entries[]
						| select(.value.doc.Preamble.profile == "function")
						| select(.value.traits | any(. == "generator")?)
						| .key' ${PATH}


* Extract examples assigned to for a given object. The code snippet below
  extracts the python example in :wtrl_file:`doc-json/tde4_with_examples.wtrl.core.rfc-2119.json`
  for the documented function :wtrl_func:`tde4.getFirstCamera`.

	.. code-block:: bash

		jq -r '. as $root | "__WTRL_EXAMPLES__" , (
        		$root.__WTRL_EXAMPLES__
        		| to_entries[]
        		| select((.value.referenced_by // []) | index("tde4.getFirstCamera"))
        		| "---- " + .key + " ----\n" + (.value.code // "")
			) ' doc-json/tde4_with_examples.wtrl.core.rfc-2119.json


The examples above illustrate only a small subset of what can be achieved
with :wtrl_cmd:`jq`. For a comprehensive reference, consult the official
jq documentation at `jqlang.github.io/jq <https://jqlang.github.io>`_.

