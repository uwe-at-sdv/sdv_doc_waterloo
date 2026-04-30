#!/usr/bin/bash

mypy --config-file mypy.ini -m sdv.doc.waterloo.waterlint
mypy --config-file mypy.ini -m sdv.doc.waterloo.waterlint_render_html5
