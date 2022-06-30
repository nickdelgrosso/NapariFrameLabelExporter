from typing import Iterable, Optional

import numpy as np
import pandas as pd
from traitlets import HasTraits, observe, validate, Instance, Tuple, List, Unicode, Dict, Int, All, TraitError
import typing as tp
from workflows import ExtractFramesResult, Progress, extract_frames, Crop
from readers import VideoReader

from .utils import PrintableTraits
from .crop import CropState

# Model
        

class AppState(HasTraits, PrintableTraits):
    video_path = Unicode(allow_none=True)
    reference_frame = Instance(np.ndarray, allow_none=True)
    reference_frame_cropped = Instance(np.ndarray, allow_none=True)
    crop = CropState()
    selected_frame_indices = List(traits=Int())
    selected_frames = Instance(np.ndarray, allow_none=True)
    body_parts = List(Unicode(), default_value=['head'])
    current_body_part = Unicode(allow_none=True, default_value='head')

        
    #### Commands ####
    def load_video(self, filename: str):
        video = VideoReader(filename=filename)
        average_frame = video.read_average_frame(nframes_to_use=10)
        self.video_path = str(filename)
        self.reference_frame = average_frame

    @observe('reference_frame')
    def default_crop_with_new_reference_frame(self, change):
        shape = self.reference_frame.shape
        with self.crop.hold_trait_notifications():
            self.crop.x0 = 0
            self.crop.x1 = shape[1]
            self.crop.x_max = shape[1]
            self.crop.y0 = 0
            self.crop.y1 = shape[0]
            self.crop.y_max = shape[0]
        
    def update_labels(self, frame_indices: tp.List[int], points: tp.List[tp.Tuple[int, int]], labels: tp.List[str]):
        df = pd.DataFrame().assign(
            FrameIndex=np.array(frame_indices, dtype=int),
            i=np.array(points[:, 0], dtype=int),
            j=np.array(points[:, 1], dtype=int),
            label=np.array(labels, dtype=str),
        )
        print(df)
        self.labels = df

    def extract_frames(self, n_clusters: int, every_n: int, downsample_level: int) -> Iterable[Progress]:
        workflow = extract_frames(
            video_path=self.video_path,
            crop=Crop(x0=self.crop.x0, x1=self.crop.x1, y0=self.crop.y0, y1=self.crop.y1),
            every_n=every_n,
            n_clusters=n_clusters,
            downsample_level=downsample_level
        )
        for step in workflow:
            if isinstance(step, Progress):
                yield step
            else:
                assert isinstance(step, ExtractFramesResult)
                self.selected_frame_indices = step.extracted_frame_indices
                self.selected_frames = step.extracted_frames


    def get_cropped_reference_frame(self) -> Optional[np.ndarray]:
        crop = self.crop
        frame = self.reference_frame[crop.y0:crop.y1, crop.x0:crop.x1]
        return frame

    def get_cropped_selected_frames(self) -> Optional[np.ndarray]:
        frames = self.selected_frames
        if frames is None:
            return None
        crop = self.crop
        frames_cropped = frames[:, crop.y0:crop.y1, crop.x0:crop.x1]
        return frames_cropped


    def remove_bodypart(self, body_part: str):
        if body_part in self.body_parts:
            self.body_parts = [part for part in self.body_parts if part != body_part]
