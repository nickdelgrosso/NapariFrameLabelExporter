from functools import partial
from operator import mod
from pathlib import Path
from graphviz import view

import numpy as np
import napari
from magicgui import magicgui, type_map, widgets
from magicgui.widgets._bases.widget import Widget as BaseWidget
from models import AppState


class ViewNapari:

    def __init__(self, model: AppState) -> None:
        self.model = model
        
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

    def register_napari(self, viewer: napari.Viewer) -> None:
        viewer.window.add_dock_widget(self.widget, name='')

    def show(self, run: bool = False):
        self.widget.show(run=run)

    def on_videopath_change(self):
        self.model.load_video(filename=self._videp_picker.value)
        self._crop_x0.visible = True
        self._crop_x1.visible = True
        self._crop_y0.visible = True
        self._crop_y1.visible = True


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

        






app = AppState()
view = ViewNapari(model=app)
view.show(run=True)

# viewer = napari.Viewer()
# view.register_napari(viewer=viewer)
# napari.run()





# @magicgui(auto_call=True)
# def crop_widget(x0: int, x1: int, y0: int, y1: int):
#     # Update View based on App
#     crop = app.crop
#     crop_widget.x0.max = crop.x_max
#     crop.x0 = x0
#     crop_widget.x0.value = crop.x0

#     crop_widget.x1.max  = crop.x_max
#     crop.x1 = x1
#     crop_widget.x1.value = crop.x1
    
#     crop_widget.y0.max = crop.y_max
#     crop.y0 = y0
#     crop_widget.y0.value = crop.y0
    
#     crop_widget.y1.max  = crop.y_max
#     crop.y1 = y1
#     crop_widget.y1.value = crop.y1



# class ReferenceImageViewNapari:

#     def __init__(self) -> None:
#         viewer = napari.current_viewer()
#         self.layer = viewer.add_image(data=np.zeros((3,3, 3), dtype=np.uint8), name='Reference Frame')

#     def __call__(self, change):
#         print('calling')
#         if app.reference_frame is not None:
#             self.layer.data = app.get_cropped_reference_frame()




# if __name__ == '__main__':
#     viewer = napari.Viewer()
#     widget_container = Container(
#         layout='vertical', 
#         widgets=[video_path, crop_widget],
#         labels=False,
#     )
#     viewer.window.add_dock_widget(widget_container, name='Try2')

#     ref_view = ReferenceImageViewNapari()
#     app.crop.observe(ref_view)
    

#     napari.run()