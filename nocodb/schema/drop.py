"""Deletes from the base what was removed from schema_v1.py: reference values and fields.

apply.py never deletes, so a value or field taken out of schema_v1.py stays in the base. This script
deletes the entries listed below, each with the date and reason of the decision. Rerunnable: what is
already gone is skipped. It refuses to delete a value still linked to a record, or a field that
still holds data, unless the entry says why that data can go.

    python3 nocodb/schema/drop.py --dry-run
    python3 nocodb/schema/drop.py
"""
import argparse
import sys

from client import Client

# (table, libelle, why)
# Example: ("type_cible", "Some value", "YYYY-MM-DD: why it was removed from schema_v1.py"),
VALUES = []

# (table, field title, field type, why, data allowed to go: None or the reason). The type keeps a
# later field with the same title, but another type, from being deleted.
# Example: ("cas", "Some field", "SingleSelect", "YYYY-MM-DD: why it was removed", None),
FIELDS = []


def filled(value):
    return value not in (None, "", [], False)


def drop_values(c, ids):
    blocked = 0
    for table, libelle, why in VALUES:
        row = next((r for r in c.records(ids[table]) if r.get("libelle") == libelle), None)
        if row is None:
            print(f"  [skip] {table}.{libelle} already gone")
            continue
        links = [k for k, v in row.items() if not k.startswith("_nc") and isinstance(v, list) and v]
        if links:
            print(f"  [BLOCKED] {table}.{libelle} is still linked through {', '.join(links)}")
            blocked += 1
            continue
        c.write("DELETE", f"/api/v2/tables/{ids[table]}/records", {"Id": row["Id"]},
                f"delete {table}.{libelle} ({why})")
    return blocked


def drop_fields(c, ids):
    blocked = 0
    for table, title, type_, why, data_ok in FIELDS:
        col = next((col for col in c.columns(ids[table]) if col["title"] == title), None)
        if col is None:
            print(f"  [skip] {table}.{title} already gone")
            continue
        if col["uidt"] != type_:
            print(f"  [skip] {table}.{title} is now {col['uidt']}, not the dropped {type_}")
            continue
        n = sum(1 for r in c.records(ids[table]) if filled(r.get(title)))
        if n and not data_ok:
            print(f"  [BLOCKED] {table}.{title} still holds data in {n} record(s)")
            blocked += 1
            continue
        note = f"; {n} record(s) lose their value: {data_ok}" if n else ""
        c.write("DELETE", f"/api/v2/meta/columns/{col['id']}", None,
                f"delete field {table}.{title} ({why}{note})")
    return blocked


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    c = Client(p.parse_args().dry_run)
    print(f"{'DRY RUN' if c.dry_run else 'APPLY'} on {c.url}, base {c.base_id}")
    ids = c.tables()
    print("Values")
    blocked = drop_values(c, ids)
    print("Fields")
    blocked += drop_fields(c, ids)
    print(f"{c.actions} change(s) {'planned' if c.dry_run else 'applied'}.")
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
