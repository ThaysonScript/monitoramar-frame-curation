"""Sinal task-aware de contagem de pessoas.

Usa o YOLOv8 apenas para *inferência* (o modelo já treinado e em produção
no MonitoraMAR), não para treino. O objetivo é preencher `people_count`
em cada FrameRecord, permitindo que `task_aware.compute_event_scores`
detecte mudanças reais na quantidade de banhistas -- o diferencial
descrito na proposta (curadoria orientada à tarefa, não apenas
dedup/diversidade visual genérica).

Se o `ultralytics` não estiver instalado, o pipeline continua funcionando
normalmente: `people_count` fica None e o event_score passa a depender
apenas da novidade de embedding (comportamento anterior).
"""
from abc import ABC, abstractmethod


class PeopleCounterBackend(ABC):
    @abstractmethod
    def count(self, images):
        """Retorna uma lista de int (ou None) com o nº de pessoas por frame."""
        raise NotImplementedError


class NullPeopleCounter(PeopleCounterBackend):
    def count(self, images):
        return [None] * len(images)


class YOLOv8PeopleCounter(PeopleCounterBackend):
    def __init__(self, model_name="yolov8n.pt", device="auto", conf=0.25, person_class=0):
        import torch
        from ultralytics import YOLO
        self.model = YOLO(model_name)
        self.device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
        self.conf = conf
        self.person_class = person_class

    def count(self, images):
        if not images:
            return []
        counts = []
        results = self.model.predict(
            images, device=self.device, conf=self.conf,
            classes=[self.person_class], verbose=False,
        )
        for r in results:
            counts.append(len(r.boxes) if r.boxes is not None else 0)
        return counts


def create_people_counter(config):
    """`config` é o sub-dicionário `task_aware.people_counting` do YAML."""
    config = config or {}
    if not config.get("enabled", False):
        return NullPeopleCounter()
    if config.get("backend", "yolov8") == "yolov8":
        try:
            return YOLOv8PeopleCounter(
                config.get("model", "yolov8n.pt"),
                config.get("device", "auto"),
                config.get("conf", 0.25),
                config.get("person_class", 0),
            )
        except Exception as exc:
            print(f"[WARN] YOLOv8 indisponível; contagem de pessoas desabilitada: {exc}")
    return NullPeopleCounter()
