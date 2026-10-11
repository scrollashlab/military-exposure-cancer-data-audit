# Military Exposure Cancer Data Audit

This repository holds the code and results behind "The Military Exposure Cancer Data Bridge," an entry by Ben Herman to the NCI Office of Data Sharing Impact Prize (Track 1, Ideas).

The audit measures how often military service and exposure information appears in public NCI metadata. It uses only open-access metadata and no controlled-access data.

## What it checks

1. **NCI Genomic Data Commons (GDC) public API:** the number of cases with exposure and occupation fields populated, the number coded "Agent Orange" or with an armed-forces occupation, the exposure dictionary's allowed values, and the four APOLLO projects.
2. **Index of NCI Studies (INS) public data files, release 2.4.1:** a keyword search of all dataset and cohort records for "Agent Orange," "burn pit," "Camp Lejeune," "airborne hazard," "military" and "veteran."

## Results (run 8 October 2026, GDC Data Release 46.0)

| Measure | Result |
|---|---|
| GDC cases, all projects | 50,571 |
| Cases with any chemical-exposure value | 60 |
| Cases coded "Agent Orange" | 2 |
| Cases with an armed-forces occupation | 11 |
| APOLLO cases (4 projects) with any occupation or exposure value | 0 of 232 |
| INS records mentioning Agent Orange, burn pits, Camp Lejeune or airborne hazards | 0 of 13,875 |
| INS records mentioning "military" or "veteran" | 11 distinct records |

Full output: `audit_results.json`.

## How to reproduce

You need Python 3. No other packages are required.

```
# GDC part only
python3 audit_gdc_ins.py > audit_results.json

# With the INS keyword search
curl -LO https://github.com/CBIIT/INS-Data/releases/download/2.4.1/ins_data_files_2.4.1.0.zip
unzip ins_data_files_2.4.1.0.zip -d ins
python3 audit_gdc_ins.py ins > audit_results.json
```

GDC counts change as new data releases are published, so later runs may differ slightly.

## License

CC0 1.0 Universal (public domain dedication).
