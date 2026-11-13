import argparse
import csv
from collections import Counter
from pathlib import Path


def load_benchmark(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {
            int(row["term_days"]): int(row["renewed_count"]) / int(row["deposit_count"])
            for row in csv.DictReader(stream)
        }


def main():
    parser = argparse.ArgumentParser(description="Summarize deposit renewals by term.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--benchmark", type=Path, help="Compare rates with a separate benchmark snapshot.")
    args = parser.parse_args()

    counts = Counter()
    renewals = Counter()
    with args.input.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            term = int(row["term_days"])
            renewed = row["renewed"].strip().lower()
            if renewed not in {"yes", "no"}:
                raise ValueError(f"Expected 'yes' or 'no' for renewed, got {renewed!r}")
            counts[term] += 1
            renewals[term] += renewed == "yes"

    benchmarks = load_benchmark(args.benchmark) if args.benchmark else None
    header = "| Term (days) | Deposits | Renewals | Renewal rate |"
    separator = "| ---: | ---: | ---: | ---: |"
    if benchmarks is not None:
        header += " Benchmark | Difference (pp) |"
        separator += " ---: | ---: |"
    print(header)
    print(separator)
    for term, total in sorted(counts.items()):
        count = renewals[term]
        rate = count / total
        row = f"| {term} | {total} | {count} | {rate:.0%} |"
        if benchmarks is not None:
            benchmark = benchmarks.get(term)
            row += " — | — |" if benchmark is None else f" {benchmark:.1%} | {(rate - benchmark) * 100:+.1f} |"
        print(row)


if __name__ == "__main__":
    main()
