import numpy as np
from monitoramar_curator.redundancy import perceptual_hash, hamming_distance, TemporalRedundancyFilter

def test_identical_hash():
    x = np.zeros((100,100,3), dtype=np.uint8)
    h = perceptual_hash(x)
    assert hamming_distance(h,h) == 0

def test_first_frame():
    x = np.zeros((100,100,3), dtype=np.uint8)
    assert TemporalRedundancyFilter().accept(x)[0]
