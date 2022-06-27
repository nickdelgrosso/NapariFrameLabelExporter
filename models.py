from multiprocessing import allow_connection_pickling
from typing import Iterable, Optional

import numpy as np
from traitlets import HasTraits, observe, validate, Instance, Tuple, List, Unicode, Dict, Int, All, TraitError
from commands import ExtractFramesResult, Progress, extract_frames, Crop

from reader import VideoReader


class PrintableTraits:
    """Makes HasTrait instances pretty-print the trait values, to help with debugging."""

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{key}={val}' for key, val in self.trait_values().items())})"

# Model
class CropState(HasTraits, PrintableTraits):
    x0 = Int(default_value=0)
    x1 = Int(default_value=50)
    x_max = Int(default_value=100)
    y0 = Int(default_value=0)
    y1 = Int(default_value=60)
    y_max = Int(default_value=80)

    @validate('x0')
    def _check_x0(self, proposal):
        x0 = proposal['value']
        if x0 >= self.x1:
            return self.x0
        return x0

    @validate('x1')
    def _check_x1(self, proposal):
        x1 = proposal['value']
        if self.x0 >= x1:
            return self.x1
        return x1

    @validate('y0')
    def _check_y0(self, proposal):
        y0 = proposal['value']
        if y0 >= self.y1:
            return self.y0
        return y0

    @validate('y1')
    def _check_y1(self, proposal):
        y1 = proposal['value']
        if self.y0 >= y1:
            return self.y1
        return y1
        

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
        shape = average_frame.shape
        with self.crop.hold_trait_notifications():
            self.crop.x0 = 0
            self.crop.x1 = shape[1]
            self.crop.x_max = shape[1]
            self.crop.y0 = 0
            self.crop.y1 = shape[0]
            self.crop.y_max = shape[0]
        
    def extract_frames(self, n_clusters: int, every_n: int) -> Iterable[Progress]:
        workflow = extract_frames(
            video_path=self.video_path,
            crop=Crop(x0=self.crop.x0, x1=self.crop.x1, y0=self.crop.y0, y1=self.crop.y1),
            every_n=every_n,
            n_clusters=n_clusters,
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
