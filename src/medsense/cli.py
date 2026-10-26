"""Local command-line entry points."""
import argparse
import json

from medsense.data.legacy_audit import audit_legacy_archive
from medsense.data.synthetic_generator import generate
from medsense.training.train_baselines import run


def main():
    parser = argparse.ArgumentParser(prog="medsense")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit-legacy", help="audit archived processed legacy rows")
    audit.add_argument("--archive", default="medical-wsd.zip")
    audit.add_argument("--output", default="outputs/legacy_audit")
    generator = sub.add_parser("generate-synthetic", help="generate the verified synthetic dataset")
    generator.add_argument("--config", default="configs/synthetic.yaml")
    baseline = sub.add_parser("train-baselines", help="fit/evaluate majority and TF-IDF baselines")
    baseline.add_argument("--config", default="configs/baseline.yaml")
    args = parser.parse_args()
    if args.command == "audit-legacy":
        result = audit_legacy_archive(args.archive, args.output)
    elif args.command == "generate-synthetic":
        examples, quality = generate(args.config)
        result = {"generated_examples": len(examples), "quality": quality}
    else:
        result = run(args.config)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
