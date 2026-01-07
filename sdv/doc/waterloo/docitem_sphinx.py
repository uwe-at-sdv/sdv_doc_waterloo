from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Tuple, Type, TypeAlias, TypeGuard, Union
import inspect
from docutils import nodes
from sdv_doc_docitem import (
	docitem_docstring_module,
	docitem_docstring_class,
	docitem_docstring_method,
	docitem_preamble,
	docitem_contract_module,
	docitem_contract_class,
	docitem_contract_method,
	docitem_derived_from,
	docitem_factory,
	docitem_description,
	docitem_public_methods,
	docitem_public_functions,
	docitem_public_types,
	docitem_public_constants,
	docitem_parameters,
	docitem_returns,
	docitem_raises,
	docitem_usage,
	parse_indent_docstring,
	validate_docstring,
	validate_class_method_coverage,
	)

__version__ = "0.1.0"

def _render_bullet(items: List[str]) -> nodes.bullet_list:
	node_list: nodes.bullet_list = nodes.bullet_list()
	for it in items:
		node_item: nodes.list_item = nodes.list_item()
		node_para: nodes.paragraph = nodes.paragraph()
		node_para += nodes.Text(it)
		node_item += node_para
		node_list += node_item
	return node_list

class context:
	def __init__(self,parse_inline : Callable[...,List[nodes.Node]],lineno: int) -> None:
		self._location_stack : List[str] = ["top"]
		self.parse = parse_inline
		self.i_line = lineno
		self.add_role_func = lambda t:t
		self.add_role_method = lambda t:t
		self.add_role_var = lambda t:t
		self.add_role_type = lambda t:t
		self.add_role_label = lambda t:t
		self.build_prolog_public_methods = lambda ctx: []
		self.build_prolog_method_block = lambda ctx, parent, cls, meth: []
		
	def set_add_role_func(self,c):
		self.add_role_func = c
	def set_add_role_method(self,c):
		self.add_role_method = c
	def set_add_role_var(self,c):
		self.add_role_var = c
	def set_add_role_type(self,c):
		self.add_role_type = c
	def set_add_role_label(self,c):
		self.add_role_label = c
	def set_build_prolog_public_methods(self,c):
		self.build_prolog_public_methods = c
	def set_build_prolog_method_block(self,c):
		self.build_prolog_method_block = c
	def push_location(self,loc : str) -> None:
		self._location_stack.append(loc)
	def pop_location(self) -> None:
		del self._location_stack[-1]
	def to_str_location(self) -> str:
		return "->".join(self._location_stack)

