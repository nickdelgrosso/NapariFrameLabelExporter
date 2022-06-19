from pathlib import Path

import napari
from magicgui import magicgui
from magicgui.tqdm import trange, tqdm
from magicgui.widgets._bases.value_widget import UNSET
import numpy as np
from kmeans import select_subset_frames_kmeans

from reader import VideoReader


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
    napari.current_viewer().add_image(average_frame, name="Reference Frame")



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

    # Read the Starting Frames to Analyze From the Video
    video = VideoReader(filename=video_path)
    frames = np.array(list(video.read_frames(step=every_n)))

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