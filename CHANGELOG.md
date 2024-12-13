## [0.6.2](https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.6.2) - 2024-12-12


### Fixed

- fix: not checking if actors have datasets. [#209](https://github.com/ansys/ansys-tools-visualization-interface/pull/209)


## [0.6.1](https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.6.1) - 2024-12-11


### Fixed

- fix: not checking if actors have datasets. [#209](https://github.com/ansys/ansys-tools-visualization-interface/pull/209)

## [0.6.0](https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.6.0) - 2024-11-26


### Added

- feat: Add PyVista Qt support [#192](https://github.com/ansys/ansys-tools-visualization-interface/pull/192)


### Dependencies

- build(deps): bump pytest-cov from 5.0.0 to 6.0.0 in the test-dependencies group [#182](https://github.com/ansys/ansys-tools-visualization-interface/pull/182)
- build(deps): bump ansys-sphinx-theme from 1.1.7 to 1.2.0 in the doc-dependencies group [#183](https://github.com/ansys/ansys-tools-visualization-interface/pull/183)
- build(deps): update websockets requirement from(14,>=12.0 to >=12.0,<15 in the general-dependencies group [#188](https://github.com/ansys/ansys-tools-visualization-interface/pull/188)
- build(deps): bump codecov/codecov-action from 4 to 5 [#190](https://github.com/ansys/ansys-tools-visualization-interface/pull/190)
- build(deps): bump pyside6 from 6.7.3 to 6.8.0.2 in the general-dependencies group [#193](https://github.com/ansys/ansys-tools-visualization-interface/pull/193)
- build(deps): bump ansys-sphinx-theme from 1.2.0 to 1.2.2 in the doc-dependencies group [#194](https://github.com/ansys/ansys-tools-visualization-interface/pull/194)


### Maintenance

- chore: update CHANGELOG for v0.5.0 [#181](https://github.com/ansys/ansys-tools-visualization-interface/pull/181)
- maint: Update AUTHORS [#184](https://github.com/ansys/ansys-tools-visualization-interface/pull/184)
- [pre-commit.ci] pre-commit autoupdate [#186](https://github.com/ansys/ansys-tools-visualization-interface/pull/186), [#189](https://github.com/ansys/ansys-tools-visualization-interface/pull/189), [#191](https://github.com/ansys/ansys-tools-visualization-interface/pull/191), [#195](https://github.com/ansys/ansys-tools-visualization-interface/pull/195)

## [0.5.0](https://github.com/ansys/ansys-tools-visualization-interface/releases/tag/v0.5.0) - 2024-10-31


### Added

- feat: add changelog and vulnerability check [#58](https://github.com/ansys/ansys-tools-visualization-interface/pull/58)
- feat: add dynamic scraper on docs [#86](https://github.com/ansys/ansys-tools-visualization-interface/pull/86)
- feat: Add interactive documentation [#92](https://github.com/ansys/ansys-tools-visualization-interface/pull/92)
- feat: Remove buttons on screenshot and static docs [#94](https://github.com/ansys/ansys-tools-visualization-interface/pull/94)
- feat: Add plane clip slider [#95](https://github.com/ansys/ansys-tools-visualization-interface/pull/95)
- feat: Add screenshot button [#96](https://github.com/ansys/ansys-tools-visualization-interface/pull/96)
- feat!: Add hover capabilities [#98](https://github.com/ansys/ansys-tools-visualization-interface/pull/98)
- feat: Add show/hide button for buttons [#99](https://github.com/ansys/ansys-tools-visualization-interface/pull/99)
- feat: allow for multi_colors argument in plotting options [#118](https://github.com/ansys/ansys-tools-visualization-interface/pull/118)
- fix: preserve access order using dictionary and adapt show to already existing objects [#175](https://github.com/ansys/ansys-tools-visualization-interface/pull/175)
- feat: Add StructuredGrid support [#180](https://github.com/ansys/ansys-tools-visualization-interface/pull/180)


### Changed

- [pre-commit.ci] pre-commit autoupdate [#53](https://github.com/ansys/ansys-tools-visualization-interface/pull/53), [#70](https://github.com/ansys/ansys-tools-visualization-interface/pull/70), [#83](https://github.com/ansys/ansys-tools-visualization-interface/pull/83), [#85](https://github.com/ansys/ansys-tools-visualization-interface/pull/85), [#89](https://github.com/ansys/ansys-tools-visualization-interface/pull/89), [#90](https://github.com/ansys/ansys-tools-visualization-interface/pull/90), [#101](https://github.com/ansys/ansys-tools-visualization-interface/pull/101), [#109](https://github.com/ansys/ansys-tools-visualization-interface/pull/109), [#115](https://github.com/ansys/ansys-tools-visualization-interface/pull/115), [#123](https://github.com/ansys/ansys-tools-visualization-interface/pull/123)
- ci: enable proper Codecov upload [#68](https://github.com/ansys/ansys-tools-visualization-interface/pull/68)
- maint: Add CODEOWNERS file [#76](https://github.com/ansys/ansys-tools-visualization-interface/pull/76)
- maint: Add project URLs to toml [#77](https://github.com/ansys/ansys-tools-visualization-interface/pull/77)
- maint: Upload PDF documentation [#80](https://github.com/ansys/ansys-tools-visualization-interface/pull/80)
- fix: Add details to contributing guide [#81](https://github.com/ansys/ansys-tools-visualization-interface/pull/81)
- maint: Upload to PyPI as trusted publisher [#82](https://github.com/ansys/ansys-tools-visualization-interface/pull/82)
- Added postprocessing visualization example. [#112](https://github.com/ansys/ansys-tools-visualization-interface/pull/112)
- maint: Drop 3.9 support [#122](https://github.com/ansys/ansys-tools-visualization-interface/pull/122)


### Fixed

- fix: Ignore pickle vulnerability [#62](https://github.com/ansys/ansys-tools-visualization-interface/pull/62)
- fix: Fix support for interactive documentation [#63](https://github.com/ansys/ansys-tools-visualization-interface/pull/63)
- fix: usage of global vars throughout the library [#65](https://github.com/ansys/ansys-tools-visualization-interface/pull/65)
- fix: Off_screen not working properly [#71](https://github.com/ansys/ansys-tools-visualization-interface/pull/71)
- fix: Bug in MeshObject clipping [#73](https://github.com/ansys/ansys-tools-visualization-interface/pull/73)
- fix: Rename built in shadowing variables [#75](https://github.com/ansys/ansys-tools-visualization-interface/pull/75)
- fix: dynamic scraper via vtk-osmesa [#88](https://github.com/ansys/ansys-tools-visualization-interface/pull/88)
- fix: Search not working [#93](https://github.com/ansys/ansys-tools-visualization-interface/pull/93)
- fix: Buttons still appearing in doc [#97](https://github.com/ansys/ansys-tools-visualization-interface/pull/97)
- fix: Vue version alignment [#103](https://github.com/ansys/ansys-tools-visualization-interface/pull/103)
- fix: Hovering issues [#104](https://github.com/ansys/ansys-tools-visualization-interface/pull/104)
- fix: Allow PyVista HTML jupyter backend [#119](https://github.com/ansys/ansys-tools-visualization-interface/pull/119)
- fix: Remove Jupyter warning [#135](https://github.com/ansys/ansys-tools-visualization-interface/pull/135)
- fix: Missing support for unstructured grid types [#140](https://github.com/ansys/ansys-tools-visualization-interface/pull/140)
- fix: UnstructuredGrid not working with clipping plane widget [#142](https://github.com/ansys/ansys-tools-visualization-interface/pull/142)
- fix: Remove please from AUTHORS file [#154](https://github.com/ansys/ansys-tools-visualization-interface/pull/154)
- fix: Contributors file template [#156](https://github.com/ansys/ansys-tools-visualization-interface/pull/156)
- fix: update labeler and ci_cd to use email and username [#164](https://github.com/ansys/ansys-tools-visualization-interface/pull/164)
- fix: Missing non initialized variable [#165](https://github.com/ansys/ansys-tools-visualization-interface/pull/165)
- fix: handle properly multi_colors=False [#172](https://github.com/ansys/ansys-tools-visualization-interface/pull/172)
- fix: Changelog action failing on release [#178](https://github.com/ansys/ansys-tools-visualization-interface/pull/178)
- fix: Reduce import time of the library [#179](https://github.com/ansys/ansys-tools-visualization-interface/pull/179)


### Dependencies

- build(deps): bump ansys-sphinx-theme from 0.16.2 to 0.16.5 in the doc-dependencies group [#69](https://github.com/ansys/ansys-tools-visualization-interface/pull/69)
- build(deps): bump pytest from 8.2.1 to 8.2.2 in the test-dependencies group [#72](https://github.com/ansys/ansys-tools-visualization-interface/pull/72)
- build(deps): bump the doc-dependencies group with 2 updates [#84](https://github.com/ansys/ansys-tools-visualization-interface/pull/84), [#121](https://github.com/ansys/ansys-tools-visualization-interface/pull/121), [#128](https://github.com/ansys/ansys-tools-visualization-interface/pull/128), [#176](https://github.com/ansys/ansys-tools-visualization-interface/pull/176)
- build(deps): bump jupytext from 1.16.2 to 1.16.3 in the general-dependencies group [#100](https://github.com/ansys/ansys-tools-visualization-interface/pull/100)
- build(deps): bump pytest from 8.2.2 to 8.3.1 in the test-dependencies group [#105](https://github.com/ansys/ansys-tools-visualization-interface/pull/105)
- build(deps): bump the doc-dependencies group with 3 updates [#106](https://github.com/ansys/ansys-tools-visualization-interface/pull/106), [#124](https://github.com/ansys/ansys-tools-visualization-interface/pull/124), [#167](https://github.com/ansys/ansys-tools-visualization-interface/pull/167)
- build(deps): bump pytest from 8.3.1 to 8.3.2 in the test-dependencies group [#113](https://github.com/ansys/ansys-tools-visualization-interface/pull/113)
- build(deps): bump sphinx-autoapi from 3.2.0 to 3.2.1 in the doc-dependencies group [#114](https://github.com/ansys/ansys-tools-visualization-interface/pull/114)
- build(deps): bump jupytext from 1.16.3 to 1.16.4 in the general-dependencies group [#120](https://github.com/ansys/ansys-tools-visualization-interface/pull/120)
- build(deps): bump ansys/actions from 6 to 7 [#125](https://github.com/ansys/ansys-tools-visualization-interface/pull/125)
- build(deps): bump ansys-fluent-core from 0.22.0 to 0.24.0 in the general-dependencies group [#127](https://github.com/ansys/ansys-tools-visualization-interface/pull/127)
- build(deps): bump the general-dependencies group with 2 updates [#131](https://github.com/ansys/ansys-tools-visualization-interface/pull/131)
- build(deps): bump sphinx-autoapi from 3.2.1 to 3.3.1 in the doc-dependencies group [#137](https://github.com/ansys/ansys-tools-visualization-interface/pull/137)
- build(deps): bump ansys-fluent-core from 0.24.2 to 0.25.0 in the general-dependencies group [#143](https://github.com/ansys/ansys-tools-visualization-interface/pull/143)
- build(deps): bump ansys-sphinx-theme from 1.0.7 to 1.0.8 in the doc-dependencies group [#144](https://github.com/ansys/ansys-tools-visualization-interface/pull/144)
- build(deps): bump ansys-fluent-core from 0.25.0 to 0.26.0 in the general-dependencies group [#146](https://github.com/ansys/ansys-tools-visualization-interface/pull/146)
- build(deps): bump pytest from 8.3.2 to 8.3.3 in the test-dependencies group [#147](https://github.com/ansys/ansys-tools-visualization-interface/pull/147)
- build(deps): bump ansys-sphinx-theme from 1.0.8 to 1.0.11 in the doc-dependencies group [#149](https://github.com/ansys/ansys-tools-visualization-interface/pull/149)
- build(deps): bump sphinx-autoapi from 3.3.1 to 3.3.2 in the doc-dependencies group [#151](https://github.com/ansys/ansys-tools-visualization-interface/pull/151)
- build(deps): bump ansys-sphinx-theme from 1.0.11 to 1.1.2 in the doc-dependencies group [#158](https://github.com/ansys/ansys-tools-visualization-interface/pull/158)
- build(deps): bump ansys-fluent-core from 0.26.0 to 0.26.1 in the general-dependencies group [#166](https://github.com/ansys/ansys-tools-visualization-interface/pull/166)
- build(deps): bump ansys-sphinx-theme from 1.1.3 to 1.1.6 in the doc-dependencies group [#171](https://github.com/ansys/ansys-tools-visualization-interface/pull/171)


### Documentation

- build(deps): bump ansys-sphinx-theme from 1.0.5 to 1.0.7 in the doc-dependencies group [#132](https://github.com/ansys/ansys-tools-visualization-interface/pull/132)


### Maintenance

- [pre-commit.ci] pre-commit autoupdate [#126](https://github.com/ansys/ansys-tools-visualization-interface/pull/126), [#129](https://github.com/ansys/ansys-tools-visualization-interface/pull/129), [#133](https://github.com/ansys/ansys-tools-visualization-interface/pull/133), [#138](https://github.com/ansys/ansys-tools-visualization-interface/pull/138), [#145](https://github.com/ansys/ansys-tools-visualization-interface/pull/145), [#148](https://github.com/ansys/ansys-tools-visualization-interface/pull/148), [#150](https://github.com/ansys/ansys-tools-visualization-interface/pull/150), [#152](https://github.com/ansys/ansys-tools-visualization-interface/pull/152), [#163](https://github.com/ansys/ansys-tools-visualization-interface/pull/163), [#168](https://github.com/ansys/ansys-tools-visualization-interface/pull/168), [#174](https://github.com/ansys/ansys-tools-visualization-interface/pull/174), [#177](https://github.com/ansys/ansys-tools-visualization-interface/pull/177)
- fix: Remove deprecated name checking action [#159](https://github.com/ansys/ansys-tools-visualization-interface/pull/159)
- maint: add hacktoberfest labels [#161](https://github.com/ansys/ansys-tools-visualization-interface/pull/161)

This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in(https://github.com/ansys/ansys-tools-visualization-interface/tree/main/doc/changelog.d/>.

<!-- towncrier release notes start -->