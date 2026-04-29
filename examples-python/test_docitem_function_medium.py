#-----8<-----1
from typing import List, TypeAlias, Union

class tracer:
	pass

DocstringSubtree: TypeAlias = Union[str, List["DocstringSubtree"]]

class docitem_base:
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Description:
			This docstring is located in the base class of all docitem
			node classes. The method is not implemented here and will
			raise an exception if it is invoked without a corresponding
			implementation in a derived class.
		Contract:
			general:
				|Must| parse a docstring subtree and create the related child items.
			requires:
				:wtrl_var:`subtree` |must| be a formally correct docstring subtree\
				from a Waterloo docstring; otherwise parsing will fail.
		Parameters:
			tr:
				The tracer for collecting diagnostics.
			subtree:
				A subtree of the tree matching this instance.
		Returns:
			|None|
		Raises:
			NotImplementedError:
				|Must| raise if not implemented in the derived class.
			RuntimeError:
				|Must| raise if the subtree does not match the expected format.
		"""
		raise NotImplementedError
#----->8-----1

#-----8<-----2

class docitem_list_of_symbols_base(docitem_base):
	def _parse(self, tr: tracer, refs: DocstringSubtree, pattern = str):
# Some implementation here...
#		...
		pass

class docitem_traits(docitem_list_of_symbols_base):
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
		Contract:
			general:
				|Must| set rules-on-fail in the tracer and delegate\
				to method :wtrl_func:`._parse` in class\
				:wtrl_type:`docitem_list_of_symbols_base`.
			base:
				test_docitem_function_medium.docitem_base.parse
		"""
# Some implementation here...
#		...
		pass
#----->8-----2
