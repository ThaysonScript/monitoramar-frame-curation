"""Comparação entre as estratégias de curadoria descritas na proposta:

A. Amostragem fixa       -- sem redundância e sem clustering.
B. Similaridade temporal -- redundância ativa, sem clustering.
C. Diversidade visual    -- redundância + embeddings + clustering.

Cada método é apenas uma combinação de flags de configuração; o pipeline
(`pipeline.run`) já sabe respeitar cada uma delas. Este módulo só monta
os três configs, roda o pipeline uma vez por método e agrega as
métricas de dataset (sem treino) definidas em `metrics.py`.
"""
import copy
import json
from pathlib import Path

import pandas as pd

from .metrics import compute_dataset_metrics
from .pipeline import run

METHOD_OVERRIDES = {
    "A_fixed_sampling": {
        "redundancy": {"enabled": False},
        "embedding": {"enabled": False},
        "clustering": {"enabled": False},
    },
    "B_temporal_similarity": {
        "redundancy": {"enabled": True},
        "embedding": {"enabled": False},
        "clustering": {"enabled": False},
    },
    "C_visual_diversity": {
        "redundancy": {"enabled": True},
        "embedding": {"enabled": True},
        "clustering": {"enabled": True},
    },
}


def _merge(base, override):
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = {**out[key], **value}
        else:
            out[key] = value
    return out


def run_comparison(input_dir, output_root, base_config, minutes_per_frame=2.0, methods=None):
    methods = methods or list(METHOD_OVERRIDES.keys())
    output_root = Path(output_root)
    rows = []
    for name in methods:
        cfg = _merge(base_config, METHOD_OVERRIDES[name])
        out_dir = output_root / name
        summary = run(input_dir, str(out_dir), cfg)

        manifest_path = Path(summary["manifest"])
        manifest = pd.read_csv(manifest_path) if manifest_path.exists() and summary["selected_frames"] else pd.DataFrame()

        stats_path = Path(summary["stats"])
        stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}

        row = compute_dataset_metrics(manifest, stats, minutes_per_frame)
        row["method"] = name
        rows.append(row)

    df = pd.DataFrame(rows).set_index("method")
    comparison_path = output_root / "comparison.csv"
    output_root.mkdir(parents=True, exist_ok=True)
    df.to_csv(comparison_path)
    return df, str(comparison_path)
