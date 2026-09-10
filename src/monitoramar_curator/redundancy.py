import cv2
import numpy as np

def perceptual_hash(image, size=32):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(gray))
    block = dct[:8, :8]
    return (block > np.median(block[1:, 1:])).astype(np.uint8)

def hamming_distance(a, b):
    return int(np.count_nonzero(a != b))

class TemporalRedundancyFilter:
    def __init__(self, threshold=8):
        self.threshold = threshold
        self.previous_hash = None

    def accept(self, image):
        current = perceptual_hash(image)
        if self.previous_hash is None:
            self.previous_hash = current
            return True, 1.0
        distance = hamming_distance(current, self.previous_hash)
        self.previous_hash = current
        return distance >= self.threshold, distance / current.size
