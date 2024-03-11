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

PyAnsys Visualizer is a Python API that provides an interface between PyAnsys libraries and plotting backends.

Installation
^^^^^^^^^^^^

To install the developer version of PyAnsys Visualizer, use pip.

.. code:: bash

    git clone https://github.com/ansys-internal/pyansys-visualizer
    cd pyansys-visualizer
    pip install -e .

Quick Start
^^^^^^^^^^^

The following examples demonstrates how to visualize a result file using PyAnsys Visualizer.

Using PyVista meshes only:

.. code:: python

    from ansys.visualizer import Plotter

    my_mesh = my_custom_object.get_mesh()

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.add(my_mesh)

    # Plot the result
    pl.plot()


Using objects from your library:

.. code:: python

    from ansys.visualizer import Plotter, MeshObjectPlot

    my_custom_object = MyObject()
    my_mesh = my_custom_object.get_mesh()

    meshobject = MeshObjectPlot(my_custom_object, my_mesh)

    # Create a PyAnsys Visualizer object
    pl = Plotter()
    pl.add(meshobject)

    # Plot the result
    pl.plot()

