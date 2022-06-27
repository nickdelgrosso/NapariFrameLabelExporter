from time import sleep
import numpy as np
import napari
from napari import layers
from magicgui import widgets

from models import AppState


class ViewNapari:

    def __init__(self, model: AppState) -> None:
        self.model = model

        # Controls
        self._videp_picker = widgets.FileEdit(label='Select Video:')
        self._videp_picker.changed.connect(self.on_videopath_change)

        self._crop_x0 =  widgets.IntSlider(label='x0', max=10)
        self._crop_x0.changed.connect(self.on_crop_x0_change)
        self.model.crop.observe(self.on_model_crop_x0_change, 'x0')
        self._crop_x0.visible = False

        
        self._crop_x1 =  widgets.IntSlider(label='x1', max=10)
        self._crop_x1.changed.connect(self.on_crop_x1_change)
        self.model.crop.observe(self.on_model_crop_x1_change, 'x1')
        self._crop_x1.visible = False

        self._crop_y0 =  widgets.IntSlider(label='y0', max=10)
        self._crop_y0.changed.connect(self.on_crop_y0_change)
        self.model.crop.observe(self.on_model_crop_y0_change, 'y0')
        self._crop_y0.visible = False

        self._crop_y1 =  widgets.IntSlider(label='y1', max=10)
        self._crop_y1.changed.connect(self.on_crop_y1_change)
        self.model.crop.observe(self.on_model_crop_y1_change, 'y1')
        self._crop_y1.visible = False

        self.widget = widgets.Container(
            layout='vertical',
            widgets=[self._videp_picker, self._crop_x0, self._crop_x1, self._crop_y0, self._crop_y1],
            labels=False,
        )

        # Image Viewer
        self.layer = layers.Image(data=np.zeros(shape=(3, 3, 3), dtype=np.uint8), name='Reference Image')
        self.model.observe(self.on_model_cropped_refframe_change, ['reference_frame'])
        self.model.crop.observe(self.on_model_cropped_refframe_change)


    def register_napari(self, viewer: napari.Viewer) -> None:
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='')

    def show(self, run: bool = False):
        self.widget.show(run=run)

    def on_videopath_change(self):
        self.model.load_video(filename=self._videp_picker.value)
        self._crop_x0.visible = True
        self._crop_x1.visible = True
        self._crop_y0.visible = True
        self._crop_y1.visible = True


    ###### Callbacks #######
    # Note: each widget has a pair of callbacks: 
    #   - one that updates the model from the widget (e.g. slider moving), 
    #   - and one that updates the widget when the model changes (e.g. model validation, image loading, etc)
    #  Though it is more code, By handling each direction independently, it's simpler to control how the app should behave and reduces debugging tmie 
    
    # x0
    def on_crop_x0_change(self):
        self.model.crop.x0 = self._crop_x0.value  # update model from view
        self._crop_x0.value = self.model.crop.x0  # update view again after model does validation (e.g. slider is not allowed to be there.)

    def on_model_crop_x0_change(self, change):
        self._crop_x0.max = self.model.crop.x_max
        self._crop_x0.value = change['new']
        
    # x1
    def on_crop_x1_change(self):
        self.model.crop.x1 = self._crop_x1.value
        self._crop_x1.value = self.model.crop.x1


    def on_model_crop_x1_change(self, change):
        self._crop_x1.max = self.model.crop.x_max
        self._crop_x1.value = change['new']

    # y0
    def on_crop_y0_change(self):
        self.model.crop.y0 = self._crop_y0.value
        self._crop_y0.value = self.model.crop.y0

    def on_model_crop_y0_change(self, change):
        self._crop_y0.max = self.model.crop.y_max
        self._crop_y0.value = self.model.crop.y0

    # y1
    def on_crop_y1_change(self):
        self.model.crop.y1 = self._crop_y1.value
        self._crop_y1.value = self.model.crop.y1

    def on_model_crop_y1_change(self, change):
        self._crop_y1.max = self.model.crop.y_max
        self._crop_y1.value = self.model.crop.y1

    # Image Viewer    
    def on_model_cropped_refframe_change(self, change) -> None:
        if self.layer not in self.viewer.layers and self.model.reference_frame is not None:
            self.viewer.add_layer(self.layer)
        self.layer.data = self.model.get_cropped_reference_frame()
        self.viewer.reset_view()

    

class MultiFrameExtractionControlsViewNapari:
    def __init__(self, model: AppState) -> None:
        self.model = model

        # Controls
        self.every_n_widget = widgets.SpinBox(min=1, max=1000, value=30)
        self.n_clusters_widget = widgets.SpinBox(min=2, max=500, value=20)
        self.run_button = widgets.PushButton(text="Extract Frames")
        self.progress_bar = widgets.ProgressBar(name='Progress')
        self.run_button.clicked.connect(self.on_run_button_click)

        

        self.widget = widgets.Container(
            layout='vertical',
            widgets=[
                self.every_n_widget,
                self.n_clusters_widget,
                self.run_button,
                self.progress_bar,
            ],
            labels=False,
        )

        # Image Viewer
        self.layer = layers.Image(data=np.zeros(shape=(1, 3, 3, 3), dtype=np.uint8), name='Extracted Frames')
        self.model.observe(self.on_model_selected_frames_change, ['selected_frames'])
        self.model.crop.observe(self.on_model_crop_change)
    
    def register_napari(self, viewer: napari.Viewer) -> None:
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='')

    # Run Button
    def on_run_button_click(self) -> None:
        workflow = self.model.extract_frames(n_clusters=self.n_clusters_widget.value, every_n=self.every_n_widget.value)
        for step in workflow:
            self.progress_bar.max = step.max
            self.progress_bar.value = step.value
        
    
    # Image Viewer
    def on_model_selected_frames_change(self, change) -> None:
        if self.layer not in self.viewer.layers:
            self.viewer.add_layer(self.layer)
        self.layer.data = self.model.get_cropped_selected_frames()

    def on_model_crop_change(self, change) -> None:
        frames = self.model.get_cropped_selected_frames()
        if frames is not None:
            self.layer.data = frames


        
class LabelingViewNapari:

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
        self.point_layer = layers.Points(ndim=3, symbol='o', size=12, name='Body Part Labels', opacity=0.6)
        self.model.observe(self.on_model_selected_frames_change, 'selected_frames')
        self.point_layer.events.data.connect(self.on_pointlayer_data_event)
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

    def on_model_bodyparts_change(self, change):
        self.current_bodypart_widget.choices = self.model.body_parts
        
    # Delete Current Bodypart button
    def on_delete_current_bodypart_button_click(self):
        current = self.model.current_body_part
        self.model.remove_bodypart(body_part=current)

    # Points Layer View
    def on_pointlayer_data_event(self, event):
        print(event, str(event))



    def on_model_selected_frames_change(self, change):
        if not self.point_layer.name in self.viewer.layers:
            self.viewer.add_layer(self.point_layer)
            layers = self.viewer.layers
            layers.move(layers.index(self.point_layer), -1)  # move the points layer to the end

    