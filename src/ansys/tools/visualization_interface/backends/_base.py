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

"""Module for the backend base class."""
from abc import ABC, abstractmethod
from typing import Any, Iterable


class BaseBackend(ABC):
    """Base class for plotting backends."""

    @abstractmethod
    def plot(self, plottable_object: Any, **plotting_options):
        """Plot the specified object."""
        raise NotImplementedError("plot method must be implemented")

    @abstractmethod
    def plot_iter(self, plotting_list: Iterable):
        """Plot the elements of an iterable."""
        raise NotImplementedError("plot_iter method must be implemented")

    @abstractmethod
    def show(self):
        """Show the plotted objects."""
        raise NotImplementedError("show method must be implemented")
