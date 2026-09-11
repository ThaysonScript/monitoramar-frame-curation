"""Métricas de qualidade do dataset produzido, sem depender de treinamento.

Escopo desta aplicação: produzir o dataset curado. O treinamento do
YOLO/U-Net com esse dataset é uma etapa posterior e separada. Por isso,
as métricas aqui medem propriedades do próprio dataset (redução de
volume, diversidade, cobertura de situações raras, custo estimado de
anotação) e não desempenho de modelo (mAP/mIoU), que pertence à fase
seguinte do projeto.
"""
import numpy as np


def _pct_reduction(base, kept):
    if not base:
        return None
    return round(100.0 * (1 - kept / base), 2)


def compute_dataset_metrics(manifest_df, stats, minutes_per_frame=2.0):
    """
    manifest_df: DataFrame de `selections.csv` (pode ser vazio/None).
    stats: dict carregado de `dataset_stats.json` (produzido pelo pipeline).
    minutes_per_frame: estimativa heurística de tempo médio de anotação por frame.
    """
    totals = (stats or {}).get("totals", {})
    raw = totals.get("raw_frame_count", 0) or 0
    sampled = totals.get("frames_sampled", 0) or 0
    candidates = totals.get("frames_after_redundancy", 0) or 0
    selected = len(manifest_df) if manifest_df is not None else int(totals.get("frames_selected", 0) or 0)

    metrics = {
        "raw_frames": raw,
        "frames_sampled": sampled,
        "frames_after_redundancy": candidates,
        "frames_selected": selected,
        "reduction_vs_raw_pct": _pct_reduction(raw, selected),
        "reduction_vs_sampled_pct": _pct_reduction(sampled, selected),
        "reduction_vs_candidates_pct": _pct_reduction(candidates, selected),
    }

    has_rows = manifest_df is not None and len(manifest_df) > 0

    # Diversidade: entropia normalizada da distribuição de cluster_id entre os selecionados.
    if has_rows and "cluster_id" in manifest_df.columns and manifest_df["cluster_id"].notna().any():
        counts = manifest_df["cluster_id"].dropna().value_counts().to_numpy(dtype=float)
        probs = counts / counts.sum()
        entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
        max_entropy = float(np.log(len(probs))) if len(probs) > 1 else None
        metrics["clusters_covered"] = len(probs)
        metrics["cluster_diversity_normalized"] = round(entropy / max_entropy, 3) if max_entropy else 1.0
    else:
        metrics["clusters_covered"] = None
        metrics["cluster_diversity_normalized"] = None

    # Cobertura de eventos críticos (task-aware).
    if has_rows and "selection_reason" in manifest_df.columns:
        reasons = manifest_df["selection_reason"].fillna("")
        critical = int(reasons.str.contains("critical_event").sum())
        metrics["critical_event_frames"] = critical
        metrics["critical_event_share_pct"] = round(100.0 * critical / len(manifest_df), 2)
    else:
        metrics["critical_event_frames"] = 0
        metrics["critical_event_share_pct"] = None

    # Cobertura de situações raras via contagem de pessoas (se o sinal YOLOv8 estiver ativo).
    if has_rows and "people_count" in manifest_df.columns and manifest_df["people_count"].notna().any():
        pc = manifest_df["people_count"].dropna()
        metrics["people_count_buckets_selected"] = int(pc.nunique())
    else:
        metrics["people_count_buckets_selected"] = None

    # Custo estimado de anotação (heurística, não depende de treino).
    metrics["estimated_annotation_hours_selected"] = round(selected * minutes_per_frame / 60.0, 2)
    metrics["estimated_annotation_hours_raw"] = round(raw * minutes_per_frame / 60.0, 2) if raw else None
    if metrics["estimated_annotation_hours_raw"] is not None:
        metrics["estimated_annotation_hours_saved"] = round(
            metrics["estimated_annotation_hours_raw"] - metrics["estimated_annotation_hours_selected"], 2)
    else:
        metrics["estimated_annotation_hours_saved"] = None

    return metrics


_REPORT_FIELDS = [
    ("raw_frames", "Frames brutos (vídeo original)"),
    ("frames_sampled", "Frames após amostragem temporal"),
    ("frames_after_redundancy", "Frames candidatos (pós-redundância)"),
    ("frames_selected", "Frames selecionados (dataset final)"),
    ("reduction_vs_raw_pct", "Redução vs. frames brutos (%)"),
    ("reduction_vs_sampled_pct", "Redução vs. amostrados (%)"),
    ("reduction_vs_candidates_pct", "Redução vs. candidatos (%)"),
    ("clusters_covered", "Clusters distintos cobertos"),
    ("cluster_diversity_normalized", "Diversidade normalizada de clusters (0-1)"),
    ("critical_event_frames", "Frames mantidos por evento crítico"),
    ("critical_event_share_pct", "Parcela de frames por evento crítico (%)"),
    ("people_count_buckets_selected", "Nº de contagens distintas de pessoas cobertas"),
    ("estimated_annotation_hours_raw", "Horas de anotação estimadas (bruto)"),
    ("estimated_annotation_hours_selected", "Horas de anotação estimadas (selecionado)"),
    ("estimated_annotation_hours_saved", "Horas de anotação economizadas (estimado)"),
]


def format_report(metrics):
    lines = ["=== Relatório de curadoria de dataset ==="]
    for key, label in _REPORT_FIELDS:
        lines.append(f"{label}: {metrics.get(key)}")
    return "\n".join(lines)
