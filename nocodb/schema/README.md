# NocoDB schema as code

The NocoDB base of the project is described in `schema_v1.py` and brought in line by script, not by hand in the UI. The same scripts rebuild the base from zero on any NocoDB instance (for example the Clever Cloud one deployed from `nocodb/`).

| File | Role |
|---|---|
| `schema_v1.py` | Target V1 schema: tables, fields, links, reference values. Edit this file to change the schema |
| `apply.py` | Creates whatever is missing from the spec. Rerunnable; never deletes or retypes, reports mismatches as `DRIFT` |
| `seed_communes.py` | Fills `commune` with every commune of the 18 regions from geo.api.gouv.fr (name, INSEE code, department, coordinates, region link). Rerunnable, matched on the INSEE code |
| `drop.py` | Deletes the reference values and fields taken out of `schema_v1.py`, which `apply.py` never deletes. Rerunnable; refuses to delete a value still linked to a record or a field that still holds data, unless the entry says why. Not needed on an empty base |
| `client.py` | Small API client shared by the scripts |

## Setup

An API token (NocoDB: avatar, Account settings, Tokens) and the id of the target base, in `~/.config/d4g/nocodb.env`, outside the repo:

```
NOCODB_URL=https://<your NocoDB instance>
NOCODB_TOKEN=...
NOCODB_BASE_ID=...
```

Optional: `NOCODB_ENV` to read another env file. Needs Python 3 and curl, no other dependency. Never commit the token.

## Usage

Every change to the base goes through these scripts, never through the UI or one-off API calls: the base must be rebuildable from zero. Change `schema_v1.py`, then apply. Always read the dry run before applying.

From an empty base:

```
python3 nocodb/schema/apply.py --dry-run
python3 nocodb/schema/apply.py
python3 nocodb/schema/seed_communes.py --dry-run
python3 nocodb/schema/seed_communes.py    # about 25 minutes: NocoDB takes 100 rows per request
```

`apply.py --dry-run` must then report 0 changes.

Both scripts stop at the first API error and can be rerun: finished steps are skipped.

To remove a value or a field: delete it from `schema_v1.py`, add an entry to `drop.py` with the date and the reason, then run `drop.py --dry-run` and `drop.py`.
