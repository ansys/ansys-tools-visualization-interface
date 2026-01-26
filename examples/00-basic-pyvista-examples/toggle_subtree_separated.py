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

"""
.. _ref_toggle_subtree_separated:

==========================================
Toggle subtree visibility - Separated objects
==========================================

This example demonstrates toggling visibility of hierarchical objects
that are spatially separated, making it easy to see when children
are hidden or shown.

We create a "solar system" style hierarchy with a parent sphere at the center
and children arranged in a circle around it, with grandchildren further out.
"""

import numpy as np
import pyvista as pv

from ansys.tools.visualization_interface import MeshObjectPlot, Plotter
from ansys.tools.visualization_interface.backends.pyvista.pyvista import PyVistaBackend

# %%
# Create spatially separated hierarchy
# =====================================
# Create a parent object at the origin and arrange children around it.

# Parent - large sphere at center (RED)
parent_mesh = pv.Sphere(center=(0, 0, 0), radius=1.0)
parent = MeshObjectPlot("Parent", parent_mesh)

# Create 4 children arranged in a circle around the parent (BLUE)
children = []
radius = 4.0  # Distance from center
for i in range(4):
    angle = i * np.pi / 2  # 90 degrees apart
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    z = 0

    child_mesh = pv.Sphere(center=(x, y, z), radius=0.6)
    child = MeshObjectPlot(f"Child_{i}", child_mesh)
    parent.add_child(child)
    children.append(child)

    # Add 2 grandchildren to each child (GREEN)
    for j in range(2):
        # Place grandchildren further out from their parent
        gx = x + 1.5 * np.cos(angle + (j - 0.5) * 0.5)
        gy = y + 1.5 * np.sin(angle + (j - 0.5) * 0.5)
        gz = (j - 0.5) * 1.5

        grandchild_mesh = pv.Sphere(center=(gx, gy, gz), radius=0.3)
        grandchild = MeshObjectPlot(f"Grandchild_{i}_{j}", grandchild_mesh)
        child.add_child(grandchild)

# %%
# Visualize with picking and toggle button
# =========================================
# Create plotter with picking enabled. The ToggleSubtreeButton will be
# automatically added to the interface.

backend = PyVistaBackend(allow_picking=True)
plotter = Plotter(backend=backend)

# Plot with different colors for hierarchy levels
plotter.plot(parent, color="red", name="Parent")
for i, child in enumerate(parent._children):
    plotter.plot(child, color="lightblue", name=f"Child_{i}")
    for j, grandchild in enumerate(child._children):
        plotter.plot(grandchild, color="lightgreen", name=f"GC_{i}_{j}")

# %%
# Instructions
# ============
# 1. Click on the RED parent sphere to pick it
# 2. Click the toggle visibility button (eye icon in top-left area)
# 3. The parent and ALL its children (blue and green spheres) will disappear
# 4. Click the button again to show them all again
#
# You can also:
# - Pick a BLUE child sphere and toggle - only that child and its green grandchildren hide
# - Pick a GREEN grandchild and toggle - only that specific sphere hides (no children)
# - Unpick any object (click empty space or press 'u') - hidden objects automatically reappear!

print("\nHierarchy structure:")
print("  Parent (red) - at origin")
print("    +- Child_0 (blue) - 4 children in circle around parent")
print("    +- Child_1 (blue)")
print("    +- Child_2 (blue)")
print("    +- Child_3 (blue)")
print("         +- Each child has 2 grandchildren (green)")
print("\nPick any object (click on it) and then click the toggle button to hide/show its subtree!")
print("Unpick (click empty space or press 'u') to automatically restore visibility!")

plotter.show()
