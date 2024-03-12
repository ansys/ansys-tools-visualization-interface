PyAnsys Visualizer documentation |version|
==========================================

PyAnsys Visualizer is a Python client library that provides a simple user interface
for visualizing Ansys data. This library is built on top of
`PyVista <https://docs.pyvista.org/version/stable/>`_.

PyAnsys Visualizer offers these main features:

* Serves as an interface between PyAnsys and other plotting libraries (although only
  PyVista is supported currently).
* Provides out-of-the box picking, viewing, and measuring functionalities.
* Supplies an extensible class for adding custom functionalities.

.. grid:: 1 2 2 2


    .. grid-item-card:: Getting started :material-regular:`directions_run`
        :padding: 2 2 2 2
        :link: getting_started/index
        :link-type: doc

        Learn how to install PyAnsys Visualizer in user mode and quickly
        begin using it.

    .. grid-item-card:: User guide :material-regular:`menu_book`
        :padding: 2 2 2 2
        :link: user_guide/index
        :link-type: doc

        Understand key concepts for implementing PyAnsys Visualizer in
        your workflow.

    .. jinja:: main_toctree

        {% if build_api %}
        .. grid-item-card:: API reference :material-regular:`bookmark`
            :padding: 2 2 2 2
            :link: api/index
            :link-type: doc

            Understand how to use Python to interact programmatically with
            PyAnsys Visualizer.
        {% endif %}

        {% if build_examples %}
        .. grid-item-card:: Examples :material-regular:`play_arrow`
            :padding: 2 2 2 2
            :link: examples/index
            :link-type: doc

            Explore examples that show how to use PyAnsys Visualizer to
            perform many different types of operations.
        {% endif %}

        .. grid-item-card:: Contribute :material-regular:`people-group`
            :padding: 2 2 2 2
            :link: contributing
            :link-type: doc

            Learn how to contribute to the PyAnsys Visualizer codebase or documentation.


.. jinja:: main_toctree

    .. toctree::
       :hidden:
       :maxdepth: 3

       getting_started/index
       user_guide/index
       {% if build_api %}
       api/index
       {% endif %}
       {% if build_examples %}
       examples/index
       {% endif %}
       contributing