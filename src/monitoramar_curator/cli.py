import argparse
from pathlib import Path
import yaml
from .pipeline import run

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--config", required=True)
    a = p.parse_args()
    config = yaml.safe_load(Path(a.config).read_text(encoding="utf-8"))
    print(run(a.input, a.output, config))

if __name__ == "__main__":
    main()
