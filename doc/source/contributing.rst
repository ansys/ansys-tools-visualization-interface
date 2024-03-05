Contribute
##########

Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar
with this guide before attempting to contribute to PyAnsys Visualizer.

The following contribution information is specific to PyAnsys Visualizer.

Clone the repository
--------------------

To clone and install the latest PyAnsys Visualizer release in development mode, run
these commands:

.. code::

    git clone https://github.com/ansys/pyansys-visualizer
    cd pyansys-visualizer
    python -m pip install --upgrade pip
    pip install -e .


Post issues
-----------

Use the `PyAnsys Visualizer Issues <https://github.com/ansys/pyansys-visualizer/issues>`_
page to submit questions, report bugs, and request new features. When possible, you
should use these issue templates:

* Bug, problem, error: For filing a bug report
* Documentation error: For requesting modifications to the documentation
* Adding an example: For proposing a new example
* New feature: For requesting enhancements to the code

If your issue does not fit into one of these template categories, you can click
the link for opening a blank issue.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

View documentation
------------------

Documentation for the latest stable release of PyAnsys Visualizer is hosted at
`PyAnsys Visualizer Documentation <https://visualizer.docs.pyansys.com>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

Adhere to code style
--------------------

PyAnsys Visualizer follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys Developer's Guide* and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  black....................................................................Passed
  blacken-docs.............................................................Passed
  isort....................................................................Passed
  flake8...................................................................Passed
  docformatter.............................................................Passed
  codespell................................................................Passed
  pydocstyle...............................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  check yaml...............................................................Passed
  trim trailing whitespace.................................................Passed
  Add License Headers......................................................Passed
  Validate GitHub Workflows................................................Passed

Build the documentation
-----------------------

.. note::

  To build the documentation locally, you must run this command to install the
  documentation dependencies::

    pip install -e .[doc]

Then, navigate to the ``docs`` directory and run this command::

  # On Linux or macOS
  make html

  # On Windows
  ./make.bat html

The documentation is built in the ``docs/_build/html`` directory.

You can clean the documentation build by running this command::

  # On Linux or macOS
  make clean

  # On Windows
  ./make.bat clean

Run tests
---------

PyAnsys Visualizer uses `pytest <https://docs.pytest.org/en/stable/>`_ for testing.

Prerequisites
^^^^^^^^^^^^^

Prior to running the tests, you must run this command to install the test dependencies::

  pip install -e .[tests]

Make sure to define the port and host of the service using the following environment variables::

  # On Linux or macOS
  export ANSRV_GEO_PORT=5000
  export ANSRV_GEO_HOST=localhost

  # On Windows CMD
  set ANSRV_GEO_PORT=5000
  set ANSRV_GEO_HOST=localhost

  # On Windows PowerShell
  $env:ANSRV_GEO_PORT=5000
  $env:ANSRV_GEO_HOST="localhost"

Running the tests
^^^^^^^^^^^^^^^^^

To run the tests, navigate to the root directory of the repository and run this command::

  pytest
