# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -v
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
ROOT          := $(abspath ../src/sdv/doc/waterloo)
STATICDIR     := $(abspath $(SOURCEDIR)/_static)

do_mypy:
	# @../do_mypy.sh --echo --out-dir $(STATICDIR) --out-hash type_checking.hash --out-report type_checking_report.txt --out-ignore type_checking_exceptions.txt $(ROOT)/docitem*.py
	@../do_mypy_simple.sh $(ROOT)/docitem*.py > $(STATICDIR)/type_checking_report.txt

# Run type checking before building HTML.
html: do_mypy
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
