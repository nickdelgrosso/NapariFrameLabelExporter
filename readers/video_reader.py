from pathlib import Path
from typing import Iterator, Optional

import cv2
import numpy as np
from os import path


class VideoReader:

    def __init__(self, filename: Path) -> None:
        cap = cv2.VideoCapture(str(filename))
        if not cap.isOpened():
            raise IOError(f"Video File '{path.basename(filename)}' isn't opening with OpenCV. Not sure why; is it a video file?")
        
        self.cap = cap
    
    @property
    def n_frames(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __len__(self) -> int:
        return self.n_frames

    @property
    def frame_height(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    @property
    def frame_width(self) -> int:
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def seek_to(self, frame_idx) -> None:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

    def read_frame(self) -> np.ndarray:
        success, frame = self.cap.read()
        if not success:
            raise IOError("No Frame")
        frame = frame[..., ::-1]
        # frame = img_as_ubyte(frame)
        assert isinstance(frame, np.ndarray), f"Frame should be an array, instead is {type(frame)}"
        return frame

    def read_frames(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> Iterator[np.ndarray]:
        stop = len(self) if stop is None else stop
        for idx in range(start, stop, step):
            self.seek_to(idx)
            frame = self.read_frame()
            yield frame

    def read_average_frame(self, nframes_to_use: int = 10) -> np.ndarray:
        """Returns a roughly-estimated average frame from the data, using a subsample of evenly-spaced frames."""
        step_size = int(len(self) / nframes_to_use)
        frames = np.array(list(self.read_frames(step=step_size))).astype(int)
        average_frame = np.mean(frames, axis=0).astype(np.uint8)
        return average_frame
        
    