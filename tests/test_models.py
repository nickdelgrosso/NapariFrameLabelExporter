
import numpy as np

from gui.models import AppState


def test_app_loads_reference_frame_when_video_path_updated():
    app = AppState()
    assert app.reference_frame is None
    app.load_video(filename=r"C:\Users\nickdg\Projects\WaspTracker\data\raw\jwasp0.avi")
    assert isinstance(app.reference_frame, np.ndarray)


def test_app_sets_crop_to_frame_dimensions_when_reference_frame_set():
    app = AppState()
    assert app.x1 is not 20
    app.reference_frame = np.empty((10, 20))
    assert app.x0 == 0
    assert app.x1 == 20
    assert app.x_max == 20
    assert app.y0 == 0
    assert app.y1 == 10
    assert app.y_max == 10
    
    
    # detector = Mock()
    # observe(detector)

    # app.observe('reference_frame')
