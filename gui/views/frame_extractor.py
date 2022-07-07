import subprocess
from pathlib import Path
import sys
import numpy as np
import napari
from napari import layers
from magicgui import widgets

from gui.models import AppState
from gui.views.base import BaseNapariView


class MultiFrameExtractionControlsViewNapari(BaseNapariView):
    def __init__(self, model: AppState) -> None:
        self.model = model

        # Controls
        self.every_n_widget = widgets.SpinBox(name='Every N Frames', min=1, max=1000, value=30)
        self.n_clusters_widget = widgets.SpinBox(name='Make N Clusters', min=2, max=500, value=20)
        self.downsample_widget = widgets.SpinBox(name='Downsample Level (For Clustering)', min=1, max=50, value=3)
        
        self.run_button = widgets.PushButton(text="Extract Frames")
        self.run_button.clicked.connect(self.on_run_button_click)
        
        self.progress_bar = widgets.ProgressBar(name='Progress')
        
        self.export_frames_fileselector = widgets.FileEdit(label='Export Frames to Directory', mode='d')
        self.export_frames_fileselector.changed.connect(self.on_export_frames_button_change)
        self.export_frames_fileselector.visible = False  # Can't export frames if none are loaded.


        

        self.widget = widgets.Container(
            layout='vertical',
            widgets=[
                self.every_n_widget,
                self.n_clusters_widget,
                self.downsample_widget,
                self.run_button,
                self.progress_bar,
                self.export_frames_fileselector,
            ],
            labels=True,
        )

        # Image Viewer
        self.layer = layers.Image(data=np.zeros(shape=(1, 3, 3, 3), dtype=np.uint8), name='Extracted Frames')
        self.model.observe(self.on_model_selected_frames_change, ['selected_frames'])
        self.model.crop.observe(self.on_model_crop_change)
    
    def register_napari(self, viewer: napari.Viewer) -> None:
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='')

    # Run Button
    def on_run_button_click(self) -> None:
        workflow = self.model.extract_frames(
            n_clusters=self.n_clusters_widget.value, 
            every_n=self.every_n_widget.value,
            downsample_level=self.downsample_widget.value,
        )
        for step in workflow:
            self.progress_bar.max = step.max
            self.progress_bar.value = step.value
            self.progress_bar.label = step.description
        
    
    # Image Viewer
    def on_model_selected_frames_change(self, change) -> None:
        if self.layer not in self.viewer.layers:
            self.viewer.add_layer(self.layer)

        frames = self.model.get_cropped_selected_frames()
        self.export_frames_fileselector.visible = False if frames is None else True
        self.layer.data = frames


    def on_model_crop_change(self, change) -> None:
        frames = self.model.get_cropped_selected_frames()
        if frames is not None:
            self.layer.data = frames


    def on_export_frames_button_change(self, directory: Path):
        self.model.export_frames_to_directory(directory=directory)
        if 'win' in sys.platform:
            subprocess.call(f'explorer {str(directory)}')