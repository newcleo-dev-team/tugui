# Makefile for Sphinx documentation

# These variables can be changed directly from the command line
# and/or through the environment variables.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
# These variables can be changed from the command line only.
SOURCEDIR     = .
BUILDDIR      = _build

# "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)