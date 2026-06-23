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
	def p(self, val):
		self._p = val


def f() -> None:
	pass

x = X()
print("class:", h.get_obj_fully_qualified_name(X))
print("instance:", h.get_obj_fully_qualified_name(x))
print("classmethod:", h.get_obj_fully_qualified_name(X.m_cls))
print("staticmethod:", h.get_obj_fully_qualified_name(X.m_stat))
print("bound method:", h.get_obj_fully_qualified_name(x.m))
print("module function:", h.get_obj_fully_qualified_name(f))
print("nested class:", h.get_obj_fully_qualified_name(X.Y))
print("nested class via instance:", h.get_obj_fully_qualified_name(x.Y))

print("nested instance via instance:", h.get_obj_fully_qualified_name(x.y))
print("nested instance via class:", h.get_obj_fully_qualified_name(X.y))

# See limitations: nested instances should not be passed.
print("nested class attr via class:", h.get_obj_fully_qualified_name(X.z))
print("nested class attr via instance:", h.get_obj_fully_qualified_name(x.z))

print("property instance:", h.get_obj_fully_qualified_name(x.p))
print("property setter:", h.get_obj_fully_qualified_name(X.p.setter))
