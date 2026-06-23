#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

print("section:", h.explain_try_self_for_section("Contract", "class"))
print("subsection:", h.explain_try_self_for_subsection("Contract.requires", "class"))
