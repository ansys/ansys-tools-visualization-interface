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
"""Visualization Interface tool is a Python client library for visualizing the results of Ansys simulations."""
import os

import pkg_resources

__version__ = pkg_resources.get_distribution("ansys-tools-visualization-interface").version

USE_TRAME: bool = False
DOCUMENTATION_BUILD: bool = False
TESTING_MODE: bool = os.environ.get("PYANSYS_VISUALIZER_TESTMODE", "false").lower() == "true"

from ansys.tools.visualization_interface.plotter import Plotter  # noqa: F401, E402
from ansys.tools.visualization_interface.types.edge_plot import EdgePlot  # noqa: F401, E402
from ansys.tools.visualization_interface.types.mesh_object_plot import (  # noqa: F401, E402
    MeshObjectPlot,
)
from ansys.tools.visualization_interface.utils.clip_plane import ClipPlane  # noqa: F401, E402
from ansys.tools.visualization_interface.utils.color import Color  # noqa: F401, E402
