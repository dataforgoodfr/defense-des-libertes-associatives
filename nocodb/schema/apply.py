"""Bring a NocoDB base in line with schema_v1.py. Safe to rerun: what already matches is left alone.

Creates missing tables, fields, select options, links, computed fields and reference values; fixes accent or case
variants of existing values. It never deletes or retypes anything: mismatches are reported as DRIFT
and fixed by hand or by a migration script.

    python3 nocodb/schema/apply.py --dry-run   # print the plan, change nothing
    python3 nocodb/schema/apply.py             # apply it
"""
import argparse
import sys

from client import LINK_TYPES, SELECT_TYPES, ApiError, Client, norm
from schema_v1 import TABLES

PENDING = "(to be created)"


def field_body(f):
    body = {"title": f["title"], "column_name": f["column"], "uidt": f["type"]}
    if f["type"] in SELECT_TYPES:
        body["colOptions"] = {"options": [{"title": o} for o in f["options"]]}
    return body


def ensure_table(c, spec, ids):
    if spec["title"] in ids:
        return
    body = {"title": spec["title"], "table_name": spec["title"],
            "columns": [field_body(f) for f in spec["fields"]]}
    res = c.write("POST", f"/api/v2/meta/bases/{c.base_id}/tables", body,
                  f"create table {spec['title']} ({', '.join(f['title'] for f in spec['fields'])})")
    ids[spec["title"]] = res["id"] if res else PENDING


def ensure_options(c, table, col, wanted):
    current = col["colOptions"]["options"]
    by_key = {norm(o["title"]): o for o in current}
    options, changes = [], []
    for title in wanted:
        o = by_key.pop(norm(title), None)
        if o is None:
            options.append({"title": title})
            changes.append(f"+{title}")
        else:
            if o["title"] != title:
                changes.append(f"{o['title']} -> {title}")
            options.append({**o, "title": title})
    options += by_key.values()  # extra options are kept
    for o in by_key.values():
        print(f"  [info] {table}.{col['title']}: option '{o['title']}' is not in the spec, kept")
    if changes:
        body = {**col, "colOptions": {"options": options}}
        c.write("PATCH", f"/api/v2/meta/columns/{col['id']}", body,
                f"{table}.{col['title']}: options {', '.join(changes)}")


def ensure_fields(c, spec, tid):
    cols = {col["title"]: col for col in c.columns(tid)}
    for f in spec["fields"]:
        col = cols.get(f["title"])
        if col is None:
            c.write("POST", f"/api/v2/meta/tables/{tid}/columns", field_body(f),
                    f"add field {spec['title']}.{f['title']} ({f['type']})")
        elif col["uidt"] != f["type"]:
            print(f"  [DRIFT] {spec['title']}.{f['title']} is {col['uidt']}, spec says {f['type']}")
        elif f["type"] in SELECT_TYPES:
            ensure_options(c, spec["title"], col, f["options"])


def ensure_links(c, spec, ids):
    tid = ids[spec["title"]]
    cols = {} if tid == PENDING else {col["title"]: col for col in c.columns(tid)}
    for l in spec["links"]:
        target = ids.get(l["to"])
        col = cols.get(l["title"])
        if col is None:
            body = {"title": l["title"], "uidt": "LinkToAnotherRecord",
                    "parentId": tid, "childId": target, "type": l["type"]}
            c.write("POST", f"/api/v2/meta/tables/{tid}/columns", body,
                    f"add link {spec['title']}.{l['title']} -> {l['to']} [{l['type']}]")
            continue
        opts = col.get("colOptions") or {}
        if col["uidt"] not in LINK_TYPES or opts.get("fk_related_model_id") != target \
                or opts.get("type") != l["type"]:
            print(f"  [DRIFT] {spec['title']}.{l['title']}: found {col['uidt']} "
                  f"[{opts.get('type')}], spec says link -> {l['to']} [{l['type']}]")


def ensure_reverses(c, spec, ids):
    """Rename the fields NocoDB created on the linked tables to the link's or the table's `reverse` title."""
    tid = ids[spec["title"]]
    if not spec.get("reverse") or tid == PENDING:
        return
    cols = {col["title"]: col for col in c.columns(tid)}
    for l in spec["links"]:
        col = cols.get(l["title"])
        if col is not None and ids.get(l["to"]) not in (None, PENDING):
            ensure_reverse(c, l.get("reverse", spec["reverse"]), l, col.get("colOptions") or {}, ids[l["to"]])


def ensure_reverse(c, title, l, opts, target):
    for col in c.columns(target):
        o = col.get("colOptions") or {}
        if col["uidt"] in LINK_TYPES and col["id"] != opts.get("fk_column_id") \
                and o.get("fk_mm_model_id") == opts.get("fk_mm_model_id") \
                and o.get("fk_child_column_id") == opts.get("fk_parent_column_id") \
                and o.get("fk_parent_column_id") == opts.get("fk_child_column_id"):
            if col["title"] != title:
                c.write("PATCH", f"/api/v2/meta/columns/{col['id']}",
                        {"title": title, "column_name": title, "uidt": col["uidt"]},
                        f"rename reverse {l['to']}.{col['title']} -> {title}")
            return


