import argparse

from .review import build_review


def main():
    parser = argparse.ArgumentParser(description="Gera uma página local para revisar frames curados.")
    parser.add_argument("--dataset", required=True, help="Diretório produzido por monitoramar-curate")
    parser.add_argument("--output", default=None, help="Pasta da revisão; padrão: <dataset>/review")
    args = parser.parse_args()
    print(build_review(args.dataset, args.output))


if __name__ == "__main__":
    main()
