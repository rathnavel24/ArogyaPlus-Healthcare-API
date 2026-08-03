"""
One-off importer for the lab test/profile price list (TSV export).

Usage (from backend/app/):
    python -m app.seed.import_lab_catalog /path/to/tests_raw.tsv

Rows with Type "Test" become `Test` rows. Rows with Type "Profile" become
`Package` rows, best-effort linked to existing `Test` rows by matching names
found in the "Tests / Parameters Included" column. Safe to re-run: existing
rows are matched by `test_code` (falling back to `name`) and updated in place
rather than duplicated.
"""

import csv
import sys
from decimal import Decimal, InvalidOperation

from app.db.base import Base  # noqa: F401
from app.db.session import SessionLocal, engine
from app.models.package import Package
from app.models.test import Test

FIXED_COLUMNS = [
    "s_no",
    "type_",
    "process",
    "test_code",
    "name",
    "sample_type",
    "tat",
    "parameters_count",
    "b2b_price",
    "b2c_price",
    "mrp",
]

TUBE_TOKENS = {"serum", "edta", "urine", "fluoride", "plasma"}


def _clean(value: str) -> str | None:
    value = (value or "").strip()
    return value or None


def _decimal(value: str | None) -> Decimal | None:
    if not value:
        return None
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return None


def _int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(float(value.strip()))
    except ValueError:
        return None


def _parse_tail(type_: str, tail: list[str]) -> dict:
    tail = [c.strip() for c in tail]

    included_items = ""
    if type_ == "Profile" and tail:
        included_items = tail.pop(0)

    reason = ""
    if tail and tail[-1] and tail[-1].lower() not in TUBE_TOKENS:
        reason = tail.pop()

    tubes = [c for c in tail if c]
    tubes = (tubes + ["", "", "", ""])[:4]

    return {
        "included_items": included_items,
        "tube1": tubes[0],
        "tube2": tubes[1],
        "tube3": tubes[2],
        "tube4": tubes[3],
        "reason": reason,
    }


def read_rows(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)  # header
        for raw in reader:
            if not any(cell.strip() for cell in raw):
                continue
            fixed = (raw + [""] * len(FIXED_COLUMNS))[: len(FIXED_COLUMNS)]
            row = dict(zip(FIXED_COLUMNS, fixed))
            row.update(_parse_tail(row["type_"].strip(), raw[len(FIXED_COLUMNS) :]))
            rows.append(row)
    return rows


def upsert_test(db, row: dict) -> Test:
    name = _clean(row["name"])
    test_code = _clean(row["test_code"])
    price = _decimal(row["b2c_price"]) or Decimal("0")

    test = None
    if test_code:
        test = db.query(Test).filter(Test.test_code == test_code).first()
    if test is None:
        test = db.query(Test).filter(Test.name == name).first()
    if test is None:
        test = Test(name=name, lab_price=price, home_price=price)
        db.add(test)

    test.name = name
    test.description = _clean(row["reason"])
    test.sample_type = _clean(row["sample_type"]) or _clean(row["tube1"])
    test.tat = _clean(row["tat"])
    test.test_code = test_code
    test.b2b_price = _decimal(row["b2b_price"])
    test.mrp = _decimal(row["mrp"])
    test.parameters_count = _int(row["parameters_count"])
    test.tube1 = _clean(row["tube1"])
    test.tube2 = _clean(row["tube2"])
    test.tube3 = _clean(row["tube3"])
    test.tube4 = _clean(row["tube4"])
    test.included_items = _clean(row["included_items"])
    test.lab_price = price
    test.home_price = price
    db.flush()
    return test


def upsert_package(db, row: dict) -> Package:
    name = _clean(row["name"])
    test_code = _clean(row["test_code"])
    price = _decimal(row["b2c_price"]) or Decimal("0")

    package = None
    if test_code:
        package = db.query(Package).filter(Package.test_code == test_code).first()
    if package is None:
        package = db.query(Package).filter(Package.name == name).first()
    if package is None:
        package = Package(name=name, lab_price=price, home_price=price)
        db.add(package)

    package.name = name
    package.description = _clean(row["reason"])
    package.tat = _clean(row["tat"])
    package.test_code = test_code
    package.b2b_price = _decimal(row["b2b_price"])
    package.mrp = _decimal(row["mrp"])
    package.parameters_count = _int(row["parameters_count"])
    package.tube1 = _clean(row["tube1"])
    package.tube2 = _clean(row["tube2"])
    package.tube3 = _clean(row["tube3"])
    package.tube4 = _clean(row["tube4"])
    package.included_items = _clean(row["included_items"])
    package.lab_price = price
    package.home_price = price
    db.flush()
    return package


def link_package_tests(db, package: Package, included_items: str | None, tests_by_name: dict[str, Test]) -> int:
    if not included_items:
        return 0
    names = [n.strip() for n in included_items.replace("\n", ", ").split(",") if n.strip()]
    matched: list[Test] = []
    for raw_name in names:
        key = raw_name.lower()
        test = tests_by_name.get(key)
        if test is None:
            for candidate_name, candidate_test in tests_by_name.items():
                if key in candidate_name or candidate_name in key:
                    test = candidate_test
                    break
        if test is not None and test not in matched:
            matched.append(test)
    package.tests = matched
    return len(matched)


def run_import(path: str) -> None:
    Base.metadata.create_all(bind=engine)
    rows = read_rows(path)

    db = SessionLocal()
    try:
        test_rows = [r for r in rows if _clean(r["type_"]) == "Test"]
        profile_rows = [r for r in rows if _clean(r["type_"]) == "Profile"]

        print(f"Importing {len(test_rows)} tests...")
        for row in test_rows:
            upsert_test(db, row)
        db.flush()

        tests_by_name = {t.name.lower(): t for t in db.query(Test).all()}

        print(f"Importing {len(profile_rows)} profiles as packages...")
        total_links = 0
        for row in profile_rows:
            package = upsert_package(db, row)
            total_links += link_package_tests(db, package, row["included_items"], tests_by_name)

        db.commit()
        print(f"Done. {len(test_rows)} tests, {len(profile_rows)} packages, {total_links} package-test links.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m app.seed.import_lab_catalog /path/to/tests_raw.tsv")
        sys.exit(1)
    run_import(sys.argv[1])
