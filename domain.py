from typing import List

import numpy as np
import cv2
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans


def downsample(frame: np.ndarray, level: float) -> np.ndarray:
    h, w, c = frame.shape
    new_frame = cv2.resize(frame, (w//level, h//level), fx=0, fy=0, interpolation=cv2.INTER_AREA)
    return new_frame


def pca(frames: np.ndarray) -> np.ndarray:
    flat_frames = frames.reshape(frames.shape[0], -1)
    do_pca = PCA(n_components=min(flat_frames.shape))
    component_frames = do_pca.fit_transform(flat_frames)
    return component_frames


def select_subset_frames_kmeans(frames: np.ndarray, n_clusters: int = 20) -> List[int]:
    """
    Returns indices of a subset of frames, selected via clustering using KMeans
    """

    flat_frames = frames.reshape(frames.shape[0], -1)
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, tol=1e-5, batch_size=100, max_iter=50, verbose=1)
    kmeans.fit(flat_frames)
    
    selected_frame_indices = []
    for cluster_id in np.unique(kmeans.labels_):
        frame_indices_in_cluster = np.where(cluster_id == kmeans.labels_)[0]
        idx = np.random.choice(frame_indices_in_cluster)
        selected_frame_indices.append(idx)

    return selected_frame_indices

