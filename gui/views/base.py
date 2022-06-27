from abc import ABC, abstractmethod

import napari

from gui.models import AppState


class BaseNapariView(ABC):

    @abstractmethod
    def __init__(self, model: AppState) -> None:
        ...


    @abstractmethod
    def register_napari(self, viewer: napari.Viewer) -> None:
        ...