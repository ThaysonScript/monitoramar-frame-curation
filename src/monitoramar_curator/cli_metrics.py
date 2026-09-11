import argparse
import json
from pathlib import Path

import pandas as pd

from .metrics import compute_dataset_metrics, format_report


def main():
    p = argparse.ArgumentParser(description="Relatório de qualidade de um dataset curado (sem treino).")
    p.add_argument("--dataset", required=True, help="Diretório de saída produzido por monitoramar-curate")
    p.add_argument("--minutes-per-frame", type=float, default=2.0,
                   help="Tempo médio estimado de anotação por frame, em minutos")
    p.add_argument("--json-out", default=None, help="Caminho opcional para salvar o relatório em JSON")
    args = p.parse_args()

    dataset_dir = Path(args.dataset)
    manifest_path = dataset_dir / "manifests" / "selections.csv"
    stats_path = dataset_dir / "manifests" / "dataset_stats.json"

    manifest = pd.read_csv(manifest_path) if manifest_path.exists() else pd.DataFrame()
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}

    metrics = compute_dataset_metrics(manifest, stats, args.minutes_per_frame)
    print(format_report(metrics))

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
