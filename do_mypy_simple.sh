#!/usr/bin/bash

PATH_MYPY_INI=$(realpath $(dirname $0)/mypy.ini)

mypy --config-file ${PATH_MYPY_INI} -p sdv.doc.waterloo