def build_sphinx_nodes(ctx : context,objname,doc: docitem_docstring_class) -> List[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| convert a parsed :cdml_type:`docitem_docstring_class` or :cdml_type:`docitem_docstring_method` into a list of docutils nodes.
		|Must| render section/key/value content into a two-column table with section labels on the left and content on the right.
		|Must| apply role-formatters provided by :cdml_type:`context` (labels, types, vars, funcs, methods).
Parameters:
	ctx:
		Rendering context providing inline parser and role-formatters.
	objname:
		Name of the documented object (class or method) used in headings.
	doc:
		Parsed docstring tree (:cdml_type:`docitem_docstring_class` or :cdml_type:`docitem_docstring_method`).
Returns:
	List of :cdml_type:`docutils.nodes.Node` representing the rendered documentation table.
Raises:
	RuntimeError:
		|May| raise if unexpected section structure is encountered.
	"""
	node_root: List[nodes.Node] = []

# Build table
	node_table = nodes.table(classes=["sdv-meta"])
	node_tgroup = nodes.tgroup(cols=2)
	node_tgroup += nodes.colspec(colwidth=20)
	node_tgroup += nodes.colspec(colwidth=80)
	node_tbody = nodes.tbody()
	node_tgroup += node_tbody

	profile = doc.items()["Preamble"].items()["profile"].items()[0]
	node_thead = nodes.thead(classes=["sdv-meta-head-" + profile])
	node_hrow = nodes.row()
	node1_entry = nodes.entry()
	node1_entry += ctx.parse(node1_entry,0,ctx.add_role_label(profile.capitalize()))
	node2_entry = nodes.entry()
	node2_entry += nodes.paragraph(text=objname)
	node_hrow += node1_entry
	node_hrow += node2_entry
	node_thead += node_hrow
	node_tgroup += node_thead

	node_table += node_tgroup

	for label,item_section in doc.items().items():
# New table row per section
		node_row = nodes.row()

		node_entry = nodes.entry()
		node_paragraph = nodes.paragraph()
		node_paragraph.extend(ctx.parse(node_paragraph,0,ctx.add_role_label(item_section.label())))
		node_entry += node_paragraph
		node_row += node_entry

		node_entry = nodes.entry()
		if label in ("Preamble","Contract"):
			ctx.push_location(label)
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				if label1 == "profile":
					continue
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_label(item_subsection.label())))
				if label1 in ("api","normative_sections"):
					node2_bullet_list = nodes.bullet_list()
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()
					node2_paragraph.extend(ctx.parse(node2_paragraph,0,", ".join([ctx.add_role_label(content) for content in item_subsection.items()])))
					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				else:

					node2_bullet_list = nodes.bullet_list()
					for content in item_subsection.items():
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item

				node_list_item += node1_paragraph
				node_list_item += node2_bullet_list
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
			ctx.pop_location()
		elif label in ("Factory"):
			ctx.push_location(label)
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_func(label1)))

				node2_bullet_list = nodes.bullet_list()
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
			ctx.pop_location()
		elif label in ("Public_methods"):
			ctx.push_location(label)
			node_paragraph = nodes.paragraph()
			node_paragraph.extend(ctx.parse(node_paragraph,0,"This section is normative. The list below defines the set of public methods."))
			node_entry += node_paragraph

			node_bullet_list = nodes.bullet_list()
			for label1,item_subsection in item_section.items().items():
				node_list_item = nodes.list_item()
				node1_paragraph = nodes.paragraph()
				node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_method(label1)))

				node2_bullet_list = nodes.bullet_list()
				for content in item_subsection.items():
					node2_list_item = nodes.list_item()
					node2_paragraph = nodes.paragraph()

					node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

					node2_list_item += node2_paragraph
					node2_bullet_list += node2_list_item
				node1_paragraph += node2_bullet_list

				node_list_item += node1_paragraph
				node_bullet_list += node_list_item

			node_entry += node_bullet_list
			ctx.pop_location()
		elif label in ("Parameters"):
			ctx.push_location(label)
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			if len(item_section.items()) == 0:
				node_entry.extend(ctx.parse(node1_paragraph,0,"|empty|"))
			else:
				node_bullet_list = nodes.bullet_list()
				for label1,item_subsection in item_section.items().items():
					node_list_item = nodes.list_item()
					node1_paragraph = nodes.paragraph()
					node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_var(label1)))

					node2_bullet_list = nodes.bullet_list()
					for content in item_subsection.items():
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item
					node1_paragraph += node2_bullet_list

					node_list_item += node1_paragraph
					node_bullet_list += node_list_item

				node_entry += node_bullet_list
			ctx.pop_location()
		elif label in ("Raises"):
			ctx.push_location(label)
#			node_paragraph = nodes.paragraph()
#			node_entry += node_paragraph
			if len(item_section.items()) == 0:
				node_entry.extend(ctx.parse(node1_paragraph,0,"|empty|"))
			else:
				node_bullet_list = nodes.bullet_list()
				for label1,item_subsection in item_section.items().items():
					node_list_item = nodes.list_item()
					node1_paragraph = nodes.paragraph()
					node1_paragraph.extend(ctx.parse(node1_paragraph,0,ctx.add_role_type(label1)))

					node2_bullet_list = nodes.bullet_list()
					for content in item_subsection.items():
						node2_list_item = nodes.list_item()
						node2_paragraph = nodes.paragraph()

						node2_paragraph.extend(ctx.parse(node2_paragraph,0,content))

						node2_list_item += node2_paragraph
						node2_bullet_list += node2_list_item
					node1_paragraph += node2_bullet_list

					node_list_item += node1_paragraph
					node_bullet_list += node_list_item

				node_entry += node_bullet_list
			ctx.pop_location()
		elif label in ("Description","Usage"):
			ctx.push_location(label)
			node1_paragraph = nodes.paragraph()
			node1_paragraph.extend(ctx.parse(node1_paragraph,0," ".join([content for content in item_section.items()])))
			node_entry += node1_paragraph
			ctx.pop_location()
		elif label in ("Returns"):
			ctx.push_location(label)
			node1_paragraph = nodes.paragraph()
			node1_paragraph.extend(ctx.parse(node1_paragraph,0," ".join([content for content in item_section.items()])))
			node_entry += node1_paragraph
			ctx.pop_location()
		elif label in ("Derived_from"):
			ctx.push_location(label)
			node1_paragraph = nodes.paragraph()
			node1_paragraph.extend(ctx.parse(node1_paragraph,0,", ".join([ctx.add_role_type(content) for content in item_section.items()])))
			node_entry += node1_paragraph
			ctx.pop_location()
		else:
			ctx.push_location(label)
			node_paragraph = nodes.paragraph(text="TBD")
			node_entry += node_paragraph
			ctx.pop_location()

		node_row += node_entry
		node_tbody += node_row

	return [node_table]

def build_sphinx_nodes_full(ctx : context,
				class_obj,
				) -> List[nodes.Node]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstring and methods of the class object.
		|Must| create a list of sphinx nodes, with elements as specified in the following and have the order as indicated:
		The list |must| contain nodes representing the class' docstring.
		The list |must| contain nodes produced by :cdml_func:`ctx.build_prolog_public_methods`.
		For each public method as indicated by the class' normative docstring:
		1. The list |must| contain nodes produced by :cdml_func:`ctx.build_prolog_method_block`.
		2. The list |must| contain nodes representing the class' public method's docstring.
Parameters:
	ctx:
		The context
	class_obj:
		The class object to generate a sphinx documentation node list from.
Returns:
	A list of sphinx nodes representing the class and public member documentation.
Raises:
	RuntimeError:
		|Must| raise if something goes wrong parsing a docstring.
	Any:
		|Must| forward exceptions from Sphinx
	"""
	nodes_out: List[nodes.Node] = []

# Validate class docstring and Public_methods coverage
	if not isinstance(class_obj.__doc__, str):
		raise RuntimeError(f"class {class_obj} has no docstring.")
	validate_class_method_coverage(class_obj)
	tree_cls = parse_indent_docstring(class_obj.__doc__)
	di_cls = docitem_docstring_class()
	di_cls.parse(tree_cls)
	validate_docstring(class_obj,di_cls)

# Render class block
	nodes_out.extend(build_sphinx_nodes(ctx, class_obj.__name__, di_cls))

# Render public methods
	if "Public_methods" in di_cls.items():
		nodes_out.extend(ctx.build_prolog_public_methods(ctx))
		pm_node = di_cls._items["Public_methods"]
		assert isinstance(pm_node, docitem_public_methods)
		for meth_name in pm_node.items().keys():
			if not hasattr(class_obj, meth_name):
				continue
			meth_obj = getattr(class_obj, meth_name)
			if inspect.ismethod(meth_obj):
				func_obj = meth_obj.__func__
			elif inspect.isfunction(meth_obj):
				func_obj = meth_obj
			elif isinstance(meth_obj, staticmethod):
				func_obj = meth_obj.__func__
			elif isinstance(meth_obj, classmethod):
				func_obj = meth_obj.__func__
			else:
				continue
			if not isinstance(func_obj.__doc__, str):
				continue
			tree_m = parse_indent_docstring(func_obj.__doc__)
			di_m = docitem_docstring_method()
			di_m.parse(tree_m)
			validate_docstring(func_obj,di_m)
			ctx.push_location(meth_name)
			nodes_out.extend(ctx.build_prolog_method_block(ctx, None, class_obj, func_obj))
			nodes_out.extend(build_sphinx_nodes(ctx, meth_name, di_m))
			ctx.pop_location()

	return nodes_out

if __name__ == "__main__":
# Self test
	assert isinstance(build_sphinx_nodes_full.__doc__,str)
	tree = parse_indent_docstring(build_sphinx_nodes_full.__doc__)
	print(tree)
	node = docitem_docstring_method()
	node.parse(tree)
	validate_docstring(build_sphinx_nodes_full,node)
	assert isinstance(build_sphinx_nodes.__doc__,str)
	tree2 = parse_indent_docstring(build_sphinx_nodes.__doc__)
	print(tree2)
	node2 = docitem_docstring_method()
	node2.parse(tree2)
	validate_docstring(build_sphinx_nodes,node2)
