import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_distances

def cluster_embeddings(embeddings, n_clusters=50, random_state=42):
    if len(embeddings) == 0:
        return np.array([], dtype=int)
    k = min(max(1, n_clusters), len(embeddings))
    return KMeans(n_clusters=k, random_state=random_state, n_init="auto").fit_predict(embeddings)

def representative_indices(embeddings, labels):
    selected = []
    for cluster_id in sorted(set(labels.tolist())):
        idx = np.where(labels == cluster_id)[0]
        if len(idx) == 1:
            selected.append(int(idx[0]))
        else:
            d = cosine_distances(embeddings[idx])
            selected.append(int(idx[np.argmin(d.mean(axis=1))]))
    return selected
