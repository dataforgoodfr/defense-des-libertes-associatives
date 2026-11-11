"""Fill the `commune` table with every commune of France, so nobody types a commune by hand.

Source: the public API geo.api.gouv.fr (official geographic code, with the centre of each commune).
Only communes of the 18 regions of the `region` table are loaded; overseas collectivities outside
those regions (Polynésie française, Nouvelle-Calédonie...) are skipped and counted.

Rerunnable: communes are matched on their INSEE code; new ones are added, changed ones updated,
and each commune is linked to its region.

    python3 nocodb/schema/seed_communes.py --dry-run
    python3 nocodb/schema/seed_communes.py
"""
import argparse
import json
import subprocess
import sys

from client import ApiError, Client, norm

GEO_URL = "https://geo.api.gouv.fr/communes?fields=nom,code,departement,region,centre&format=json"
BATCH = 100  # NocoDB limit per request


def fetch_communes():
    out = subprocess.run(["curl", "-sf", GEO_URL], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def to_row(c):
    lon, lat = c["centre"]["coordinates"]
    return {"Nom": c["nom"], "Code INSEE": c["code"], "Département": c["departement"]["nom"],
            "latitude": lat, "longitude": lon}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print the plan without changing anything")
    args = parser.parse_args()
    c = Client(dry_run=args.dry_run)
    print(f"{'DRY RUN on' if c.dry_run else 'Applying to'} {c.url}, base {c.base_id}")

    ids = c.tables()
    regions = {norm(r["libelle"]): r["Id"] for r in c.records(ids["region"])}
    communes = fetch_communes()
    kept = [x for x in communes if norm(x.get("region", {}).get("nom")) in regions]
    print(f"{len(communes)} communes from geo.api.gouv.fr, {len(kept)} in the 18 regions, "
          f"{len(communes) - len(kept)} skipped (outside the region table)")

    try:
        existing = {r["Code INSEE"]: r for r in c.records(ids["commune"])}
        inserts, updates = [], []
        for x in kept:
            row, cur = to_row(x), existing.get(x["code"])
            if cur is None:
                inserts.append(row)
            elif any(cur.get(k) != v for k, v in row.items()):
                updates.append({"Id": cur["Id"], **row})
        for i in range(0, len(inserts), BATCH):
            c.write("POST", f"/api/v2/tables/{ids['commune']}/records", inserts[i:i + BATCH],
                    f"commune: add {len(inserts[i:i + BATCH])} rows")
        for i in range(0, len(updates), BATCH):
            c.write("PATCH", f"/api/v2/tables/{ids['commune']}/records", updates[i:i + BATCH],
                    f"commune: update {len(updates[i:i + BATCH])} rows")

        # Region links, set from the region side: one call per region instead of one per commune.
        rows = {r["Code INSEE"]: r for r in c.records(ids["commune"])}  # in a dry run, new ones are missing
        link = next(col for col in c.columns(ids["region"]) if col["title"] == "Communes")
        by_region = {}
        for x in kept:
            r = rows.get(x["code"])
            if r is None or not r.get("Région"):
                by_region.setdefault(regions[norm(x["region"]["nom"])], []).append(r["Id"] if r else None)
        for region_id, commune_ids in by_region.items():
            for i in range(0, len(commune_ids), BATCH):
                chunk = commune_ids[i:i + BATCH]
                c.write("POST", f"/api/v2/tables/{ids['region']}/links/{link['id']}/records/{region_id}",
                        [{"Id": cid} for cid in chunk], f"region #{region_id}: link {len(chunk)} communes")
    except ApiError as e:
        print(f"\nSTOPPED on API error, nothing after this point was applied:\n  {e}")
        sys.exit(1)
    print(f"{c.actions} change(s) {'planned' if c.dry_run else 'applied'}.")


if __name__ == "__main__":
    main()
