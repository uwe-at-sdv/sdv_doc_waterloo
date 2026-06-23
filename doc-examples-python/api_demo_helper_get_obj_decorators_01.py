#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

class X:
	@classmethod
	def m_cls(cls) -> None:
		pass
	@staticmethod
	def m_stat(cls) -> None:
		pass

print("classmethod decorators:", h.get_obj_decorators(X.m_cls))
print("staticmethod decorators:", h.get_obj_decorators(X.m_stat))
