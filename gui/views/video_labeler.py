import numpy as np
import napari
from napari import layers
from napari.utils.events import Event
from magicgui import widgets
import pandas as pd

from gui.models import AppState
from gui.views.base import BaseNapariView

        
class LabelingViewNapari(BaseNapariView):

    def __init__(self, model: AppState) -> None:
        self.model = model

        # Add-bodypart widget (text box + submit button)
        self.add_bodypart_text_widget = widgets.LineEdit()
        self.add_bodypart_button = widgets.PushButton(text='Add')
        self.add_bodypart_button.clicked.connect(self.on_add_bodypart_button_clicked)

        self.add_bodypart_widget = widgets.Container(
            layout='horizontal',
            widgets=[
                self.add_bodypart_text_widget,
                self.add_bodypart_button,
            ],
            labels=False,
        )

        # Select-Current-Bodypart widget
        self.current_bodypart_widget = widgets.ComboBox(choices=(), allow_multiple=False)
        self.current_bodypart_widget.changed.connect(self.on_current_bodypart_widget_selection_change)
        self.model.observe(self.on_model_bodyparts_change)

        self.delete_current_bodypart_button = widgets.PushButton(text="Delete")
        self.delete_current_bodypart_button.clicked.connect(self.on_delete_current_bodypart_button_click)

        self.bodypart_selection_deletion_widget = widgets.Container(
            layout='horizontal',
            widgets=[
                self.current_bodypart_widget,
                self.delete_current_bodypart_button,
            ],
            labels=False
        )

        # All widgets together
        self.widget = widgets.Container(
            layout='vertical',
            widgets=[
                self.add_bodypart_widget,
                self.bodypart_selection_deletion_widget,
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
            # edge_color_
        )
        self.model.observe(self.on_model_selected_frames_change, 'selected_frames') 
        self.point_layer.events.data.connect(self.on_pointlayer_data_event)
        self.model.observe(self.on_model_labels_change, 'labels')
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
    def on_add_bodypart_button_clicked(self):
        text = self.add_bodypart_text_widget.value
        if text:
            body_parts = [s.strip() for s in text.split(';')]
            self.model.body_parts = body_parts
            self.add_bodypart_text_widget.value = ''  # clear textfield

    # Select Current Bodypart Dropdown box
    def on_current_bodypart_widget_selection_change(self, value: str):
        self.model.current_body_part = value
        self.current_bodypart_widget.value = self.model.current_body_part
        self.point_layer.feature_defaults['label'] = self.model.current_body_part


    def on_model_bodyparts_change(self, change):
        self.current_bodypart_widget.choices = self.model.body_parts
        
    # Delete Current Bodypart button
    def on_delete_current_bodypart_button_click(self):
        current = self.model.current_body_part
        self.model.remove_bodypart(body_part=current)

    # Points Layer View
    def on_pointlayer_data_event(self, event: Event):
        coords = self.point_layer.data[:, 1:3]
        frame_indices = self.point_layer.data[:, 0]

        self.model.update_labels(
            points=coords, 
            frame_indices=frame_indices,
            labels=self.point_layer.properties['label'],
        )

    def on_model_labels_change(self, change):
        self.point_layer.data = self.model.labels[['FrameIndex', 'i', 'j']]
        self.point_layer.properties['label'] = self.model.labels['label']


    def on_model_selected_frames_change(self, change):
        if not self.point_layer.name in self.viewer.layers:
            self.viewer.add_layer(self.point_layer)
            layers = self.viewer.layers
            layers.move(layers.index(self.point_layer), -1)  # move the points layer to the end

    