
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union, Iterable

import numpy as np

from readers import VideoReader
from core.video_processing import downsample, select_subset_frames_kmeans, pca
from workflows.misc import Progress


@dataclass
class Crop:
    x0: int
    x1: int
    y0: int
    y1: int


@dataclass
class ExtractFramesResult:
    extracted_frame_indices: List[int]
    extracted_frames: np.ndarray




def extract_frames(video_path: Path, crop: Crop, n_clusters: int = 20, every_n: int = 30, downsample_level: int = 3) -> Iterable[Union[Progress, ExtractFramesResult]]:

    video = VideoReader(filename=video_path)

    
    yield Progress(value=0, max=2, description='Reading Frames from File...')
    frames = []
    for idx, frame in enumerate(video.read_frames(step=every_n)):
        frames.append(frame)
        yield Progress(value=idx, max=int(len(video) // every_n), description='Reading Frames from File...')


    yield Progress(value=0, max=len(frames), description='Downsampling Frames for Quicker Analysis...')
    frames_to_cluster = []
    for idx, frame in enumerate(frames):
        frame_cropped = frame[crop.y0:crop.y1, crop.x0:crop.x1]
        frame = downsample(frame_cropped, level=downsample_level)
        frames_to_cluster.append(frame)
        yield Progress(value=idx, max=len(frames), description='Downsampling Frames for Quicker Analysis...')
    

    # Extract only a Selection of Frames after clustering them using KMeans
    n_steps = 4
    yield Progress(value=1, max=n_steps, description="Packing Read frames into Array for Analysis....")
    frames_to_cluster = np.array(frames_to_cluster)
    yield Progress(value=2, max=n_steps, description="Selecting Frames (PCA)...")
    frame_components = pca(frames_to_cluster)
    yield Progress(value=3, max=n_steps, description="Selecting Frames (KMeans)...")
    selected_frame_indices = select_subset_frames_kmeans(frames=frame_components, n_clusters=n_clusters)
    yield Progress(value=4, max=n_steps, description="Done!")

    # Update model
    yield ExtractFramesResult(
        extracted_frame_indices = selected_frame_indices,
        extracted_frames = np.array([frames[idx] for idx in selected_frame_indices]),
    )
