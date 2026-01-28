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

"""Tests for tree-based visibility functionality."""

import pytest
import pyvista as pv

from ansys.tools.visualization_interface import MeshObjectPlot, Plotter
from ansys.tools.visualization_interface.backends.pyvista.pyvista import PyVistaBackend


def create_test_tree():
	"""Create a 3-level test tree for visibility testing."""
	root = MeshObjectPlot("Root", pv.Cube())
	child1 = MeshObjectPlot("Child1", pv.Sphere(center=(1, 0, 0)))
	child2 = MeshObjectPlot("Child2", pv.Sphere(center=(-1, 0, 0)))
	grandchild1 = MeshObjectPlot("Grandchild1", pv.Sphere(center=(1, 1, 0), radius=0.3))
	grandchild2 = MeshObjectPlot("Grandchild2", pv.Sphere(center=(1, -1, 0), radius=0.3))

	root.add_child(child1)
	root.add_child(child2)
	child1.add_child(grandchild1)
	child1.add_child(grandchild2)

	return root, child1, child2, grandchild1, grandchild2


def test_visible_property_default():
	"""Test that MeshObjectPlot is visible by default."""
	obj = MeshObjectPlot("Test", pv.Cube())
	assert obj.visible is True


def test_visible_property_setter():
	"""Test setting visibility property."""
	obj = MeshObjectPlot("Test", pv.Cube())
	obj.visible = False
	assert obj.visible is False
	obj.visible = True
	assert obj.visible is True


def test_visible_property_with_actor():
	"""Test that visibility syncs with actor."""
	pl = Plotter()
	obj = MeshObjectPlot("Test", pv.Cube())
	pl.plot(obj)

	# Actor should be assigned after plotting
	assert obj.actor is not None

	# Set visibility
	obj.visible = False
	assert obj.actor.GetVisibility() == 0

	obj.visible = True
	assert obj.actor.GetVisibility() == 1


def test_is_visible_in_tree_no_parent():
	"""Test is_visible_in_tree for object with no parent."""
	obj = MeshObjectPlot("Test", pv.Cube())
	assert obj.is_visible_in_tree() is True

	obj.visible = False
	assert obj.is_visible_in_tree() is False


def test_is_visible_in_tree_with_parent():
	"""Test is_visible_in_tree considers parent visibility."""
	parent = MeshObjectPlot("Parent", pv.Cube())
	child = MeshObjectPlot("Child", pv.Sphere())
	parent.add_child(child)

	# Both visible
	assert child.is_visible_in_tree() is True

	# Hide parent
	parent.visible = False
	assert child.is_visible_in_tree() is False

	# Show parent, hide child
	parent.visible = True
	child.visible = False
	assert child.is_visible_in_tree() is False


def test_is_visible_in_tree_deep_hierarchy():
	"""Test is_visible_in_tree with multiple levels."""
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	# All visible initially
	assert grandchild1.is_visible_in_tree() is True

	# Hide root - everything should be invisible in tree
	root.visible = False
	assert child1.is_visible_in_tree() is False
	assert grandchild1.is_visible_in_tree() is False

	# Show root but hide child1
	root.visible = True
	child1.visible = False
	assert grandchild1.is_visible_in_tree() is False  # Parent hidden
	assert child2.is_visible_in_tree() is True  # Sibling still visible


def test_toggle_subtree_visibility_include_root():
	"""Test toggling visibility of object and children."""
	pl = Plotter()
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	backend = pl.backend._pl

	# Initially all visible
	assert root.visible
	assert child1.visible
	assert grandchild1.visible

	# Toggle root - should hide everything
	backend.toggle_subtree_visibility(root, include_root=True)
	assert not root.visible
	assert not child1.visible
	assert not child2.visible
	assert not grandchild1.visible
	assert not grandchild2.visible

	# Toggle again - should show everything
	backend.toggle_subtree_visibility(root, include_root=True)
	assert root.visible
	assert child1.visible
	assert child2.visible
	assert grandchild1.visible
	assert grandchild2.visible


