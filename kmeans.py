from typing import List
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import MiniBatchKMeans


def select_subset_frames_kmeans(frames: np.ndarray, n_clusters: int = 20, do_pca=True) -> List[int]:
    """
    Returns indices of a subset of frames, selected via clustering using KMeans
    """

    flat_frames = frames.reshape(frames.shape[0], -1)

    if do_pca:
        print('starting pca')
        do_pca = PCA(n_components=500)
        component_frames = do_pca.fit_transform(flat_frames)

    kmeans = MiniBatchKMeans(n_clusters=n_clusters, tol=1e-5, batch_size=100, max_iter=50, verbose=1)
    kmeans.fit(component_frames)
    
    selected_frame_indices = []
    for cluster_id in np.unique(kmeans.labels_):
        frame_indices_in_cluster = np.where(cluster_id == kmeans.labels_)[0]
        idx = np.random.choice(frame_indices_in_cluster)
        selected_frame_indices.append(idx)

    return selected_frame_indices

