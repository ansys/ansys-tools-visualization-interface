# Contribute

Overall guidance on contributing to a PyAnsys library appears in the
[Contributing] topic in the *PyAnsys developer's guide*. Ensure that you
are thoroughly familiar with this guide before attempting to contribute to
ansys-tools-visualization-interface.

The following contribution information is specific to *Ansys Tools Visualization Interface*.

[Contributing]: https://dev.docs.pyansys.com/how-to/contributing.html

<!-- Begin content specific to your library here. -->

## Clone the repository

To clone and install the latest *Ansys Tools Visualization Interface* release in development mode, run
these commands:

```bash
git clone https://github.com/ansys/ansys-tools-visualization-interface/
cd ansys-tools-visualization-interface
python -m pip install --upgrade pip
pip install -e .
```

## Adhere to code style

*Ansys Tools Visualization Interface* follows the PEP8 standard as outlined in PEP 8 in the PyAnsys Developer’s Guide and implements style checking using pre-commit.

To ensure your code meets minimum code styling standards, run these commands:

```bash
pip install pre-commit
pre-commit run --all-files
```

You can also install this as a pre-commit hook by running this command:

```bash
pre-commit install
```

## Run the tests

Prior to running the tests, you must run this command to install the test dependencies:

```bash
pip install -e .[tests]
```

To run the tests, navigate to the root directory of the repository and run this command:

```bash
pytest
```


## Build the documentation

Prior to building the documentation, you must run this command to install the documentation dependencies:

```bash
pip install -e .[doc]
```

To build the documentation, run the following commands:

```bash
cd doc

# On linux
make html

# On windows
./make.bat html
```

The documentation is built in the `docs/_build/html` directory.
