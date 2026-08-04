Visualization Interface Tool documentation |version|
====================================================

The Visualization Interface Tool is a Python API that provides an interface between PyAnsys libraries and
different plotting backends.

The Visualization Interface Tool offers these main features:

* Serves as an interface between PyAnsys and other plotting libraries (although only
  `PyVista <https://docs.pyvista.org/version/stable/>`_ is supported currently).
* Provides out-of-the box picking, viewing, and measuring functionalities.
* Supplies an extensible class for adding custom functionalities.

.. grid:: 1 2 2 2


    .. grid-item-card:: Getting started :material-regular:`directions_run`
        :padding: 2 2 2 2
        :link: getting_started/index
        :link-type: doc

        Learn how to install the Visualization Interface Tool in user mode and quickly
        begin using it.

    .. grid-item-card:: User guide :material-regular:`menu_book`
        :padding: 2 2 2 2
        :link: user_guide/index
        :link-type: doc

        Understand key concepts for implementing the Visualization Interface Tool in
        your workflow.

    .. jinja:: main_toctree

        {% if build_api %}
        .. grid-item-card:: API reference :material-regular:`bookmark`
            :padding: 2 2 2 2
            :link: api/index
            :link-type: doc

            Understand how to use Python to interact programmatically with
            the Visualization Interface Tool.
        {% endif %}

        {% if build_examples %}
        .. grid-item-card:: Examples :material-regular:`play_arrow`
            :padding: 2 2 2 2
            :link: examples/index
            :link-type: doc

            Explore examples that show how to use the Visualization Interface Tool to
            perform many different types of operations.
        {% endif %}

        .. grid-item-card:: Contribute :material-regular:`group`
            :padding: 2 2 2 2
            :link: contributing
            :link-type: doc

            Learn how to contribute to the Visualization Interface Tool codebase or documentation.


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