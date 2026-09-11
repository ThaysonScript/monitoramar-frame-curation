import argparse
from pathlib import Path

import yaml

from .compare import METHOD_OVERRIDES, run_comparison


def main():
    p = argparse.ArgumentParser(
        description="Compara as estratégias de curadoria (amostragem fixa, similaridade "
                    "temporal, diversidade visual, task-aware) sobre o mesmo conjunto de vídeos.")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True, help="Diretório raiz; cada método gera uma subpasta")
    p.add_argument("--config", required=True, help="Config base (será sobrescrito por método)")
    p.add_argument("--minutes-per-frame", type=float, default=2.0)
    p.add_argument("--methods", nargs="*", default=None, choices=list(METHOD_OVERRIDES.keys()),
                   help="Subconjunto de métodos a rodar (padrão: todos)")
    args = p.parse_args()

    base_config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    df, comparison_path = run_comparison(args.input, args.output, base_config,
                                          args.minutes_per_frame, args.methods)
    print(df.to_string())
    print(f"\nTabela comparativa salva em: {comparison_path}")


if __name__ == "__main__":
    main()
