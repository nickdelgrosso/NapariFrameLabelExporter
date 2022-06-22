from functools import partial
from pathlib import Path
from graphviz import view

import numpy as np
import napari
from magicgui import magicgui, type_map
from magicgui.widgets import Container
from models import AppState

app = AppState()


type_map.register_type(int, widget_type='Slider')

@magicgui(auto_call=True)
def video_path(filename: Path):
    app.load_video(filename=filename)




@magicgui(auto_call=True)
def crop_widget(x0: int, x1: int, y0: int, y1: int):
    # Update View based on App
    crop = app.crop
    crop_widget.x0.max = crop.x_max
    crop.x0 = x0
    crop_widget.x0.value = crop.x0

    crop_widget.x1.max  = crop.x_max
    crop.x1 = x1
    crop_widget.x1.value = crop.x1
    
    crop_widget.y0.max = crop.y_max
    crop.y0 = y0
    crop_widget.y0.value = crop.y0
    
    crop_widget.y1.max  = crop.y_max
    crop.y1 = y1
    crop_widget.y1.value = crop.y1



class ReferenceImageViewNapari:

    def __init__(self) -> None:
        viewer = napari.current_viewer()
        self.layer = viewer.add_image(data=np.zeros((3,3, 3), dtype=np.uint8), name='Reference Frame')

    def __call__(self, change):
        print('calling')
        if app.reference_frame is not None:
            self.layer.data = app.get_cropped_reference_frame()




if __name__ == '__main__':
    viewer = napari.Viewer()
    widget_container = Container(
        layout='vertical', 
        widgets=[video_path, crop_widget],
        labels=False,
    )
    viewer.window.add_dock_widget(widget_container, name='Try2')

    ref_view = ReferenceImageViewNapari()
    app.crop.observe(ref_view)
    

    napari.run()