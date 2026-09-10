from pathlib import Path
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm
from .video import sample_video
from .models import FrameRecord
from .redundancy import TemporalRedundancyFilter
from .embeddings import create_backend
from .clustering import cluster_embeddings, representative_indices
from .task_aware import compute_event_scores, add_reason

def curate_video(video_path, output_dir, config):
    video_path, output_dir = Path(video_path), Path(output_dir)
    records, images = [], []
    red = TemporalRedundancyFilter(config["redundancy"]["threshold"])

    for idx, ts, frame in tqdm(sample_video(str(video_path), config["sampling"]["target_fps"]),
                                desc=f"Sampling {video_path.name}"):
        accepted, novelty = red.accept(frame)
        if accepted:
            records.append(FrameRecord(video_path.stem, str(video_path), idx, ts,
                                       redundancy_score=novelty, selection_reason="temporal_novelty"))
            images.append(frame)

    if not records:
        return []

    backend = create_backend(config["embedding"])
    emb = backend.encode(images)
    labels = cluster_embeddings(emb, config["clustering"]["n_clusters"],
                                 config["clustering"]["random_state"])
    for r, label in zip(records, labels):
        r.cluster_id = int(label)

    sim = emb @ emb.T
    np.fill_diagonal(sim, -1)
    novelty = np.clip(1 - np.max(sim, axis=1), 0, 1)
    for r, v in zip(records, novelty):
        r.embedding_novelty = float(v)

    if config["task_aware"]["enabled"]:
        compute_event_scores(records,
            config["task_aware"]["criticality"]["novelty"],
            config["task_aware"]["criticality"]["people_count_change"])

    reps = set(representative_indices(emb, labels))
    selected = set(reps)
    for i, r in enumerate(records):
        if config["selection"]["always_keep_events"] and r.event_score >= config["task_aware"]["min_event_score"]:
            selected.add(i)

    selected = sorted(selected, key=lambda i: records[i].frame_index)
    selected = selected[:config["selection"]["max_frames_per_video"]]

    frame_dir = output_dir / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for i in selected:
        r = records[i]
        add_reason(r, "cluster_representative" if i in reps else "critical_event")
        out = frame_dir / f"{r.video_id}_f{r.frame_index:08d}.jpg"
        cv2.imwrite(str(out), images[i], [cv2.IMWRITE_JPEG_QUALITY, config["output"]["jpeg_quality"]])
        r.output_path = str(out)

    return [records[i] for i in selected]

def run(input_dir, output_dir, config):
    videos = sorted(p for p in Path(input_dir).rglob("*")
                    if p.suffix.lower() in {".mp4",".avi",".mov",".mkv",".ts"})
    all_records = []
    for video in videos:
        try:
            all_records.extend(curate_video(video, output_dir, config))
        except Exception as exc:
            print(f"[ERROR] {video}: {exc}")
    out = Path(output_dir) / "manifests"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r.to_dict() for r in all_records]).to_csv(out / "selections.csv", index=False)
    return {"videos_processed": len(videos), "selected_frames": len(all_records),
            "manifest": str(out / "selections.csv")}
