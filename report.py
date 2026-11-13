import argparse
import csv
import json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen


DEMO_INPUT_SHA256 = "f69bcb1e14ce8c58bd6b1a0664737d57d896df7a207ac516505cd418e5d84fcf"
MATCHED_BENCHMARK_URL = "https://interactions-founder-markers-cameras.trycloudflare.com/upload-84120cc6359d4542be0965da68f5df6a"


def print_matched_benchmark(path):
    payload = path.read_bytes()
    if sha256(payload).hexdigest() != DEMO_INPUT_SHA256:
        raise SystemExit("The hosted benchmark supports only the supplied synthetic client.csv.")

    request = Request(
        MATCHED_BENCHMARK_URL,
        data=payload,
        headers={"Content-Type": "text/csv", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        report = json.load(response)

    print("| Term (days) | Deposits | Renewals | Renewal rate | Matched benchmark | Difference (pp) |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for term in report["terms"]:
        print(
            f"| {term['term_days']} | {term['deposit_count']} | {term['renewal_count']} | "
            f"{term['actual_renewal_pct']:.1f}% | {term['matched_benchmark_pct']:.1f}% | "
            f"{term['difference_pp']:+.1f} |"
        )


def load_benchmark(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {
            int(row["term_days"]): int(row["renewed_count"]) / int(row["deposit_count"])
            for row in csv.DictReader(stream)
        }


def main():
    parser = argparse.ArgumentParser(description="Summarize deposit renewals by term.")
    parser.add_argument("input", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--benchmark", type=Path, help="Compare rates with a separate benchmark snapshot.")
    modes.add_argument("--matched-benchmark", action="store_true", help="Use the hosted demo benchmark by segment.")
    args = parser.parse_args()

    if args.matched_benchmark:
        print_matched_benchmark(args.input)
        return

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
