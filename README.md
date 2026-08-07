# Invoice OCR Record Cleaner

This project is a solution for the Junior Software Engineer home assignment.

The program takes raw OCR invoice records, normalizes valid values, detects duplicates, and separates the results into:

- Clean records
- Flagged records with reasons

## Files

- `invoice_processor.py` — code implementation
- `test_invoice_processor.py` — automated tests using Python's built-in `unittest`
- `thoughts.md` — assumptions, edge cases, and AI usage

## Requirements

Python 3.9 or newer.

No third-party packages are required.

## Run the program

```bash
python invoice_processor.py
```

## Run the tests

```bash
python -m unittest test_invoice_processor.py
```

Expected result:

```text
Ran 17 tests
OK
```

## Main function

```python
def process_records(
    raw_records: list[dict],
) -> tuple[list[dict], list[dict]]:
```

The first returned list contains clean records.

The second returned list contains flagged records. Each flagged record includes a `reason` field.
