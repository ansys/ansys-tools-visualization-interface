`0.5.0 <https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.5.0>`_ - 2024-11-04

No significant changes.


`0.5.0 <https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.5.0>`_ - 2024-10-31


### Added

- feat: add changelog and vulnerability check `#58 <https://github.com/ansys/ansys-tools-visualization-interface/pull/58>`_
- feat: add dynamic scraper on docs `#86 <https://github.com/ansys/ansys-tools-visualization-interface/pull/86>`_
- feat: Add interactive documentation `#92 <https://github.com/ansys/ansys-tools-visualization-interface/pull/92>`_
- feat: Remove buttons on screenshot and static docs `#94 <https://github.com/ansys/ansys-tools-visualization-interface/pull/94>`_
- feat: Add plane clip slider `#95 <https://github.com/ansys/ansys-tools-visualization-interface/pull/95>`_
- feat: Add screenshot button `#96 <https://github.com/ansys/ansys-tools-visualization-interface/pull/96>`_
- feat!: Add hover capabilities `#98 <https://github.com/ansys/ansys-tools-visualization-interface/pull/98>`_
- feat: Add show/hide button for buttons `#99 <https://github.com/ansys/ansys-tools-visualization-interface/pull/99>`_
- feat: allow for multi_colors argument in plotting options `#118 <https://github.com/ansys/ansys-tools-visualization-interface/pull/118>`_
- fix: preserve access order using dictionary and adapt show to already existing objects `#175 <https://github.com/ansys/ansys-tools-visualization-interface/pull/175>`_
- feat: Add StructuredGrid support `#180 <https://github.com/ansys/ansys-tools-visualization-interface/pull/180>`_


### Changed

- [pre-commit.ci] pre-commit autoupdate `#53 <https://github.com/ansys/ansys-tools-visualization-interface/pull/53>`_, `#70 <https://github.com/ansys/ansys-tools-visualization-interface/pull/70>`_, `#83 <https://github.com/ansys/ansys-tools-visualization-interface/pull/83>`_, `#85 <https://github.com/ansys/ansys-tools-visualization-interface/pull/85>`_, `#89 <https://github.com/ansys/ansys-tools-visualization-interface/pull/89>`_, `#90 <https://github.com/ansys/ansys-tools-visualization-interface/pull/90>`_, `#101 <https://github.com/ansys/ansys-tools-visualization-interface/pull/101>`_, `#109 <https://github.com/ansys/ansys-tools-visualization-interface/pull/109>`_, `#115 <https://github.com/ansys/ansys-tools-visualization-interface/pull/115>`_, `#123 <https://github.com/ansys/ansys-tools-visualization-interface/pull/123>`_
- ci: enable proper Codecov upload `#68 <https://github.com/ansys/ansys-tools-visualization-interface/pull/68>`_
- maint: Add CODEOWNERS file `#76 <https://github.com/ansys/ansys-tools-visualization-interface/pull/76>`_
- maint: Add project URLs to toml `#77 <https://github.com/ansys/ansys-tools-visualization-interface/pull/77>`_
- maint: Upload PDF documentation `#80 <https://github.com/ansys/ansys-tools-visualization-interface/pull/80>`_
- fix: Add details to contributing guide `#81 <https://github.com/ansys/ansys-tools-visualization-interface/pull/81>`_
- maint: Upload to PyPI as trusted publisher `#82 <https://github.com/ansys/ansys-tools-visualization-interface/pull/82>`_
- Added postprocessing visualization example. `#112 <https://github.com/ansys/ansys-tools-visualization-interface/pull/112>`_
- maint: Drop 3.9 support `#122 <https://github.com/ansys/ansys-tools-visualization-interface/pull/122>`_


### Fixed

