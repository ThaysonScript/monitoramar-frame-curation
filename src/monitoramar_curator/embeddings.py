from abc import ABC, abstractmethod
import numpy as np

class EmbeddingBackend(ABC):
    @abstractmethod
    def encode(self, images):
        raise NotImplementedError

class ColorTextureEmbedding(EmbeddingBackend):
    def encode(self, images):
        import cv2
        out = []
        for image in images:
            hsv = cv2.cvtColor(cv2.resize(image, (64, 64)), cv2.COLOR_BGR2HSV)
            hs = [cv2.calcHist([hsv], [c], None, [32], [0, 180] if c == 0 else [0, 256]).flatten()
                  for c in range(3)]
            v = np.concatenate(hs).astype("float32")
            out.append(v / (np.linalg.norm(v) + 1e-8))
        return np.asarray(out)

class DINOv2Embedding(EmbeddingBackend):
    def __init__(self, model_name="dinov2_vits14", device="auto"):
        import torch
        import torchvision.transforms as T
        self.torch = torch
        self.device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
        self.model = torch.hub.load("facebookresearch/dinov2", model_name).eval().to(self.device)
        self.transform = T.Compose([
            T.ToPILImage(), T.Resize((224,224)), T.ToTensor(),
            T.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))
        ])

    def encode(self, images):
        batch = self.torch.stack([self.transform(img[:,:,::-1]) for img in images]).to(self.device)
        with self.torch.no_grad():
            x = self.model(batch)
        x = x / x.norm(dim=1, keepdim=True).clamp_min(1e-8)
        return x.cpu().numpy().astype("float32")

def create_backend(config):
    if config.get("backend") == "dinov2":
        try:
            return DINOv2Embedding(config.get("model","dinov2_vits14"), config.get("device","auto"))
        except Exception as exc:
            print(f"[WARN] DINOv2 indisponível; fallback: {exc}")
    return ColorTextureEmbedding()
