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
    selection_reason: str = ""

    def to_dict(self):
        return asdict(self)


def add_reason(record, reason):
    """Inclui um motivo de seleção sem duplicá-lo no manifesto."""
    parts = [item for item in record.selection_reason.split(";") if item]
    if reason not in parts:
        parts.append(reason)
    record.selection_reason = ";".join(parts)
