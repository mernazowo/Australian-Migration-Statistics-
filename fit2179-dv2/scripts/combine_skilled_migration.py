#!/usr/bin/env python3
"""Combine skilled migration country datasets for 2024-25 map."""

import csv
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

# ISO 3166-1 numeric codes for world-110m.json (geographic join only).
ISO_NUMERIC = {
    "India": 356,
    "China": 156,
    "United Kingdom": 826,
    "Nepal": 524,
    "Pakistan": 586,
    "Philippines": 608,
    "Sri Lanka": 144,
    "Hong Kong": 344,
    "Ireland": 372,
    "Malaysia": 458,
    "Iran": 364,
    "Vietnam": 704,
    "South Africa": 710,
    "Brazil": 76,
    "Singapore": 702,
    "United States": 840,
    "Taiwan": 158,
    "Bangladesh": 50,
    "Israel": 376,
    "Russian Federation": 643,
    "Republic of Korea": 410,
    "Italy": 380,
    "Zimbabwe": 716,
    "Colombia": 170,
    "Bhutan": 64,
}


def read_wide_2024_25(path):
    totals = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Year"] != "2024–25":
                continue
            for key, value in row.items():
                if key in ("Year", "Other", "Total") or not value:
                    continue
                totals[key] = int(float(value))
    return totals


def read_country_visas(path):
    totals = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row["Country"].strip()
            totals[country] = int(float(row["Visas"]))
    return totals


def main():
    sources = {
        "employer_sponsored_countries.csv": read_wide_2024_25(
            DATA / "employer_sponsored_countries.csv"
        ),
        "state_nominated_countries.csv": read_wide_2024_25(
            DATA / "state_nominated_countries.csv"
        ),
        "skilled_independent_countries.csv": read_country_visas(
            DATA / "skilled_independent_countries.csv"
        ),
        "global_talent_countries.csv": read_country_visas(
            DATA / "global_talent_countries.csv"
        ),
    }

    combined = defaultdict(int)
    country_sources = defaultdict(set)

    for source_name, country_counts in sources.items():
        for country, count in country_counts.items():
            combined[country] += count
            country_sources[country].add(source_name)

    rows = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    combined_path = DATA / "skilled_migration_combined.csv"
    with combined_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Country", "Total_Visas"])
        writer.writerows(rows)

    map_path = DATA / "skilled_migration_map.csv"
    with map_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "country", "value"])
        for country, total in rows:
            iso_id = ISO_NUMERIC.get(country)
            if iso_id is not None:
                writer.writerow([iso_id, country, total])

    multi = [
        (country, sorted(names), combined[country])
        for country, names in country_sources.items()
        if len(names) > 1
    ]
    multi.sort(key=lambda x: x[2], reverse=True)

    print("Wrote", combined_path.name, f"({len(rows)} countries)")
    print("Wrote", map_path.name)
    print("\nTop 20 countries by Total_Visas:")
    for i, (country, total) in enumerate(rows[:20], 1):
        print(f"  {i:2}. {country}: {total:,}")

    print("\nCountries appearing in more than one dataset:")
    for country, names, total in multi:
        print(f"  {country} ({total:,}): {', '.join(names)}")


if __name__ == "__main__":
    main()
