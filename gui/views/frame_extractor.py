import subprocess
from pathlib import Path
import sys
from typing import Optional
import numpy as np
import napari
from napari import layers
from magicgui import widgets

from gui.models import AppState
from gui.views.base import BaseNapariView
from gui.views.utils import match_items_atttributes_to_kwargs


class MultiFrameExtractionControlsViewNapari(BaseNapariView):
    def __init__(self, model: AppState) -> None:

        # Controls
        self.every_n_widget = widgets.SpinBox(name='Every N Frames', min=1, max=1000, value=30)
        self.n_clusters_widget = widgets.SpinBox(name='Make N Clusters', min=2, max=500, value=20)
        self.downsample_widget = widgets.SpinBox(name='Downsample Level (For Clustering)', min=1, max=50, value=3)
        
        self.run_button = widgets.PushButton(text="Extract Frames")
        
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


    def register_appmodel(self, model: AppState) -> None:
        model.observe(
            match_items_atttributes_to_kwargs(self.update, 'owner', frames='selected_frames'),
            names=['selected_frames', 'x0', 'x1', 'x_max', 'y0', 'y1', 'y_max'],
        )
    
        def on_run_button_click() -> None:
            workflow = model.extract_frames(
                n_clusters=self.n_clusters_widget.value, 
                every_n=self.every_n_widget.value,
                downsample_level=self.downsample_widget.value,
            )
            for step in workflow:
                self.progress_bar.max = step.max
                self.progress_bar.value = step.value
                self.progress_bar.label = step.description
        self.run_button.clicked.connect(on_run_button_click)


    def register_napari(self, viewer: napari.Viewer) -> None:
        self.viewer = viewer
        viewer.window.add_dock_widget(self.widget, name='')
        
    
    # Image Viewer
    def update(self, frames: Optional[np.ndarray]) -> None:
        if self.layer not in self.viewer.layers:
            self.viewer.add_layer(self.layer)

        if frames is None:
            self.export_frames_fileselector.visible = False
            return

        self.export_frames_fileselector.visible = True
        self.layer.data = frames


    def on_export_frames_button_change(self, directory: Path):
        self.model.export_frames_to_directory(directory=directory)
        if 'win' in sys.platform:
            subprocess.call(f'explorer {str(directory)}')