- fix: Ignore pickle vulnerability `#62 <https://github.com/ansys/ansys-tools-visualization-interface/pull/62>`_
- fix: Fix support for interactive documentation `#63 <https://github.com/ansys/ansys-tools-visualization-interface/pull/63>`_
- fix: usage of global vars throughout the library `#65 <https://github.com/ansys/ansys-tools-visualization-interface/pull/65>`_
- fix: Off_screen not working properly `#71 <https://github.com/ansys/ansys-tools-visualization-interface/pull/71>`_
- fix: Bug in MeshObject clipping `#73 <https://github.com/ansys/ansys-tools-visualization-interface/pull/73>`_
- fix: Rename built in shadowing variables `#75 <https://github.com/ansys/ansys-tools-visualization-interface/pull/75>`_
- fix: dynamic scraper via vtk-osmesa `#88 <https://github.com/ansys/ansys-tools-visualization-interface/pull/88>`_
- fix: Search not working `#93 <https://github.com/ansys/ansys-tools-visualization-interface/pull/93>`_
- fix: Buttons still appearing in doc `#97 <https://github.com/ansys/ansys-tools-visualization-interface/pull/97>`_
- fix: Vue version alignment `#103 <https://github.com/ansys/ansys-tools-visualization-interface/pull/103>`_
- fix: Hovering issues `#104 <https://github.com/ansys/ansys-tools-visualization-interface/pull/104>`_
- fix: Allow PyVista HTML jupyter backend `#119 <https://github.com/ansys/ansys-tools-visualization-interface/pull/119>`_
- fix: Remove Jupyter warning `#135 <https://github.com/ansys/ansys-tools-visualization-interface/pull/135>`_
- fix: Missing support for unstructured grid types `#140 <https://github.com/ansys/ansys-tools-visualization-interface/pull/140>`_
- fix: UnstructuredGrid not working with clipping plane widget `#142 <https://github.com/ansys/ansys-tools-visualization-interface/pull/142>`_
- fix: Remove please from AUTHORS file `#154 <https://github.com/ansys/ansys-tools-visualization-interface/pull/154>`_
- fix: Contributors file template `#156 <https://github.com/ansys/ansys-tools-visualization-interface/pull/156>`_
- fix: update labeler and ci_cd to use email and username `#164 <https://github.com/ansys/ansys-tools-visualization-interface/pull/164>`_
- fix: Missing non initialized variable `#165 <https://github.com/ansys/ansys-tools-visualization-interface/pull/165>`_
- fix: handle properly multi_colors=False `#172 <https://github.com/ansys/ansys-tools-visualization-interface/pull/172>`_
- fix: Changelog action failing on release `#178 <https://github.com/ansys/ansys-tools-visualization-interface/pull/178>`_
- fix: Reduce import time of the library `#179 <https://github.com/ansys/ansys-tools-visualization-interface/pull/179>`_


### Dependencies

