from pathlib import Path

import numpy as np
import napari
from magicgui import magicgui
from magicgui.tqdm import trange, _tqdm_kwargs
from traitlets import HasTraits, observe, Instance, Tuple, List, Unicode, Dict, Int
import traitlets

from kmeans import select_subset_frames_kmeans
from reader import VideoReader

# Model
class Crop(HasTraits):
    x0 = Int(default_value=0)
    x1 = Int()
    x1_max = Int()
    y0 = Int(default_value=0)
    y1 = Int()
    y1_max = Int()

    @observe('x0', 'x1')
    def restrict_xrange(self, changed):
        if self.x0 >= self.x1:
            if changed['name'] == 'x0':
                self.x0 = self.x1 - 2
            elif changed['name'] == 'x1':
                self.x1 = self.x0 + 2
            
    @observe('y0', 'y1')
    def restrict_yrange(self, changed):
        if self.y0 >= self.y1:
            print(changed)
            if changed['name'] == 'y0':
                self.y0 = self.y1 - 2
            elif changed['name'] == 'y1':
                self.y1 = self.y0 + 2


class AppState(HasTraits):
    video_path = Unicode(allow_none=True)
    reference_frame = Instance(np.ndarray, allow_none=True)
    crop = Instance(Crop, allow_none=True)

    @observe('video_path')
    def load_video(self, changed):
        # Calculate the reference frame (using average) from the video
        video = VideoReader(filename=self.video_path)
        average_frame = video.read_average_frame(nframes_to_use=10)
        self.reference_frame = average_frame


    @observe('reference_frame')
    def set_crop_range(self, changed):
        print('detected change in image')
        shape = self.reference_frame.shape
        self.crop = Crop(x0=0, x1=shape[1], x1_max=shape[1], y0=0, y1=shape[0], y1_max=shape[0])


model = AppState()


### Load Reference Frame
@magicgui(
    video_path={"label": "Pick a Video File:"},
    x0={'label': 'x0', 'widget_type': 'Slider'},
    x1={'label': 'x1', 'widget_type': 'Slider'},
    y0={'label': 'y0', 'widget_type': 'Slider'},
    y1={'label': 'y1', 'widget_type': 'Slider'},
    auto_call=True,
)
def reference_frame_extraction_widget(video_path: Path = None, x0=0, x1=1, y0=0, y1=1):
    model.video_path = str(video_path)
    model.crop = Crop(x0=x0, x1=x1, y0=y0, y1=y1)


# Update View from Model
@model.observe
def view_reference_frame(changed):
    viewer = napari.current_viewer()
    if changed['name'] == 'reference_frame':
        viewer.add_image(model.reference_frame, name="Reference Frame")
        reference_frame_extraction_widget.x0.max = model.crop.x1_max - 1
        reference_frame_extraction_widget.x1.max = model.crop.x1_max
        reference_frame_extraction_widget.y0.max = model.crop.y1_max - 1
        reference_frame_extraction_widget.y1.max = model.crop.y1_max
        crop = model.crop
        reference_frame_extraction_widget.x0.value = crop.x0
        reference_frame_extraction_widget.x1.value = crop.x1
        reference_frame_extraction_widget.y0.value = crop.y0
        reference_frame_extraction_widget.y1.value = crop.y1
    elif changed['name'] == 'crop' and 'Reference Frame' in viewer.layers:
        layer = viewer.layers['Reference Frame']
        crop = model.crop
        reference_frame_extraction_widget.x0.value = crop.x0
        reference_frame_extraction_widget.x1.value = crop.x1
        reference_frame_extraction_widget.y0.value = crop.y0
        reference_frame_extraction_widget.y1.value = crop.y1
        layer.data = model.reference_frame[crop.y0:crop.y1, crop.x0:crop.x1]


@magicgui(
    video_path={"label": "Pick a Video File:"},
    every_n={"label": "Read Every N Frames"},
    n_clusters={"label": "N Clusters"},
    call_button="Extract Frames", 
)
def multiframe_extraction_widget(
    video_path: Path = Path(r"C:\Users\nickdg\Projects\WaspTracker\data\raw\jwasp0.avi"),
    every_n: int = 200,
    n_clusters: int = 10,
    # progress=5,
):

    # Read the Starting Frames to Analyze From the Video, cropping the frames to match the reference
    video = VideoReader(filename=video_path)
    frames = np.array(list(video.read_frames(step=every_n)))

    # Crop Frames to Match Reference Frame
    x0, x1, y0, y1 = model.x0, model.x1, model.y0, model.y1
    frames = frames[:, y0:y1, x0:x1]

    # Extract only a Selection of Frames after clustering them using KMeans
    selected_frame_indices = select_subset_frames_kmeans(frames=frames, n_clusters=n_clusters)
    selected_frames = frames[selected_frame_indices]

    # Finish: Send Data to Napari Viewer
    napari.current_viewer().add_image(selected_frames)

    


if __name__ == '__main__':
    viewer = napari.Viewer()
    viewer.window.add_dock_widget(reference_frame_extraction_widget, name="Reference Frame Extraction")
    viewer.window.add_dock_widget(multiframe_extraction_widget, name="K-Means Frame Extraction for Labeling")
    napari.run()