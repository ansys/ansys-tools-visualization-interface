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
Example demonstrating automatic dynamic tree menu with clickable buttons.

When you create a Plotter with allow_picking=True, a dynamic tree menu is
automatically added to the right side. Each object gets a clickable checkbox button!
"""

import pyvista as pv
from ansys.tools.visualization_interface import Plotter, MeshObjectPlot
from ansys.tools.visualization_interface.backends.pyvista.pyvista import PyVistaBackend

# Create a hierarchical structure with meaningful names
parent = MeshObjectPlot("Sun", pv.Sphere(center=(0, 0, 0), radius=1.5))
child1 = MeshObjectPlot("Earth", pv.Sphere(center=(4, 0, 0), radius=0.8))
child2 = MeshObjectPlot("Mars", pv.Sphere(center=(-4, 0, 0), radius=0.6))
grandchild1 = MeshObjectPlot("Moon", pv.Sphere(center=(5.5, 0, 0), radius=0.3))
grandchild2 = MeshObjectPlot("Space Station", pv.Cube(center=(4, 1.2, 0)))

# Build solar system hierarchy
parent.add_child(child1)
parent.add_child(child2)
child1.add_child(grandchild1)
child1.add_child(grandchild2)

# Create plotter - dynamic menu is automatically added!
backend = PyVistaBackend(allow_picking=True)
pl = Plotter(backend=backend)

# Plot objects
pl.plot(parent, color="yellow")
pl.plot(child1, color="blue")
pl.plot(child2, color="red")
pl.plot(grandchild1, color="gray")
pl.plot(grandchild2, color="white")

print("\n" + "="*70)
print("AUTOMATIC DYNAMIC TREE MENU")
print("="*70)
print("\nA clickable menu appears automatically on the right side!")
print("\nFEATURES:")
print("  - Checkbox button for each object")
print("  - Green checkbox = Visible")
print("  - Red checkbox = Hidden")
print("  - Indentation shows hierarchy")
print("  - Click parent to hide/show entire subtree")
print("\nTRY IT:")
print("  1. Click 'Sun' button -> Hides entire solar system")
print("  2. Click 'Earth' button -> Hides Earth, Moon, and Space Station")
print("  3. Click 'Moon' button -> Hides only the Moon")
print("  4. Click any button again -> Shows it back")
print("\nThe menu is automatically created - no code needed!")
print("="*70 + "\n")

pl.show()
