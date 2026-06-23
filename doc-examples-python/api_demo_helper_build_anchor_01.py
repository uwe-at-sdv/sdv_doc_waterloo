#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

# A self-referential test.
# It should produce the anchor for this function itself.
def test_build_anchor() -> None:
	print("build_anchor:", h.build_anchor(h.build_anchor))

test_build_anchor()
