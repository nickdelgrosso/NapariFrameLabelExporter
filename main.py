# import sys
# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#      color_scheme='Linux', call_pdb=1)

from enum import auto
from fileinput import filename
from pathlib import Path
from typing import Optional
from functools import partial


import napari
from magicgui import magicgui
from magicgui.widgets import Container
from magicgui.tqdm import trange
from magicgui.widgets import Select

from models import AppState

### Update Model from Widget
@magicgui(video_path={"label": "Pick a Video File:"}, auto_call=True)
def load_video_widget(video_path: Path = None):
    app.load_video(filename=video_path)


@magicgui(
    x0={'label': 'x0', 'widget_type': 'Slider'},
    x1={'label': 'x1', 'widget_type': 'Slider'},
    y0={'label': 'y0', 'widget_type': 'Slider'},
    y1={'label': 'y1', 'widget_type': 'Slider'},
    auto_call=True,
)
def reference_frame_extraction_widget(x0=0, x1=1, y0=0, y1=1):
    app.set_crop(x0=x0, x1=x1, y0=y0, y1=y1)



@magicgui(
    every_n={"label": "Read Every N Frames"},
    n_clusters={"label": "N Clusters"},
    call_button="Extract Frames", 
)
def multiframe_extraction_widget(
    every_n: int = 200,
    n_clusters: int = 10,
    # progress=5,
):
    app.extract_frames_via_kmeans(every_n=every_n, n_clusters=n_clusters)
            

    
# Update Widget from Model
app = AppState()


@partial(app.observe, names='reference_frame')
def view_reference_frame(changed):
    frame = changed['new']
    viewer = napari.current_viewer()
    viewer.add_image(frame, name="Reference Frame")
    


@partial(app.observe, names='crop')
def view_cropped_frame(changed):
    if 'Reference Frame' in viewer.layers:
        layer = viewer.layers['Reference Frame']
        crop = changed['new']
        layer.data = app.reference_frame[crop.y0:crop.y1, crop.x0:crop.x1]
        

@partial(app.observe, names=['crop'])
def view_reference_frame2(changed):        
    crop = changed['new']
    reference_frame_extraction_widget.x0.max = crop.x_max
    reference_frame_extraction_widget.x1.max = crop.x_max
    reference_frame_extraction_widget.y0.max = crop.y_max
    reference_frame_extraction_widget.y1.max = crop.y_max
    reference_frame_extraction_widget.x0.value = crop.x0
    reference_frame_extraction_widget.y1.value = crop.y1
    reference_frame_extraction_widget.x1.value = crop.x1
    reference_frame_extraction_widget.y0.value = crop.y0
    
    

@partial(app.observe, names='selected_frames')
def view_extracted_frames(changed):
    viewer = napari.current_viewer()
    viewer.add_image(app.selected_frames)
    

@partial(app.observe, names='body_parts')
def view_updated_bodypart_list(changed):
    add_bodypart_widget.body_part.value = ""
    bodypart_selector_widget.body_part.choices = app.body_parts


@magicgui(body_part = {'widget_type': 'LineEdit'}, layout='horizontal', call_button='Add')
def add_bodypart_widget(body_part: str = ""):
    if body_part:
        app.body_parts = app.body_parts + [s.strip() for s in body_part.split(';')]
    


@magicgui(body_part = {'label': "Current Body Part", 'widget_type': "ComboBox", 'choices': ('Place1', 'Place2')}, auto_call=True)
def bodypart_selector_widget(body_part: str = "Place1"):
    app.current_body_part = body_part


if __name__ == '__main__':
    viewer = napari.Viewer()
    widget_container = Container(
        layout='vertical', 
        widgets=[
            load_video_widget,
            reference_frame_extraction_widget, 
            multiframe_extraction_widget, 
            add_bodypart_widget, 
            bodypart_selector_widget
        ],
        labels=False,
    )
    viewer.window.add_dock_widget(widget_container, name='adfaf')
    napari.run()