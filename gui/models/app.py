from pathlib import Path
from typing import Any, Iterable, Optional, Union

import numpy as np
import pandas as pd
from traitlets import HasTraits, observe, validate, Instance, Tuple, List, Unicode, Dict, Int, All, TraitError
import typing as tp
from workflows import ExtractFramesResult, Progress, extract_frames, Crop
from readers import VideoReader
import cv2

from .utils import PrintableTraits, cycle_next_item, cycle_prev_item


# Model
        

class AppState(HasTraits, PrintableTraits):
    video_path = Unicode(allow_none=True)
    reference_frame = Instance(np.ndarray, allow_none=True)
    reference_frame_cropped = Instance(np.ndarray, allow_none=True)
    selected_frame_indices = List(Int())
    selected_frames = Instance(np.ndarray, allow_none=True)
    body_parts = List(Unicode(), default_value=[])
    current_body_part = Unicode(allow_none=True)
    labels = Instance(pd.DataFrame, default_value=pd.DataFrame())
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

        
    #### Commands ####
    def load_video(self, filename: str):
        video = VideoReader(filename=filename)
        average_frame = video.read_average_frame(nframes_to_use=10)
        self.video_path = str(filename)
        self.reference_frame = average_frame

    @observe('reference_frame')
    def default_crop_with_new_reference_frame(self, change):
        shape = self.reference_frame.shape
        with self.hold_trait_notifications():
            self.x0 = 0
            self.x1 = shape[1]
            self.x_max = shape[1]
            self.y0 = 0
            self.y1 = shape[0]
            self.y_max = shape[0]
        
    def update_labels(self, frame_indices: tp.List[int], points: tp.List[tp.Tuple[int, int]], labels: tp.List[str]):
        df = pd.DataFrame().assign(
            FrameIndex=np.array(frame_indices, dtype=int),
            i=np.array(points[:, 0], dtype=int),
            j=np.array(points[:, 1], dtype=int),
            label=np.array(labels, dtype=str),
        )
        self.labels = df


    def extract_frames(self, n_clusters: int, every_n: int, downsample_level: int) -> Iterable[Progress]:
        workflow = extract_frames(
            video_path=self.video_path,
            crop=Crop(x0=self.x0, x1=self.x1, y0=self.y0, y1=self.y1),
            every_n=every_n,
            n_clusters=n_clusters,
            downsample_level=downsample_level
        )
        for step in workflow:
            if isinstance(step, Progress):
                yield step
            else:
                assert isinstance(step, ExtractFramesResult)
                self.selected_frame_indices = [int(ind) for ind in step.extracted_frame_indices]
                self.selected_frames = step.extracted_frames


    def get_cropped_reference_frame(self) -> Optional[np.ndarray]:
        frame = self.reference_frame
        if frame is None:
            return
        frame = self.reference_frame[self.y0:self.y1, self.x0:self.x1]
        return frame

    def get_cropped_selected_frames(self) -> Optional[np.ndarray]:
        frames = self.selected_frames
        if frames is None:
            return None
        frames_cropped = frames[:, self.y0:self.y1, self.x0:self.x1]
        return frames_cropped

    def set_bodyparts(self, body_parts: tp.List[str]) -> None:
        self.body_parts = body_parts

    def add_bodyparts(self, body_parts: tp.List[str]) -> None:
        self.body_parts = list(set(self.body_parts + list(body_parts)))

    def remove_bodypart(self, body_part: str) -> None:
        if body_part in self.body_parts:
            self.body_parts = [part for part in self.body_parts if part != body_part]

    def cycle_next_bodypart(self) -> None:
        self.current_body_part = cycle_next_item(items=self.body_parts, item=self.current_body_part)

    def cycle_prev_bodypart(self) -> None:
        self.current_body_part = cycle_prev_item(items=self.body_parts, item=self.current_body_part)


    def export_frames_to_directory(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

        filename_template = Path(self.video_path).stem + "__{frame_idx}.png"
        for idx, frame in zip(self.selected_frame_indices, self.selected_frames):
            filename = filename_template.format(frame_idx=idx)
            full_filename = directory.joinpath(filename)
            cv2.imwrite(filename=str(full_filename), img=frame)
