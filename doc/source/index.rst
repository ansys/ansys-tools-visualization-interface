PyAnsys Visualizer documentation |version|
==========================================

PyAnsys Visualizer is a Python package that provides a simple interface to visualize ANSYS results.

.. grid:: 1 2 2 2


    .. grid-item-card:: Getting started :fa:`person-running`
        :padding: 2 2 2 2
        :link: getting_started/index
        :link-type: doc

        Learn how to install and the basic usage of PyAnsys Visualizer.

    .. grid-item-card:: User guide :fa:`book-open-reader`
        :padding: 2 2 2 2
        :link: user_guide/index
        :link-type: doc

        Understand key concepts to implement PyAnsys Visualizer in your workflow.

    .. jinja:: main_toctree

        {% if build_api %}
        .. grid-item-card:: API reference :fa:`book-bookmark`
            :padding: 2 2 2 2
            :link: api/index
            :link-type: doc

            Understand PyAnsys Geometry API endpoints, their capabilities,
            and how to interact with them programmatically.
        {% endif %}

        {% if build_examples %}
        .. grid-item-card:: Examples :fa:`scroll`
            :padding: 2 2 2 2
            :link: examples
            :link-type: doc

            Explore examples that show how to use PyAnsys Geometry to
            perform many different types of operations.
        {% endif %}

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
       examples
       {% endif %}
       contributing
       assets