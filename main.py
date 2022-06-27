import napari
from models import AppState

from gui import ViewNapari, MultiFrameExtractionControlsViewNapari, LabelingViewNapari


app = AppState()
viewer = napari.Viewer()

loader_view = ViewNapari(model=app)
loader_view.register_napari(viewer=viewer)

extract_view = MultiFrameExtractionControlsViewNapari(model=app)
extract_view.register_napari(viewer=viewer)

labeler_view = LabelingViewNapari(model=app)
labeler_view.register_napari(viewer=viewer)

napari.run()

