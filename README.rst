PyAnsys Visualizer
==================
|pyansys| |MIT|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. contents::

Overview
--------

PyAnsys Visualizer is a Python API that provides an interface between PyAnsys libraries and
different plotting backends.

PyAnsys Visualizer offers these main features:

* Serves as an interface between PyAnsys and other plotting libraries (although only
  `PyVista <https://docs.pyvista.org/version/stable/>`_ is supported currently).
* Provides out-of-the box picking, viewing, and measuring functionalities.
* Supplies an extensible class for adding custom functionalities.

Documentation and issues
------------------------

Documentation for the latest stable release of PyAnsys Visualizer is hosted
at `PyAnsys Visualizer documentation <https://visualizer.docs.pyansys.com/version/dev/`_.

The documentation has these sections:

- `Getting started <https://visualizer.docs.pyansys.com/version/dev/getting_started/index.html>`_: Learn
  how to install PyAnsys Visualizer in user mode and quickly begin using it.
- `User guide <https://visualizer.docs.pyansys.com/version/dev/user_guide/index.html>`_: Understand key
  concepts for implementing PyAnsys Visualizer in your workflow.
- `API reference <https://visualizer.docs.pyansys.com/version/dev/api/index.html>`_: Understand how to
  use Python to interact programmatically with PyAnsys Visualizer.
- `Examples <visualizer.docs.pyansys.com/version/dev/examples/index.html>`_: Explore examples that
  show how to use PyAnsys Visualizer to perform many different types of operations.
- `Contribute <https://visualizer.docs.pyansys.com/version/dev/contributing/index.html>`_: Learn how to
  contribute to the PyAnsys Visualizer codebase or documentation.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

On the `PyAnsys Visualizer Issues <https://github.com/ansys-internal/pyansys-visualizer/issues>`_
page, you can create issues to report bugs and request new features. On the
`Discussions <https://discuss.ansys.com/>`_ page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

If you have general questions about the PyAnsys ecosystem, email
`pyansys.core@ansys.com <pyansys.core@ansys.com>`_. If your
question is specific to PyAnsys Visualizer, ask your
question in an issue as described in the previous paragraph.

License
-------

PyAnsys Visualizer is licensed under the `MIT License <https://github.com/ansys-internal/pyansys-visualizer/blob/main/LICENSE>`_.

PyAnsys Visualizer makes no commercial claim over Ansys whatsoever. This library adds a
Python interface for visualizing Ansys results without changing the core behavior or
license of the original Ansys software.
