import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

from .clustering import cluster_embeddings, representative_indices
from .embeddings import create_backend
from .models import FrameRecord, add_reason
from .redundancy import TemporalRedundancyFilter
from .video import get_video_info, sample_video


def _truncate_by_priority(candidate_idx, records, reps, max_frames):
    """Mantém a ordem cronológica quando cabe no orçamento. Quando é preciso
    cortar, prioriza representantes de cluster em vez de simplesmente cortar
    pela ordem do índice.
    Se não houver nenhum sinal de prioridade (ex.: métodos-baseline sem
    clustering), usa amostragem por passo uniforme em vez de
    manter só o início cronológico do vídeo.
    """
    ordered = sorted(candidate_idx, key=lambda i: records[i].frame_index)
    if len(ordered) <= max_frames:
        return ordered

    priorities = {i: 1.0 if i in reps else 0.0 for i in ordered}
    if len(set(priorities.values())) <= 1:
        stride = len(ordered) / max_frames
        picked = sorted({ordered[int(k * stride)] for k in range(max_frames)})
        return picked

    ranked = sorted(ordered, key=lambda i: (-priorities[i], records[i].frame_index))
    kept = ranked[:max_frames]
    return sorted(kept, key=lambda i: records[i].frame_index)


def curate_video(video_path, output_dir, config):
    video_path, output_dir = Path(video_path), Path(output_dir)
    records, images = [], []

    try:
        info = get_video_info(str(video_path))
        raw_frame_count, raw_fps, raw_duration = info.frame_count, info.fps, info.duration_seconds
    except Exception:
        raw_frame_count, raw_fps, raw_duration = 0, 0.0, 0.0

    redundancy_cfg = config.get("redundancy", {})
    redundancy_enabled = redundancy_cfg.get("enabled", True)
    red = TemporalRedundancyFilter(redundancy_cfg.get("threshold", 8))
    base_reason = "temporal_novelty" if redundancy_enabled else "sampled_fixed_interval"

    frames_sampled = 0
    for idx, ts, frame in tqdm(sample_video(str(video_path), config["sampling"]["target_fps"]),
                                desc=f"Sampling {video_path.name}"):
        frames_sampled += 1
        if redundancy_enabled:
            accepted, novelty = red.accept(frame)
        else:
            accepted, novelty = True, 1.0
        if accepted:
            records.append(FrameRecord(video_path.stem, str(video_path), idx, ts,
                                       redundancy_score=novelty, selection_reason=base_reason))
            images.append(frame)

    stats = {
        "video_id": video_path.stem,
        "raw_frame_count": raw_frame_count,
        "raw_fps": raw_fps,
        "raw_duration_seconds": raw_duration,
        "frames_sampled": frames_sampled,
        "frames_after_redundancy": len(records),
        "frames_selected": 0,
        "clusters_total": None,
    }

    if not records:
        return [], stats

    embedding_cfg = config.get("embedding", {})
    clustering_cfg = config.get("clustering", {})
    reps = set()
    if embedding_cfg.get("enabled", True) and clustering_cfg.get("enabled", True):
        backend = create_backend(embedding_cfg)
        emb = backend.encode(images)
        labels = cluster_embeddings(emb, clustering_cfg.get("n_clusters", 50),
                                     clustering_cfg.get("random_state", 42))
        for r, label in zip(records, labels):
            r.cluster_id = int(label)
        stats["clusters_total"] = len(set(labels.tolist()))

        sim = emb @ emb.T
        np.fill_diagonal(sim, -1)
        novelty = np.clip(1 - np.max(sim, axis=1), 0, 1)
        for r, v in zip(records, novelty):
            r.embedding_novelty = float(v)

        reps = set(representative_indices(
            emb, labels, config["selection"].get("representatives_per_cluster", 1)))

    selected = set(reps)

    if not selected:
        # Nenhum critério estruturado de seleção ativo (ex.: métodos-baseline
        # sem clustering nem task-aware): mantém tudo que sobrou da redundância.
        selected = set(range(len(records)))

    selected = _truncate_by_priority(selected, records, reps, config["selection"]["max_frames_per_video"])

    frame_dir = output_dir / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    for i in selected:
        r = records[i]
        if i in reps:
            add_reason(r, "cluster_representative")
        out = frame_dir / f"{r.video_id}_f{r.frame_index:08d}.jpg"
        cv2.imwrite(str(out), images[i], [cv2.IMWRITE_JPEG_QUALITY, config["output"]["jpeg_quality"]])
        r.output_path = str(out)

    stats["frames_selected"] = len(selected)
    return [records[i] for i in selected], stats


def run(input_dir, output_dir, config):
    videos = sorted(p for p in Path(input_dir).rglob("*")
                    if p.suffix.lower() in {".mp4", ".avi", ".mov", ".mkv", ".ts"})
    all_records, all_stats = [], []
    for video in videos:
        try:
            records, stats = curate_video(video, output_dir, config)
            all_records.extend(records)
            all_stats.append(stats)
        except Exception as exc:
            print(f"[ERROR] {video}: {exc}")

    out = Path(output_dir) / "manifests"
    out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r.to_dict() for r in all_records]).to_csv(out / "selections.csv", index=False)

    totals = {
        "raw_frame_count": sum(s["raw_frame_count"] for s in all_stats),
        "frames_sampled": sum(s["frames_sampled"] for s in all_stats),
        "frames_after_redundancy": sum(s["frames_after_redundancy"] for s in all_stats),
        "frames_selected": sum(s["frames_selected"] for s in all_stats),
    }
    dataset_stats = {"per_video": all_stats, "totals": totals}
    (out / "dataset_stats.json").write_text(
        json.dumps(dataset_stats, indent=2, ensure_ascii=False), encoding="utf-8")

    return {"videos_processed": len(videos), "selected_frames": len(all_records),
            "manifest": str(out / "selections.csv"), "stats": str(out / "dataset_stats.json")}
