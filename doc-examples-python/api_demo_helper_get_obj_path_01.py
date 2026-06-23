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
print("class:", h.get_obj_path(X))
print("instance:", h.get_obj_path(x))
print("classmethod:", h.get_obj_path(X.m_cls))
print("staticmethod:", h.get_obj_path(X.m_stat))
print("bound method:", h.get_obj_path(x.m))
print("module function:", h.get_obj_path(f))
print("nested class:", h.get_obj_path(X.Y))
print("nested class via instance:", h.get_obj_path(x.Y))

print("nested instance via instance:", h.get_obj_path(x.y))
print("nested instance via class:", h.get_obj_path(X.y))
