import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances


def cluster_embeddings(embeddings, n_clusters=50, random_state=42):
    if len(embeddings) == 0:
        return np.array([], dtype=int)
    k = min(max(1, n_clusters), len(embeddings))
    return KMeans(n_clusters=k, random_state=random_state, n_init="auto").fit_predict(embeddings)

def representative_indices(embeddings, labels, per_cluster=1):
    """Select up to `per_cluster` most central frames from each cluster.

    Centrality is measured as the mean cosine distance of a frame to every
    other frame in the same cluster (lower = more central/representative).
    """
    per_cluster = max(1, int(per_cluster))
    selected = []
    for cluster_id in sorted(set(labels.tolist())):
        idx = np.where(labels == cluster_id)[0]
        if len(idx) <= per_cluster:
            selected.extend(int(i) for i in idx)
            continue
        d = cosine_distances(embeddings[idx])
        centrality = d.mean(axis=1)
        order = np.argsort(centrality)[:per_cluster]
        selected.extend(int(idx[i]) for i in order)
    return selected
