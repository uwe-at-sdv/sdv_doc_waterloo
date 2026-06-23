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

x = X()
print("class:", h.get_obj_name(X))
print("instance:", h.get_obj_name(x))
print("classmethod:", h.get_obj_name(X.m_cls))
print("staticmethod:", h.get_obj_name(X.m_stat))
print("bound method:", h.get_obj_name(x.m))
print("module function:", h.get_obj_name(f))
print("nested class:", h.get_obj_name(X.Y))
print("nested class via instance:", h.get_obj_name(x.Y))

# These two are a bit surprising, but seem to be irrelevant for the project.
print("nested instance via instance:", h.get_obj_name(x.y))
print("nested instance via class:", h.get_obj_name(X.y))

# Same here. See section Notes.Limitations.
print("fq name for nested instance via instance:", h.get_obj_fully_qualified_name(x.y))
print("fq name for nested instance via class:", h.get_obj_fully_qualified_name(X.y))

print("runtime class name:", x.y.__class__.__name__)
print("declared class name:", X.Y.__name__)
