#!/usr/bin/env python3

from __future__ import annotations
from typing import TypeAlias
import sdv.doc.waterloo.docitem_helper as h

class X:
	@classmethod
	def m_cls(cls) -> None:
		pass
	@staticmethod
	def m_stat(cls) -> None:
		pass
	def m(self) -> None:
		pass
	v: int = 42
	t: TypeAlias = int | float

def f() -> None:
	pass

functions_to_test = [
	h.is_obj_module,
	h.is_obj_class,
	h.is_obj_function,
	h.is_obj_method_like,
	h.is_obj_named_value,
	h.is_obj_documentable
	]

objects_to_test = [ h,X,f,X.m,X.m_cls,X.m_stat,X.v,X.t ]

if __name__ == "__main__":
	print("                     h        X        f        X.m      X.m_cls  X.m_stat X.v      X.t")
	for func in functions_to_test:
		print(func.__name__ + ":" + " " * (20 - len(func.__name__)),end='')
		for obj in objects_to_test:
			print("True " if func(obj) else "False",end='    ')
		print()

#                      h        X        f        X.m      X.m_cls  X.m_stat X.v      X.t
# is_obj_module:       True     False    False    False    False    False    False    False    
# is_obj_class:        False    True     False    False    False    False    False    False    
# is_obj_function:     False    False    True     True     True     True     False    False    
# is_obj_method_like:  False    False    False    True     True     True     False    False    
# is_obj_named_value:  False    False    False    False    False    False    True     True     
# is_obj_documentable: True     True     True     True     True     True     False    False    