- build(deps): bump ansys-sphinx-theme from 0.16.2 to 0.16.5 in the doc-dependencies group `#69 <https://github.com/ansys/ansys-tools-visualization-interface/pull/69>`_
- build(deps): bump pytest from 8.2.1 to 8.2.2 in the test-dependencies group `#72 <https://github.com/ansys/ansys-tools-visualization-interface/pull/72>`_
- build(deps): bump the doc-dependencies group with 2 updates `#84 <https://github.com/ansys/ansys-tools-visualization-interface/pull/84>`_, `#121 <https://github.com/ansys/ansys-tools-visualization-interface/pull/121>`_, `#128 <https://github.com/ansys/ansys-tools-visualization-interface/pull/128>`_, `#176 <https://github.com/ansys/ansys-tools-visualization-interface/pull/176>`_
- build(deps): bump jupytext from 1.16.2 to 1.16.3 in the general-dependencies group `#100 <https://github.com/ansys/ansys-tools-visualization-interface/pull/100>`_
- build(deps): bump pytest from 8.2.2 to 8.3.1 in the test-dependencies group `#105 <https://github.com/ansys/ansys-tools-visualization-interface/pull/105>`_
- build(deps): bump the doc-dependencies group with 3 updates `#106 <https://github.com/ansys/ansys-tools-visualization-interface/pull/106>`_, `#124 <https://github.com/ansys/ansys-tools-visualization-interface/pull/124>`_, `#167 <https://github.com/ansys/ansys-tools-visualization-interface/pull/167>`_
- build(deps): bump pytest from 8.3.1 to 8.3.2 in the test-dependencies group `#113 <https://github.com/ansys/ansys-tools-visualization-interface/pull/113>`_
- build(deps): bump sphinx-autoapi from 3.2.0 to 3.2.1 in the doc-dependencies group `#114 <https://github.com/ansys/ansys-tools-visualization-interface/pull/114>`_
- build(deps): bump jupytext from 1.16.3 to 1.16.4 in the general-dependencies group `#120 <https://github.com/ansys/ansys-tools-visualization-interface/pull/120>`_
- build(deps): bump ansys/actions from 6 to 7 `#125 <https://github.com/ansys/ansys-tools-visualization-interface/pull/125>`_
- build(deps): bump ansys-fluent-core from 0.22.0 to 0.24.0 in the general-dependencies group `#127 <https://github.com/ansys/ansys-tools-visualization-interface/pull/127>`_
- build(deps): bump the general-dependencies group with 2 updates `#131 <https://github.com/ansys/ansys-tools-visualization-interface/pull/131>`_
- build(deps): bump sphinx-autoapi from 3.2.1 to 3.3.1 in the doc-dependencies group `#137 <https://github.com/ansys/ansys-tools-visualization-interface/pull/137>`_
- build(deps): bump ansys-fluent-core from 0.24.2 to 0.25.0 in the general-dependencies group `#143 <https://github.com/ansys/ansys-tools-visualization-interface/pull/143>`_
- build(deps): bump ansys-sphinx-theme from 1.0.7 to 1.0.8 in the doc-dependencies group `#144 <https://github.com/ansys/ansys-tools-visualization-interface/pull/144>`_
- build(deps): bump ansys-fluent-core from 0.25.0 to 0.26.0 in the general-dependencies group `#146 <https://github.com/ansys/ansys-tools-visualization-interface/pull/146>`_
- build(deps): bump pytest from 8.3.2 to 8.3.3 in the test-dependencies group `#147 <https://github.com/ansys/ansys-tools-visualization-interface/pull/147>`_
- build(deps): bump ansys-sphinx-theme from 1.0.8 to 1.0.11 in the doc-dependencies group `#149 <https://github.com/ansys/ansys-tools-visualization-interface/pull/149>`_
- build(deps): bump sphinx-autoapi from 3.3.1 to 3.3.2 in the doc-dependencies group `#151 <https://github.com/ansys/ansys-tools-visualization-interface/pull/151>`_
- build(deps): bump ansys-sphinx-theme from 1.0.11 to 1.1.2 in the doc-dependencies group `#158 <https://github.com/ansys/ansys-tools-visualization-interface/pull/158>`_
- build(deps): bump ansys-fluent-core from 0.26.0 to 0.26.1 in the general-dependencies group `#166 <https://github.com/ansys/ansys-tools-visualization-interface/pull/166>`_
- build(deps): bump ansys-sphinx-theme from 1.1.3 to 1.1.6 in the doc-dependencies group `#171 <https://github.com/ansys/ansys-tools-visualization-interface/pull/171>`_


### Documentation

- build(deps): bump ansys-sphinx-theme from 1.0.5 to 1.0.7 in the doc-dependencies group `#132 <https://github.com/ansys/ansys-tools-visualization-interface/pull/132>`_


### Maintenance

- [pre-commit.ci] pre-commit autoupdate `#126 <https://github.com/ansys/ansys-tools-visualization-interface/pull/126>`_, `#129 <https://github.com/ansys/ansys-tools-visualization-interface/pull/129>`_, `#133 <https://github.com/ansys/ansys-tools-visualization-interface/pull/133>`_, `#138 <https://github.com/ansys/ansys-tools-visualization-interface/pull/138>`_, `#145 <https://github.com/ansys/ansys-tools-visualization-interface/pull/145>`_, `#148 <https://github.com/ansys/ansys-tools-visualization-interface/pull/148>`_, `#150 <https://github.com/ansys/ansys-tools-visualization-interface/pull/150>`_, `#152 <https://github.com/ansys/ansys-tools-visualization-interface/pull/152>`_, `#163 <https://github.com/ansys/ansys-tools-visualization-interface/pull/163>`_, `#168 <https://github.com/ansys/ansys-tools-visualization-interface/pull/168>`_, `#174 <https://github.com/ansys/ansys-tools-visualization-interface/pull/174>`_, `#177 <https://github.com/ansys/ansys-tools-visualization-interface/pull/177>`_
- fix: Remove deprecated name checking action `#159 <https://github.com/ansys/ansys-tools-visualization-interface/pull/159>`_
- maint: add hacktoberfest labels `#161 <https://github.com/ansys/ansys-tools-visualization-interface/pull/161>`_

This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/ansys-tools-visualization-interface/tree/main/doc/changelog.d/>.

<!-- towncrier release notes start -->