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
from typing import Any, Callable, Dict


def extract_kwargs(func: Callable, input_kwargs: Dict[str, Any]) -> Dict[str, Any]:
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
    >>> extract_kwargs(my_func, {"b": 10, "d": 20})
    {"b": 10, "c": 2}
    """
    signature = inspect.signature(func)
    kwargs = {}
    for k, v in signature.parameters.items():
        # We are ignoring positional arguments, and passing everything as kwarg
        if v.default is not inspect.Parameter.empty:
            kwargs[k] = input_kwargs[k] if k in input_kwargs else v.default
    return kwargs
