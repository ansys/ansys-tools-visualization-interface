# Copyright (C) 2024 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Utilities for filtering and extracting keyword arguments."""
import inspect
from typing import Any, Callable, Dict, List, Optional


def _extract_kwargs(func: Callable, input_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Extract keyword arguments that match a function's signature.

    This function inspects the signature of a callable and returns a dictionary
    containing only the keyword arguments that the function accepts. For each
    parameter with a default value, it uses the value from ``input_kwargs`` if
    present, otherwise it uses the parameter's default value.

    Parameters
    ----------
    func : Callable
        Function to extract the keyword arguments from.
    input_kwargs : Dict[str, Any]
        Dictionary with keyword arguments to filter.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing only the keyword arguments that match the
        function's signature, with values from ``input_kwargs`` or defaults.

    Notes
    -----
    - Only parameters with default values are included in the output.
    - Positional-only parameters without defaults are ignored.
    - This is useful for filtering kwargs before passing to PyVista functions.

    Examples
    --------
    >>> def my_func(a, b=1, c=2):
    ...     pass
    >>> _extract_kwargs(my_func, {"b": 10, "d": 20})
    {"b": 10, "c": 2}
    """
    signature = inspect.signature(func)
    kwargs = {}
    for k, v in signature.parameters.items():
        # We are ignoring positional arguments, and passing everything as kwarg
        if v.default is not inspect.Parameter.empty:
            kwargs[k] = input_kwargs[k] if k in input_kwargs else v.default
    return kwargs


def _capture_init_params(
    func_or_method: Callable,
    locals_dict: Dict[str, Any],
    exclude: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Capture initialization parameters from a function's locals for reinitialization.

    This function dynamically extracts all parameters passed to an ``__init__`` method
    by inspecting its signature and reading values from the ``locals()`` dictionary.
    This is particularly useful for implementing reinitialization patterns where the
    exact initialization parameters need to be saved and replayed later.

    Parameters
    ----------
    func_or_method : Callable
        The function or method whose parameters should be captured. Typically
        ``self.__init__`` or the class's ``__init__`` method.
    locals_dict : Dict[str, Any]
        The ``locals()`` dictionary from inside the ``__init__`` method. This
        contains the actual values of all parameters at the point of capture.
    exclude : Optional[List[str]], default: None
        List of parameter names to exclude from the result. Common exclusions
        are ``'self'`` and ``'cls'``, though ``'self'`` is automatically excluded.

    Returns
    -------
    Dict[str, Any]
        Dictionary mapping parameter names to their values, suitable for unpacking
        with ``**`` when calling the function. If the signature includes ``**kwargs``,
        those are flattened into the result dictionary.

    Examples
    --------
    Using in a child class after super():

    >>> class Parent:
    ...     def __init__(self, x, y):
    ...         self.x = x
    ...         self.y = y
    ...
    >>> class Child(Parent):
    ...     def __init__(self, x, y, z):
    ...         super().__init__(x, y)
    ...         # Capture after super() to avoid interference
    ...         self._init_params = _capture_init_params(
    ...             self.__init__,
    ...             locals()
    ...         )
    ...
    >>> obj = Child(1, 2, 3)
    >>> obj._init_params
    {'x': 1, 'y': 2, 'z': 3}
    """
    if exclude is None:
        exclude = []

    exclude_set = set(exclude) | {'self', 'cls'}
    sig = inspect.signature(func_or_method)
    result = {}

    for param_name, param in sig.parameters.items():
        if param_name in exclude_set:
            continue
        if param_name not in locals_dict:
            continue

        # Handle VAR_KEYWORD (**kwargs) parameters
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            # Flatten the kwargs into the result
            kwargs_value = locals_dict[param_name]
            if isinstance(kwargs_value, dict):
                result.update(kwargs_value)
        else:
            # Regular parameter - add directly
            result[param_name] = locals_dict[param_name]

    return result
