#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

class Z:
	pass

class X:
	def __init__(self):
		self._p = 3

	@classmethod
	def m_cls(cls) -> None:
		pass
	@staticmethod
	def m_stat(cls) -> None:
		pass
	def m(self) -> None:
		pass
	class Y:
		pass
	y = Y()
	z = Z()

	@property
	def p(self):
		return self._p
	@p.setter
	def p(self,val):
		self._p = val
	

def f() -> None:
	pass

x = X()
print(h.get_obj_fully_qualified_name(X))
print(h.get_obj_fully_qualified_name(x))
print(h.get_obj_fully_qualified_name(X.m_cls))
print(h.get_obj_fully_qualified_name(X.m_stat))
print(h.get_obj_fully_qualified_name(x.m))
print(h.get_obj_fully_qualified_name(f))
print(h.get_obj_fully_qualified_name(X.Y))
print(h.get_obj_fully_qualified_name(x.Y))

print(h.get_obj_fully_qualified_name(x.y))
print(h.get_obj_fully_qualified_name(X.y))

# See limitations. Nested instances should not be passed.
print(h.get_obj_fully_qualified_name(X.z))
print(h.get_obj_fully_qualified_name(x.z))

print(h.get_obj_fully_qualified_name(x.p))
print(h.get_obj_fully_qualified_name(X.p.setter))

