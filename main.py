from pathlib import Path
from types import SimpleNamespace

import napari
from magicgui import magicgui
from magicgui.tqdm import trange, tqdm
from magicgui.widgets._bases.value_widget import UNSET
import numpy as np
from kmeans import select_subset_frames_kmeans

from reader import VideoReader

reference_frame = None

@magicgui(
    video_path={"label": "Pick a Video File:"},
    call_button="Extract an Average Frame",
)
def reference_frame_extraction_widget(
    video_path: Path = Path(r"C:\Users\nickdg\Projects\WaspTracker\data\raw\jwasp0.avi"),
):
    # Calculate the reference frame (using average) from the video
    video = VideoReader(filename=video_path)
    average_frame = video.read_average_frame(nframes_to_use=10)

    # Finish: Send Average Frame to Napari Viewer
    global reference_frame
    reference_frame = average_frame
    viewer.add_image(average_frame, name="Reference Frame")



@magicgui(
    x0={'label': 'x0', 'widget_type': 'Slider'},
    x1={'label': 'x1', 'widget_type': 'Slider'},
    y0={'label': 'y0', 'widget_type': 'Slider'},
    y1={'label': 'y1', 'widget_type': 'Slider'},
    auto_call=True
)
def crop_frame_widget(
    x0=0,
    x1=1,
    y0=0,
    y1=1
):
    if 'Reference Frame' in viewer.layers:
        layer = viewer.layers['Reference Frame']
        layer.data = reference_frame[y0:y1, x0:x1]


@reference_frame_extraction_widget.called.connect
def set_max_ranges():
    """Once video is loaded, set the slider ranges to match the video's dimensions."""
    crop_frame_widget.x0.max = reference_frame.shape[1] - 1
    crop_frame_widget.x1.max = reference_frame.shape[1]
    crop_frame_widget.x0.value = 0
    crop_frame_widget.x1.value = reference_frame.shape[1]

    crop_frame_widget.y0.max = reference_frame.shape[0] - 1
    crop_frame_widget.y1.max = reference_frame.shape[0]
    crop_frame_widget.y0.value = 0
    crop_frame_widget.y1.value = reference_frame.shape[0]


@magicgui(
    video_path={"label": "Pick a Video File:"},
    every_n={"label": "Read Every N Frames"},
    n_clusters={"label": "N Clusters"},
    call_button="Extract Frames", 
)
def multiframe_extraction_widget(
    video_path: Path = Path(r"C:\Users\nickdg\Projects\WaspTracker\data\raw\jwasp0.avi"),
    every_n: int = 100,
    n_clusters: int = 50,
    # progress=5,
):

    # Read the Starting Frames to Analyze From the Video, cropping the frames to match the reference
    video = VideoReader(filename=video_path)
    frames = np.array(list(video.read_frames(step=every_n)))

    # Crop Frames to Match Reference Frame
    x0, x1 = crop_frame_widget.x0.value, crop_frame_widget.x1.value
    y0, y1 = crop_frame_widget.y0.value, crop_frame_widget.y1.value
    frames = frames[:, y0:y1, x0:x1]

    # Extract only a Selection of Frames after clustering them using KMeans
    selected_frame_indices = select_subset_frames_kmeans(frames=frames, n_clusters=n_clusters)
    selected_frames = frames[selected_frame_indices]

    # Finish: Send Data to Napari Viewer
    napari.current_viewer().add_image(selected_frames)

    


if __name__ == '__main__':
    viewer = napari.Viewer()
    viewer.window.add_dock_widget(reference_frame_extraction_widget, name="Reference Frame Extraction")
    viewer.window.add_dock_widget(crop_frame_widget, name="Crop Frame")
    viewer.window.add_dock_widget(multiframe_extraction_widget, name="K-Means Frame Extraction for Labeling")
    napari.run()