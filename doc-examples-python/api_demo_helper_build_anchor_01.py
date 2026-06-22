#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

# A selfreferential test...
# Should produce "wtrl-func-3:sdv-3:doc-8:waterloo-14:docitem_helper-12:build_anchor"
def test_build_anchor() -> None:
	print(h.build_anchor(h.build_anchor))

test_build_anchor()
