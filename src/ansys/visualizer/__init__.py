# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
"""PyAnsys visualizer is a python package to help visualize the results of ansys simulations."""
import os

import pkg_resources

__version__ = pkg_resources.get_distribution("pyansys-visualizer").version

USE_TRAME: bool = False
DOCUMENTATION_BUILD: bool = False
TESTING_MODE: bool = os.environ.get("PYANSYS_VISUALIZER_TESTMODE", "false").lower() == "true"
from ansys.visualizer.plotter import Plotter, PlotterInterface
from ansys.visualizer.types.edgeplot import EdgePlot
from ansys.visualizer.types.meshobjectplot import MeshObjectPlot
from ansys.visualizer.utils.clip_plane import ClipPlane
from ansys.visualizer.utils.colors import Colors
from ansys.visualizer.widgets.widget import PlotterWidget
