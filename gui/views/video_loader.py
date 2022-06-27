import numpy as np
import napari
from napari import layers
from magicgui import widgets

from gui.models import AppState
from gui.views.base import BaseNapariView


class ViewNapari(BaseNapariView):

    def __init__(self, model: AppState) -> None:
        self.model = model

        # Controls
        self._videp_picker = widgets.FileEdit(label='Select Video:')
        self._videp_picker.changed.connect(self.on_videopath_change)

        self._crop_x0 =  widgets.IntSlider(label='Crop X Min', max=10)
        self._crop_x0.changed.connect(self.on_crop_x0_change)
        self.model.crop.observe(self.on_model_crop_x0_change, 'x0')
        self._crop_x0.visible = False

        
        self._crop_x1 =  widgets.IntSlider(label='Crop X Max', max=10)
        self._crop_x1.changed.connect(self.on_crop_x1_change)
        self.model.crop.observe(self.on_model_crop_x1_change, 'x1')
        self._crop_x1.visible = False

        self._crop_y0 =  widgets.IntSlider(label='Crop Y Min', max=10)
        self._crop_y0.changed.connect(self.on_crop_y0_change)
        self.model.crop.observe(self.on_model_crop_y0_change, 'y0')
        self._crop_y0.visible = False

        self._crop_y1 =  widgets.IntSlider(label='Crop Y Max', max=10)
        self._crop_y1.changed.connect(self.on_crop_y1_change)
        self.model.crop.observe(self.on_model_crop_y1_change, 'y1')
        self._crop_y1.visible = False

        self.widget = widgets.Container(
            layout='vertical',
            widgets=[self._videp_picker, self._crop_x0, self._crop_x1, self._crop_y0, self._crop_y1],
            labels=True,
        )

        # Image Viewer
        self.layer = layers.Image(data=np.zeros(shape=(3, 3, 3), dtype=np.uint8), name='Reference Image')
        self.model.observe(self.on_model_cropped_refframe_change, ['reference_frame'])
        self.model.crop.observe(self.on_model_cropped_refframe_change)


    def register_napari(self, viewer: napari.Viewer) -> None:
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='Video Loader')

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

    