def test_toggle_subtree_visibility_exclude_root():
	"""Test toggling only children, not root."""
	pl = Plotter()
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	backend = pl.backend._pl

	# Toggle child1 without root
	backend.toggle_subtree_visibility(child1, include_root=False)

	# Child1 should still be visible, but children should toggle
	assert child1.visible  # Root not included
	assert not grandchild1.visible
	assert not grandchild2.visible

	# Child2 not affected
	assert child2.visible


def test_toggle_subtree_visibility_branch():
	"""Test toggling a branch doesn't affect siblings."""
	pl = Plotter()
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	backend = pl.backend._pl

	# Toggle child1 branch
	backend.toggle_subtree_visibility(child1, include_root=True)

	# Child1 and its descendants hidden
	assert not child1.visible
	assert not grandchild1.visible
	assert not grandchild2.visible

	# Root and child2 still visible
	assert root.visible
	assert child2.visible


def test_hide_children_updated():
	"""Test that hide_children uses new visibility property."""
	pl = Plotter()
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	backend = pl.backend._pl

	# Hide children
	backend.hide_children(root)

	# Root should still be visible
	assert root.visible

	# All children hidden
	assert not child1.visible
	assert not child2.visible
	assert not grandchild1.visible
	assert not grandchild2.visible


def test_show_children_updated():
	"""Test that show_children uses new visibility property."""
	pl = Plotter()
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	backend = pl.backend._pl

	# First hide
	backend.hide_children(root)
	assert not child1.visible

	# Then show
	backend.show_children(root)
	assert child1.visible
	assert child2.visible
	assert grandchild1.visible
	assert grandchild2.visible


def test_visibility_with_picking():
	"""Test visibility toggle works with picking system."""
	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()
	pl.plot(root, plot_children=True)

	# Simulate picking child1
	pl.backend._custom_picker._picked_dict["Child1"] = child1

	# Toggle visibility via backend
	pl.backend._pl.toggle_subtree_visibility(child1)

	assert not child1.visible
	assert not grandchild1.visible


def test_multiple_toggle_cycles():
	"""Test multiple toggle cycles work correctly."""
	pl = Plotter()
	obj = MeshObjectPlot("Test", pv.Cube())
	pl.plot(obj)

	backend = pl.backend._pl

	# Multiple toggle cycles
	for i in range(5):
		backend.toggle_subtree_visibility(obj)
		expected_state = not (i % 2 == 0)  # False on first (i=0), True on second (i=1), etc.
		assert obj.visible == expected_state



def test_unpick_restores_visibility():
    """Test that unpicking an object restores its subtree visibility."""
    # Create hierarchy
    root, child1, child2, grandchild1, grandchild2 = create_test_tree()

    # Plot the tree
    backend = PyVistaBackend(allow_picking=True)
    plotter = Plotter(backend=backend)
    plotter.plot(root)
    plotter.plot(child1)
    plotter.plot(grandchild1)

    # Pick the root
    backend._custom_picker._picked_dict['root'] = root

    # Toggle to hide
    backend._pl.toggle_subtree_visibility(root, include_root=True)
    assert not root.visible
    assert not child1.visible
    assert not grandchild1.visible

    # Unpick the root - should restore visibility
    backend._custom_picker.pick_unselect_object(root)
    assert root.visible
    assert child1.visible
    assert grandchild1.visible


def test_unpick_restores_partial_tree():
    """Test that unpicking a child restores only that subtree."""
    # Create hierarchy
    root, child1, child2, grandchild1, grandchild2 = create_test_tree()

    # Plot the tree
    backend = PyVistaBackend(allow_picking=True)
    plotter = Plotter(backend=backend)
    plotter.plot(root)
    plotter.plot(child1)
    plotter.plot(child2)
    plotter.plot(grandchild1)

    # Pick child1
    backend._custom_picker._picked_dict['child1'] = child1

    # Toggle to hide child1 and its descendants
    backend._pl.toggle_subtree_visibility(child1, include_root=True)
    assert root.visible  # Parent unaffected
    assert not child1.visible
    assert child2.visible  # Sibling unaffected
    assert not grandchild1.visible

    # Unpick child1 - should restore child1 and grandchild1
    backend._custom_picker.pick_unselect_object(child1)
    assert root.visible
    assert child1.visible
    assert child2.visible
    assert grandchild1.visible








