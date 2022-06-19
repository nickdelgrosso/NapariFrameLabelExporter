from pathlib import Path

import napari
from magicgui import magicgui
from magicgui.tqdm import trange, tqdm
from magicgui.widgets._bases.value_widget import UNSET
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from kmeans import select_subset_frames_kmeans

from reader import VideoReader


@magicgui(
    video_path={"label": "Pick a Video File:"},
    every_n={"label": "Read Every N Frames"},
    n_clusters={"label": "N Clusters"},
    call_button="Extract Frames",
)
def widget_container(
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
    viewer.window.add_dock_widget(widget_container)
    napari.run()