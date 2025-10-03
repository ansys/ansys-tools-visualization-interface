# Copyright (C) 2024 - 2025 ANSYS, Inc. and/or its affiliates.
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
"""Provides `trame <https://kitware.github.io/trame/index.html>`_ visualizer interface for visualization."""

try:
    from pyvista.trame.ui import plotter_ui
    from trame.app import get_server

    _HAS_TRAME = True

except ModuleNotFoundError:  # pragma: no cover
    _HAS_TRAME = False

# Align Vue in client and server.
try:
    from trame.ui.vuetify import SinglePageWithDrawerLayout
    from trame.widgets import vuetify as v3
    CLIENT_TYPE = "vue2"
except ModuleNotFoundError:
    from trame.ui.vuetify3 import SinglePageWithDrawerLayout
    from trame.widgets import vuetify3 as v3
    CLIENT_TYPE = "vue3"


class TrameVisualizer:
    """Defines the trame layout view."""

    def __init__(self) -> None:
        """Initialize the trame server and server-related variables."""
        if not _HAS_TRAME:  # pragma: no cover
            raise ModuleNotFoundError(
                "The package 'pyvista[trame]' is required to use this function."
            )

        self.server = get_server(client_type=CLIENT_TYPE)
        self.state, self.ctrl = self.server.state, self.server.controller
        
        # Initialize state variables for toggles
        self.state.dark_background = False
        self.state.measure_active = False
        self.state.mesh_slider_active = False
        self.state.ruler_active = False
        
        # Store reference to plotter for controller methods
        self.plotter = None


    def set_scene(self, plotter):
        """Set the trame layout view and the mesh to show through the PyVista plotter.

        Parameters
        ----------
        plotter : ~pyvista.Plotter
            PyVista plotter with the rendered mesh.

        """
        self.plotter = plotter  # Store plotter reference (this is the actual PyVista plotter)
        self.state.trame__title = "PyAnsys Viewer"

        # Define controller methods for tools
        @self.ctrl.set("toggle_measure")
        def toggle_measure():
            if self.plotter:
                self.state.measure_active = not self.state.measure_active
                if not self.state.measure_active:
                    if hasattr(self, '_measure_widget') and self._measure_widget:
                        self._measure_widget.Off()
                        self.plotter.scene.clear_measure_widgets()
                else:
                    if self.state.dark_background:
                        self._measure_widget = self.plotter.scene.add_measurement_widget(color="white")
                    else:
                        self._measure_widget = self.plotter.scene.add_measurement_widget()
                self.ctrl.view_update()

        @self.ctrl.set("toggle_mesh_slider")
        def toggle_mesh_slider():
            if self.plotter:
                self.state.mesh_slider_active = not self.state.mesh_slider_active
                if not self.state.mesh_slider_active:
                    # Remove mesh slider
                    self.plotter.scene.clear_actors()
                    self.plotter.scene.clear_plane_widgets()
                    if hasattr(self, '_mesh_actor_list'):
                        for actor in self._mesh_actor_list:
                            self.plotter.scene.add_actor(actor)
                else:
                    # Add mesh slider
                    import pyvista as pv
                    self._mesh_actor_list = []
                    meshes = []
                    for actor in self.plotter.scene.actors.values():
                        if hasattr(actor, 'mapper') and hasattr(actor.mapper, "dataset"):
                            meshes.append(actor.mapper.dataset)
                    
                    if meshes:
                        mb = pv.MultiBlock(meshes).combine()
                        self._widget_actor = self.plotter.scene.add_mesh_clip_plane(mb)
                        
                        # Store original actors before removing them
                        for mesh in meshes:
                            if isinstance(mesh, pv.PolyData):
                                mesh_id = "PolyData(" + mesh.memory_address + ")"
                            elif isinstance(mesh, pv.UnstructuredGrid):
                                mesh_id = "UnstructuredGrid(" + mesh.memory_address + ")"
                            elif isinstance(mesh, pv.MultiBlock):
                                mesh_id = "MultiBlock(" + mesh.memory_address + ")"
                            elif isinstance(mesh, pv.StructuredGrid):
                                mesh_id = "StructuredGrid(" + mesh.memory_address + ")"
                            
                            if mesh_id in self.plotter.scene.actors:
                                self._mesh_actor_list.append(self.plotter.scene.actors[mesh_id])
                                self.plotter.scene.remove_actor(mesh_id)
                self.ctrl.view_update()

        @self.ctrl.set("toggle_ruler")
        def toggle_ruler():
            """Toggle ruler display."""
            try:
                self.state.ruler_active = not getattr(self.state, 'ruler_active', False)
                if not self.state.ruler_active:
                    # Remove ruler
                    if hasattr(self, '_ruler_actor') and self._ruler_actor:
                        self.plotter.scene.remove_actor(self._ruler_actor)
                        self._ruler_actor = None
                else:
                    # Add ruler
                    self._ruler_actor = self.plotter.scene.show_bounds(
                        grid="front",
                        location="outer",
                        all_edges=False,
                        show_xaxis=True,
                        show_yaxis=True,
                        show_zaxis=True,
                        color="white" if self.state.dark_background else "black",
                        xtitle="X Axis [m]",
                        ytitle="Y Axis [m]",
                        ztitle="Z Axis [m]",
                    )
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error toggling ruler: {e}")

        @self.ctrl.set("toggle_pick_rotation_center")
        def toggle_pick_rotation_center():
            """Toggle pick rotation center mode."""
            try:
                self.state.pick_rotation_center_active = not getattr(self.state, 'pick_rotation_center_active', False)
                if not self.state.pick_rotation_center_active:
                    # Disable pick rotation center mode
                    if hasattr(self, '_rotation_text_actor') and self._rotation_text_actor:
                        self._rotation_text_actor.SetVisibility(0)
                    # Re-enable default interaction
                    # Note: This is a simplified implementation
                else:
                    # Enable pick rotation center mode
                    self._rotation_text_actor = self.plotter.scene.add_text(
                        "Select a point to set the rotation center with right click",
                        position="upper_edge",
                        font_size=14,
                        color="grey",
                        shadow=True
                    )
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error toggling pick rotation center: {e}")

        @self.ctrl.set("toggle_dark_mode")
        def toggle_dark_mode():
            """Toggle dark mode."""
            try:
                self.state.dark_background = not self.state.dark_background
                if self.state.dark_background:
                    self.plotter.scene.set_background('black')
                else:
                    self.plotter.scene.set_background('white')
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error toggling dark mode: {e}")

        @self.ctrl.set("toggle_wireframe")
        def toggle_wireframe():
            if self.plotter:
                self.state.wireframe_mode = not self.state.wireframe_mode
                for actor in self.plotter.actors.values():
                    if hasattr(actor, 'prop'):
                        if self.state.wireframe_mode:
                            actor.prop.representation = 'wireframe'
                        else:
                            actor.prop.representation = 'surface'
                self.ctrl.view_update()

        @self.ctrl.set("toggle_edges")
        def toggle_edges():
            if self.plotter:
                self.state.show_edges = not self.state.show_edges
                for actor in self.plotter.actors.values():
                    if hasattr(actor, 'prop'):
                        actor.prop.edge_visibility = self.state.show_edges
                self.ctrl.view_update()

        @self.ctrl.set("toggle_point_mode")
        def toggle_point_mode():
            if self.plotter:
                self.state.point_mode = not self.state.point_mode
                for actor in self.plotter.actors.values():
                    if hasattr(actor, 'prop'):
                        if self.state.point_mode:
                            actor.prop.representation = 'points'
                        else:
                            actor.prop.representation = 'surface'
                self.ctrl.view_update()

        @self.ctrl.set("toggle_background")
        def toggle_background():
            if self.plotter:
                self.state.dark_background = not self.state.dark_background
                if self.state.dark_background:
                    self.plotter.scene.set_background('black')
                else:
                    self.plotter.scene.set_background('white')
                self.ctrl.view_update()

        @self.ctrl.set("toggle_axes")
        def toggle_axes():
            if self.plotter:
                self.state.show_axes = not self.state.show_axes
                if self.state.show_axes:
                    self.plotter.scene.show_axes()
                else:
                    self.plotter.scene.hide_axes()
                self.ctrl.view_update()

        @self.ctrl.set("toggle_local_rendering")
        def toggle_local_rendering():
            self.state.local_rendering = not self.state.local_rendering
            # The mode_local parameter should automatically sync with the state variable
            # Force a view update to apply the change
            self.ctrl.view_update()

        @self.ctrl.set("displace_camera_x_up")
        def displace_camera_x_up():
            """Move camera in X+ direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][0] -= 0.05 * self.plotter.scene.length
                current_camera_pos[1][0] -= 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera X+: {e}")

        @self.ctrl.set("displace_camera_x_down")
        def displace_camera_x_down():
            """Move camera in X- direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][0] += 0.05 * self.plotter.scene.length
                current_camera_pos[1][0] += 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera X-: {e}")

        @self.ctrl.set("displace_camera_y_up")
        def displace_camera_y_up():
            """Move camera in Y+ direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][1] -= 0.05 * self.plotter.scene.length
                current_camera_pos[1][1] -= 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera Y+: {e}")

        @self.ctrl.set("displace_camera_y_down")
        def displace_camera_y_down():
            """Move camera in Y- direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][1] += 0.05 * self.plotter.scene.length
                current_camera_pos[1][1] += 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera Y-: {e}")

        @self.ctrl.set("displace_camera_z_up")
        def displace_camera_z_up():
            """Move camera in Z+ direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][2] -= 0.05 * self.plotter.scene.length
                current_camera_pos[1][2] -= 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera Z+: {e}")

        @self.ctrl.set("displace_camera_z_down")
        def displace_camera_z_down():
            """Move camera in Z- direction."""
            try:
                current_camera_pos = list(map(list, self.plotter.scene.camera_position.to_list()))
                current_camera_pos[0][2] += 0.05 * self.plotter.scene.length
                current_camera_pos[1][2] += 0.05 * self.plotter.scene.length
                self.plotter.scene.set_position(current_camera_pos[0])
                self.plotter.scene.set_focus(current_camera_pos[1])
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error moving camera Z-: {e}")

        @self.ctrl.set("view_xy_plus")
        def view_xy_plus():
            """Set camera to XY+ view."""
            try:
                self.plotter.scene.view_xy()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting XY+ view: {e}")

        @self.ctrl.set("view_xy_minus") 
        def view_xy_minus():
            """Set camera to XY- view."""
            try:
                self.plotter.scene.view_yx()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting XY- view: {e}")

        @self.ctrl.set("view_xz_plus")
        def view_xz_plus():
            """Set camera to XZ+ view."""
            try:
                self.plotter.scene.view_xz()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting XZ+ view: {e}")

        @self.ctrl.set("view_xz_minus")
        def view_xz_minus():
            """Set camera to XZ- view."""
            try:
                self.plotter.scene.view_zx()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting XZ- view: {e}")

        @self.ctrl.set("view_yz_plus")
        def view_yz_plus():
            """Set camera to YZ+ view."""
            try:
                self.plotter.scene.view_yz()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting YZ+ view: {e}")

        @self.ctrl.set("view_yz_minus")
        def view_yz_minus():
            """Set camera to YZ- view."""
            try:
                self.plotter.scene.view_zy()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting YZ- view: {e}")

        @self.ctrl.set("view_isometric")
        def view_isometric():
            """Set camera to isometric view."""
            try:
                self.plotter.scene.view_isometric()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error setting isometric view: {e}")

        @self.ctrl.set("view_reset_camera")
        def view_reset_camera():
            """Reset camera view."""
            try:
                self.plotter.scene.reset_camera()
                self.ctrl.view_update()
            except Exception as e:
                print(f"Error resetting camera: {e}")

        with SinglePageWithDrawerLayout(self.server) as layout:
            layout.title.set_text("Ansys Visualization Tool")
            with layout.content:
                # Use PyVista UI template for plotters without built-in controls
                # Use mode parameter to control local vs remote rendering
                view = plotter_ui(
                    plotter.scene,
                    add_menu=False,
                    mode="trame"
                )
                self.ctrl.view_update = view.update
                
                # Store the view reference for local rendering updates
                self.view = view

            # Add buttons to side drawer/menu
            with layout.drawer:
                with v3.VList(shaped=True):                    
                    # Tools Section
                    with v3.VListGroup(value=("true",)):
                        with v3.Template(v_slot_activator=True):
                            with v3.VListItemContent():
                                v3.VListItemTitle("Tools")
                        
                        with v3.VListItem(click=self.ctrl.toggle_measure):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-ruler")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Measurement Tool")
                        
                        with v3.VListItem(click=self.ctrl.toggle_mesh_slider):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-content-cut")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Mesh Slicer")
                        
                        with v3.VListItem(click=self.ctrl.toggle_ruler):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-ruler")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Ruler")
                    
                    # Camera Movement Section
                    with v3.VListGroup(value=("true",)):
                        with v3.Template(v_slot_activator=True):
                            with v3.VListItemContent():
                                v3.VListItemTitle("Camera Movement")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_x_up):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-up-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move X+")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_x_down):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-down-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move X-")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_y_up):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-up-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move Y+")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_y_down):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-down-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move Y-")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_z_up):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-up-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move Z+")
                        
                        with v3.VListItem(click=self.ctrl.displace_camera_z_down):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-arrow-down-bold")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Move Z-")
                    
                    # Camera Views Section
                    with v3.VListGroup():
                        with v3.Template(v_slot_activator=True):
                            with v3.VListItemContent():
                                v3.VListItemTitle("Camera Views")
                        
                        with v3.VListItem(click=self.ctrl.view_xy_plus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("XY+ View")
                        
                        with v3.VListItem(click=self.ctrl.view_xy_minus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("XY- View")
                        
                        with v3.VListItem(click=self.ctrl.view_xz_plus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("XZ+ View")
                        
                        with v3.VListItem(click=self.ctrl.view_xz_minus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("XZ- View")
                        
                        with v3.VListItem(click=self.ctrl.view_yz_plus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("YZ+ View")
                        
                        with v3.VListItem(click=self.ctrl.view_yz_minus):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-axis-arrow")
                            with v3.VListItemContent():
                                v3.VListItemTitle("YZ- View")
                        
                        with v3.VListItem(click=self.ctrl.view_isometric):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-cube-outline")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Isometric View")
                    
                    # Display Controls Section
                    with v3.VListGroup():
                        with v3.Template(v_slot_activator=True):
                            with v3.VListItemContent():
                                v3.VListItemTitle("Display Options")
                        
                        with v3.VListItem(click=self.ctrl.toggle_dark_mode):
                            with v3.VListItemIcon():
                                v3.VIcon("mdi-theme-light-dark")
                            with v3.VListItemContent():
                                v3.VListItemTitle("Dark Mode")

            # Hide footer with trame watermark
            layout.footer.hide()

    def show(self):
        """Start the trame server and show the mesh."""
        self.server.start()
