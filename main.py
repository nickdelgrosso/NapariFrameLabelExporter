from argparse import ArgumentParser
import napari
from yaml import parse
from gui.models import AppState
from gui.views import ViewNapari, MultiFrameExtractionControlsViewNapari, LabelingViewNapari


def main(debug=False):
    app = AppState()
    viewer = napari.Viewer()

    loader_view = ViewNapari(model=app)
    loader_view.register_napari(viewer=viewer)

    extract_view = MultiFrameExtractionControlsViewNapari(model=app)
    extract_view.register_napari(viewer=viewer)

    labeler_view = LabelingViewNapari(model=app)
    labeler_view.register_napari(viewer=viewer)

    if debug:
        app.load_video(filename=r"C:\Users\nickdg\Projects\WaspTracker\data\raw\jwasp0.avi")
        list(app.extract_frames(n_clusters=10, every_n=40, downsample_level=10))
        app.body_parts

    napari.run()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    main(debug=args.debug)