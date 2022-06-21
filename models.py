import numpy as np
from traitlets import HasTraits, observe, Instance, Tuple, List, Unicode, Dict, Int, All
import cv2

from kmeans import select_subset_frames_kmeans
from reader import VideoReader


class PrintableTraits:
    """Makes HasTrait instances pretty-print the trait values, to help with debugging."""

    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{key}={val}' for key, val in self.trait_values().items())})"

# Model
class Crop(HasTraits, PrintableTraits):
    x0 = Int(default_value=0)
    x1 = Int(default_value=50)
    x1_max = Int(default_value=100)
    y0 = Int(default_value=0)
    y1 = Int(default_value=60)
    y1_max = Int(default_value=80)

    @observe('x0')
    def restrict_xrange0(self, change):
        print(change)
        if self.x0 >= self.x1:
            self.x0 = change['old']
            
    @observe('x1')
    def restrict_xrange1(self, change):
        print(change)
        if self.x0 >= self.x1:
            self.x1 = change['old']
            
    @observe('y0')
    def restrict_yrange0(self, change):
        print(change)
        if self.y0 >= self.y1:
            self.y0 = change['old']
    
    @observe('y1')
    def restrict_yrange1(self, change):
        print(change)
        if self.y0 >= self.y1:
            self.y1 = change['old']


class AppState(HasTraits, PrintableTraits):
    video_path = Unicode(allow_none=True)
    reference_frame = Instance(np.ndarray, allow_none=True)
    crop = Instance(Crop, allow_none=True)
    selected_frames = Instance(np.ndarray, allow_none=True)
    body_parts = List(Unicode(), default_value=['head'])
    current_body_part = Unicode(allow_none=True, default='head')

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
        print(f'Setting crop to {self.crop}')


    #### Commands ####
    def set_crop(self, x0: int, x1: int, y0: int, y1: int):
        self.crop.x0 = x0
        self.crop.x1 = x1
        self.crop.y0 = y0
        self.crop.y1 = y1

    @observe('crop')
    def notify_crop_changed(self, changed):
        print('updated crop', changed)
        # self.notify_change('crop')

    def extract_frames_via_kmeans(self, every_n: int = 50, n_clusters: int = 15):
        # Read the Starting Frames to Analyze From the Video, cropping the frames to match the reference
        video = VideoReader(filename=self.video_path)
        frames = np.array(list(video.read_frames(step=every_n)))

        # Crop Frames to Match Reference Frame
        crop = self.crop
        frames = frames[:, crop.y0:crop.y1, crop.x0:crop.x1]

        # Extract only a Selection of Frames after clustering them using KMeans
        
        l, h, w, c = frames.shape
        frames_to_cluster = np.array([cv2.resize(frame, (w//3, h//3), fx=0, fy=0, interpolation=cv2.INTER_AREA) for frame in frames])
        frames_to_cluster = frames_to_cluster[:, :, :, 0]
        selected_frame_indices = select_subset_frames_kmeans(frames=frames_to_cluster, n_clusters=n_clusters)
        selected_frames = frames[selected_frame_indices]
        self.selected_frames = selected_frames

