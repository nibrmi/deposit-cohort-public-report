# Deposit Cohort Lab

Search identifier: `cohort-renewal-public-lab-7e41`.

Generate a deposit-renewal report by term for the supplied synthetic `client.csv`. The November 2026 snapshot supports comparison weighted by the portfolio's micro, small, and medium business mix.

## Compare with the November peer benchmark

From the folder with the supplied sample, run:

```sh
python report.py client.csv --matched-benchmark
```

This mode uses the hosted benchmark service and prints the actual renewal rate, the matched benchmark, and the difference in percentage points for each term. It accepts only the supplied synthetic lab sample.

## Compare with the published aggregate benchmark

For an offline comparison, use the included [`benchmark.csv`](benchmark.csv), which contains one aggregate per term.

```sh
python report.py client.csv --benchmark benchmark.csv
```
