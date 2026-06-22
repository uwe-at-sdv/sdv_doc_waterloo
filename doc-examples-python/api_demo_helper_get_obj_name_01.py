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
print(h.get_obj_name(X))
print(h.get_obj_name(x))
print(h.get_obj_name(X.m_cls))
print(h.get_obj_name(X.m_stat))
print(h.get_obj_name(x.m))
print(h.get_obj_name(f))
print(h.get_obj_name(X.Y))
print(h.get_obj_name(x.Y))

# These two are a bit surprising, but seem to be
# irrelevant for the project.
print(h.get_obj_name(x.y))
print(h.get_obj_name(X.y))

# Same here. See section Notes.Limitations.
print(h.get_obj_fully_qualified_name(x.y))
print(h.get_obj_fully_qualified_name(X.y))

