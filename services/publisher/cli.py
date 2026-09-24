"""CLI de publicação explícita; sem publicar na importação."""

import argparse
import json
from .huggingface import publish


def main(argv=None):
    parser = argparse.ArgumentParser(description="Auditar e opcionalmente publicar um snapshot curado")
    parser.add_argument("snapshot")
    parser.add_argument("--approval", required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--publish", action="store_true", help="Efetua upload (padrão: só valida)")
    args = parser.parse_args(argv)
    client = None
    if args.publish:
        from huggingface_hub import HfApi
        client = HfApi()
    result = publish(args.snapshot, approval=args.approval, repo_id=args.repo_id,
                     client=client, dry_run=not args.publish)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
