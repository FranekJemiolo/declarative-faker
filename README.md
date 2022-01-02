# Declarative Faker

Package to generate synthetic data using declarative description of the schema.

## Install

To install run `python setup.py install` or `pip install -e .`.

## Development

Install pre-commit checks by running `pre-commit install`.

## Tests

Run `pytest`

## Example

To generate fake data run:
```bash
gen_fake --schemas-dir example --out-dir out
# This should produce a directory named out with these files
ll out
# total 1024
# -rw-r--r--  1 franek  staff   306K Jan  5 15:09 schema.trades.csv
# -rw-r--r--  1 franek  staff   166K Jan  5 15:09 schema.trades_report.csv
# -rw-r--r--  1 franek  staff    32K Jan  5 15:09 schema.users.csv
```
