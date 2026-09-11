import numpy as np
from monitoramar_curator.clustering import cluster_embeddings, representative_indices

def test_clusters():
    x = np.array([[1,0],[.99,.01],[0,1],[.01,.99]], dtype="float32")
    labels = cluster_embeddings(x, 2)
    assert len(set(labels)) == 2
    assert len(representative_indices(x, labels)) == 2

def test_representatives_per_cluster():
    x = np.array([[1,0],[.99,.01],[.98,.02],[0,1],[.01,.99]], dtype="float32")
    labels = cluster_embeddings(x, 2)
    reps_1 = representative_indices(x, labels, per_cluster=1)
    reps_2 = representative_indices(x, labels, per_cluster=2)
    assert len(reps_1) == 2
    assert len(reps_2) >= len(reps_1)
    # per_cluster maior que o tamanho do cluster não deve duplicar índices
    assert len(reps_2) == len(set(reps_2))
