#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

class X:
	class Y:
		class Z:
			@classmethod
			def test(cls) -> None:
				print(h.get_obj_fully_qualified_name(cls.test))

X.Y.Z.test()
# Result: __main__.X.Y.Z.test
