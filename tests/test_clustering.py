import numpy as np
from monitoramar_curator.clustering import cluster_embeddings, representative_indices

def test_clusters():
    x = np.array([[1,0],[.99,.01],[0,1],[.01,.99]], dtype="float32")
    labels = cluster_embeddings(x, 2)
    assert len(set(labels)) == 2
    assert len(representative_indices(x, labels)) == 2
