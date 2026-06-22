#!/usr/bin/env python3

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
	class Y:
		pass
	y = Y()

def f() -> None:
	pass

# All ten results are the same, as it should be.
x = X()
print(h.get_obj_path(X))
print(h.get_obj_path(x))
print(h.get_obj_path(X.m_cls))
print(h.get_obj_path(X.m_stat))
print(h.get_obj_path(x.m))
print(h.get_obj_path(f))
print(h.get_obj_path(X.Y))
print(h.get_obj_path(x.Y))

print(h.get_obj_path(x.y))
print(h.get_obj_path(X.y))

