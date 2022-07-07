from typing import Optional
import numpy as np
import napari
from napari import layers
from napari.utils.events import Event
from magicgui import widgets
import pandas as pd
from matplotlib.pyplot import colormaps

from gui.models import AppState
from gui.views.base import BaseNapariView


        
class LabelingViewNapari(BaseNapariView):

    def __init__(self, model: AppState) -> None:
        self.model = model

        # Add-bodypart widget (text box + submit button)
        self.add_bodypart_text_widget = widgets.LineEdit()
        self.add_bodypart_text_widget.changed.connect(self.on_bodypart_text_changed)
        
        # Select-Current-Bodypart widget
        self.current_bodypart_widget = widgets.ComboBox(choices=(), allow_multiple=False)
        self.current_bodypart_widget.changed.connect(self.on_current_bodypart_widget_selection_change)
        self.model.observe(self.on_model_bodyparts_change, ['body_parts', 'current_body_part'])

        # All widgets together
        self.widget = widgets.Container(
            layout='vertical',
            widgets=[
                self.add_bodypart_text_widget,
                self.current_bodypart_widget,
            ],
            labels=False,
        )

        # Labels Points Viewer
        self.point_layer = layers.Points(
            name='Body Part Labels', 
            ndim=3, 
            symbol='o', 
            size=12, 
            opacity=0.6,
            properties={'label': []},
            edge_width=0.2,
        )
        cmap = colormaps['Set1'].colors
        cmap = append_ones_column(cmap)
        self.edge_cmap = cmap
        self.model.observe(self.on_model_selected_frames_change, 'selected_frames') 
        self.point_layer.events.data.connect(self.on_pointlayer_data_event)
        self.model.observe(self.on_model_labels_change, 'labels')
        keyboard_shortcuts = {
            'S': self.cycle_next_bodypart,
            'W': self.cycle_previous_bodypart,
        }
        for key, fun in keyboard_shortcuts.items():
            self.point_layer.bind_key(key)(fun)
        self.point_layer.mode = 'ADD'

        # Interesting event types so far: 'highlight', 'mode', 'data'.

        # Potential event types:
        # ['refresh', 'set_data', 'blending', 'opacity', 'visible', 'scale', 'translate', 'rotate', 'shear', 'affine', 'data', 'name', 'thumbnail', 'status', 'help', 'interactive', 
        # 'cursor', 'cursor_size', 'editable', 'loaded', '_ndisplay', 'select', 'deselect', 'mode', 'size', 'edge_width', 'edge_width_is_relative', 'face_color', 
        # 'current_face_color', 'edge_color', 'current_edge_color', 'properties', 'current_properties', 'symbol', 'out_of_slice_display', 'n_dimensional', 'highlight', 
        # 'shading', '_antialias', 'experimental_canvas_size_limits', 'features', 'feature_defaults'])


    def register_napari(self, viewer: napari.Viewer):
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='Label Body Parts')
        

    # Add Bodypart button
    def on_bodypart_text_changed(self, text: str):
        body_parts = [s.strip() for s in text.split(';') if s.strip()]  if text else []
        self.model.set_bodyparts(body_parts=body_parts)

    # Select Current Bodypart Dropdown box
    def on_current_bodypart_widget_selection_change(self, value: str):
        self.model.current_body_part = value
        self.current_bodypart_widget.value = self.model.current_body_part
        self.point_layer.feature_defaults['label'] = self.model.current_body_part


    def on_model_bodyparts_change(self, change):
        self.current_bodypart_widget.choices = self.model.body_parts
        self.current_bodypart_widget.value = self.model.current_body_part

    # Points Layer View
    def on_pointlayer_data_event(self, event: Event):
        

        if not len(self.point_layer.data):
            return
        if self.model.body_parts:
            coords = self.point_layer.data[:, 1:3]
            frame_indices = self.point_layer.data[:, 0]
            self.model.update_labels(
                points=coords, 
                frame_indices=frame_indices,
                labels=self.point_layer.properties['label'],
            )
            self.cycle_next_bodypart()
        else:
            data = self.point_layer.data
            self.point_layer.data = np.empty(shape=(0, data.shape[1]), dtype=data.dtype)

    def on_model_labels_change(self, change):
        if not self.model.body_parts:
            return

        data = self.model.labels[['FrameIndex', 'i', 'j']].to_numpy()
        if not np.allclose(self.point_layer.data, data):
            self.point_layer.data = data
        self.point_layer.properties['label'] = self.model.labels['label']

        edge_color_map = {name: self.edge_cmap[idx] for idx, name in enumerate(self.model.body_parts)}
        edge_colors = np.array([edge_color_map[name] for name in self.model.labels['label']])
        self.point_layer.edge_color = edge_colors
        self.point_layer.face_color[:, -1] = 0  # make face transparent
        print(self.point_layer.edge_color)


    def on_model_selected_frames_change(self, change):
        if not self.point_layer.name in self.viewer.layers:
            self.viewer.add_layer(self.point_layer)
            layers = self.viewer.layers
            layers.move(layers.index(self.point_layer), -1)  # move the points layer to the end

    def cycle_next_bodypart(self, layer: Optional[layers.Points] = None):
        self.model.cycle_next_bodypart()

    def cycle_previous_bodypart(self, layer: Optional[layers.Points] = None):
        self.model.cycle_prev_bodypart()

def append_ones_column(mat: np.ndarray) -> np.ndarray:
    return np.hstack((
        mat, 
        np.ones(shape=(len(mat), 1)),
    ))
