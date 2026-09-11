from dataclasses import asdict, dataclass


@dataclass
class FrameRecord:
    video_id: str
    source_path: str
    frame_index: int
    timestamp_seconds: float
    output_path: str = ""
    redundancy_score: float = 0.0
    embedding_novelty: float = 0.0
    cluster_id: int | None = None
    event_score: float = 0.0
    event_novelty_component: float = 0.0
    event_people_change_component: float = 0.0
    people_count_change: int | None = None
    people_count: int | None = None
    selection_reason: str = ""

    def to_dict(self):
        return asdict(self)
