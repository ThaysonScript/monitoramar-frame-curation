import argparse

from .review import build_review, serve_review


def main():
    parser = argparse.ArgumentParser(description="Gera uma página local para revisar frames curados.")
    parser.add_argument("--dataset", required=True, help="Diretório produzido por monitoramar-curate")
    parser.add_argument("--output", default=None, help="Pasta da revisão; padrão: <dataset>/review")
    parser.add_argument("--serve", action="store_true", help="Abre um servidor local com exclusão manual")
    parser.add_argument("--port", type=int, default=8765, help="Porta do servidor local")
    args = parser.parse_args()
    if args.serve:
        serve_review(args.dataset, port=args.port)
    else:
        print(build_review(args.dataset, args.output))


if __name__ == "__main__":
    main()