def ensure_computed(c, spec, ids):
    """Create lookups and formulas; they need the links (and, for a formula, the fields) they read."""
    tid = ids[spec["title"]]
    if not spec.get("computed") or tid == PENDING:
        return
    cols = {col["title"]: col for col in c.columns(tid)}
    for f in spec["computed"]:
        col = cols.get(f["title"])
        if col is not None:
            if col["uidt"] != f["type"]:
                print(f"  [DRIFT] {spec['title']}.{f['title']} is {col['uidt']}, spec says {f['type']}")
            continue
        if f["type"] == "Lookup":
            via = cols.get(f["via"])
            target = next(l["to"] for l in spec["links"] if l["title"] == f["via"])
            if via is None or ids.get(target) in (None, PENDING):
                print(f"  [plan] add lookup {spec['title']}.{f['title']} once {f['via']} exists")
                continue
            field = next(col for col in c.columns(ids[target]) if col["title"] == f["field"])
            body = {"title": f["title"], "uidt": "Lookup",
                    "fk_relation_column_id": via["id"], "fk_lookup_column_id": field["id"]}
            desc = f"add lookup {spec['title']}.{f['title']} = {f['via']}.{f['field']}"
        else:
            body = {"title": f["title"], "uidt": "Formula", "formula_raw": f["formula"]}
            desc = f"add formula {spec['title']}.{f['title']} = {f['formula']}"
        res = c.write("POST", f"/api/v2/meta/tables/{tid}/columns", body, desc)
        if res is not None:
            cols = {col["title"]: col for col in c.columns(tid)}


def ensure_display(c, spec, tid):
    if tid == PENDING:
        return
    col = next((col for col in c.columns(tid) if col["title"] == spec["display"]), None)
    if col is None:
        print(f"  [plan] {spec['title']}: display value -> {spec['display']} once it exists")
    elif not col.get("pv"):
        c.write("POST", f"/api/v2/meta/columns/{col['id']}/primary", {},
                f"{spec['title']}: display value -> {spec['display']}")


def ensure_seeds(c, spec, tid):
    seeds = [s if isinstance(s, dict) else {spec["display"]: s} for s in spec.get("seeds", [])]
    if not seeds:
        return
    key = spec["display"]
    rows = {} if tid == PENDING else {norm(r.get(key)): r for r in c.records(tid)}
    inserts, updates = [], []
    for s in seeds:
        row = rows.pop(norm(s[key]), None)
        if row is None:
            inserts.append(s)
            continue
        diff = {k: v for k, v in s.items() if row.get(k) != v}
        if diff:
            updates.append({"Id": row["Id"], **diff})
    if inserts:
        c.write("POST", f"/api/v2/tables/{tid}/records", inserts,
                f"{spec['title']}: add {', '.join(s[key] for s in inserts)}")
    for u in updates:
        c.write("PATCH", f"/api/v2/tables/{tid}/records", [u],
                f"{spec['title']} #{u['Id']}: set {', '.join(f'{k}={v}' for k, v in u.items() if k != 'Id')}")
    for r in rows.values():
        print(f"  [info] {spec['title']}: value '{r.get(key)}' (#{r['Id']}) is not in the spec, kept")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print the plan without changing anything")
    args = parser.parse_args()
    c = Client(dry_run=args.dry_run)
    print(f"{'DRY RUN on' if c.dry_run else 'Applying to'} {c.url}, base {c.base_id}")

    try:
        ids = c.tables()
        print("Tables")
        for spec in TABLES:
            ensure_table(c, spec, ids)
        print("Fields")
        for spec in TABLES:
            if ids[spec["title"]] != PENDING:
                ensure_fields(c, spec, ids[spec["title"]])
        print("Links")
        for spec in TABLES:
            ensure_links(c, spec, ids)
        print("Reverse link names")
        for spec in TABLES:
            ensure_reverses(c, spec, ids)
        print("Computed fields")
        for spec in TABLES:
            ensure_computed(c, spec, ids)
        print("Display values")
        for spec in TABLES:
            ensure_display(c, spec, ids[spec["title"]])
        print("Reference values")
        for spec in TABLES:
            ensure_seeds(c, spec, ids[spec["title"]])
    except ApiError as e:
        print(f"\nSTOPPED on API error, nothing after this point was applied:\n  {e}")
        sys.exit(1)

    others = sorted(set(ids) - {s["title"] for s in TABLES})
    if others:
        print(f"Tables outside the spec, left untouched: {', '.join(others)}")
    print(f"{c.actions} change(s) {'planned' if c.dry_run else 'applied'}.")


if __name__ == "__main__":
    main()
