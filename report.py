import argparse
import csv
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Summarize deposit renewals by term.")
    parser.add_argument("input", type=Path)
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

    print("| Term (days) | Deposits | Renewals | Renewal rate |")
    print("| ---: | ---: | ---: | ---: |")
    for term, total in sorted(counts.items()):
        count = renewals[term]
        print(f"| {term} | {total} | {count} | {count / total:.0%} |")


if __name__ == "__main__":
    main()