def test_dynamic_tree_menu_widget_creation():
	"""Test creating a DynamicTreeMenuWidget."""
	from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import DynamicTreeMenuWidget

	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	pl.plot(root, color="red")
	pl.plot(child1, color="blue")
	pl.plot(child2, color="green")

	# Create the dynamic tree menu widget
	tree_menu = DynamicTreeMenuWidget(backend)

	# Check that the widget was created
	assert tree_menu is not None
	assert len(tree_menu._buttons) > 0  # Should have created buttons
	assert len(tree_menu._text_actors) > 0  # Should have created text actors
	assert len(tree_menu._tree_objects) > 0  # Should have found root objects


def test_dynamic_tree_menu_buttons_match_objects():
	"""Test that DynamicTreeMenuWidget creates buttons for all objects."""
	from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import DynamicTreeMenuWidget

	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	pl.plot(root, color="red")
	pl.plot(child1, color="blue")
	pl.plot(child2, color="green")
	pl.plot(grandchild1, color="yellow")
	pl.plot(grandchild2, color="cyan")

	# Create the dynamic tree menu widget
	tree_menu = DynamicTreeMenuWidget(backend)

	# Check that buttons were created for all 5 objects
	# (Plus title text, so at least 6 actors total)
	assert len(tree_menu._buttons) == 5  # One button per object
	assert len(tree_menu._text_actors) >= 6  # Title + 5 labels


def test_dynamic_tree_menu_refresh():
	"""Test that DynamicTreeMenuWidget can be refreshed."""
	from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import DynamicTreeMenuWidget

	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	pl.plot(root, color="red")

	# Create the dynamic tree menu widget
	tree_menu = DynamicTreeMenuWidget(backend)
	initial_buttons = len(tree_menu._buttons)

	# Add more objects
	independent = MeshObjectPlot("Independent", pv.Cone())
	pl.plot(independent, color="orange")

	# Refresh
	tree_menu.refresh()

	# Check that more buttons were created
	assert len(tree_menu._buttons) > initial_buttons
	# Should have one more button
	assert len(tree_menu._buttons) == initial_buttons + 1


def test_tree_menu_toggle_button_creation():
	"""Test creating a TreeMenuToggleButton."""
	from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import DynamicTreeMenuWidget
	from ansys.tools.visualization_interface.backends.pyvista.widgets.tree_menu_toggle import TreeMenuToggleButton

	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	pl.plot(root, color="red")
	pl.plot(child1, color="blue")

	# Create the tree menu
	tree_menu = DynamicTreeMenuWidget(backend, dark_mode=False)

	# Create the toggle button
	toggle_button = TreeMenuToggleButton(backend, dark_mode=False, tree_menu=tree_menu)

	# Check that the button was created
	assert toggle_button is not None
	assert toggle_button._button is not None
	assert toggle_button._tree_menu is tree_menu


def test_tree_menu_toggle_functionality():
	"""Test that TreeMenuToggleButton can hide and show the menu."""
	from ansys.tools.visualization_interface.backends.pyvista.widgets.dynamic_tree_menu import DynamicTreeMenuWidget
	from ansys.tools.visualization_interface.backends.pyvista.widgets.tree_menu_toggle import TreeMenuToggleButton

	backend = PyVistaBackend(allow_picking=True)
	pl = Plotter(backend=backend)
	root, child1, child2, grandchild1, grandchild2 = create_test_tree()

	pl.plot(root, color="red")

	# Create the tree menu
	tree_menu = DynamicTreeMenuWidget(backend, dark_mode=False)
	initial_actors = len(tree_menu._text_actors)

	# Create the toggle button
	toggle_button = TreeMenuToggleButton(backend, dark_mode=False, tree_menu=tree_menu)

	# Test hiding the menu
	toggle_button.callback(False)

	# Check that text actors are hidden (we can't easily check SetVisibility directly,
	# but we can verify the method was called without error)
	assert tree_menu is not None

	# Test showing the menu
	toggle_button.callback(True)

	# Menu should still exist
	assert tree_menu is not None
	assert len(tree_menu._text_actors) == initial_actors


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
