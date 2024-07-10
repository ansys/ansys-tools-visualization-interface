# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W --color
SPHINXBUILD   = sphinx-build
APIDIR        = api
SOURCEDIR     = source
BUILDDIR      = _build

IS_VTK_INSTALLED := $(pip show vtk)
ifneq ($(IS_VTK_INSTALLED),)
	@echo "VTK is installed. Uninstalling vtk and installing vtk-osmesa"
	@pip uninstall -y vtk
	@pip install --extra-index-url https://wheels.vtk.org vtk-osmesa==9.3.0
endif

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Customized clean due to examples gallery
clean:
	rm -rf $(BUILDDIR)/*
	find . -type d -name $(APIDIR) -exec rm -rf {} +

# Create PDF
pdf:
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true

# Build HTML files and generate examples as .py files
html:
	pip uninstall vtk -y
	pip install --extra-index-url https://wheels.vtk.org vtk-osmesa
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
