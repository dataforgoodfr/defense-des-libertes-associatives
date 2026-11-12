"""Thin client for the NocoDB v2 REST API (meta + data), shared by the schema scripts.

Credentials are read from an env file kept outside the repo (default ~/.config/d4g/nocodb.env):
    NOCODB_URL=https://<your NocoDB instance>
    NOCODB_TOKEN=...
    NOCODB_BASE_ID=...   # id of the target base (NocoDB: base context menu, Copy base ID)

Calls go through curl because some Python builds ship without a CA bundle.
"""
import json
import os
import re
import subprocess
import unicodedata

ENV_FILE = os.environ.get("NOCODB_ENV", os.path.expanduser("~/.config/d4g/nocodb.env"))
LINK_TYPES = ("LinkToAnotherRecord", "Links")
SELECT_TYPES = ("SingleSelect", "MultiSelect")


class ApiError(Exception):
    pass


def norm(s):
    """Accent-, case- and punctuation-insensitive key, to match 'Fécrier'-style variants."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def read_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


class Client:
    def __init__(self, dry_run):
        env = read_env(ENV_FILE)
        self.url = env["NOCODB_URL"].rstrip("/")
        self.token = env["NOCODB_TOKEN"]
        self.base_id = env["NOCODB_BASE_ID"]
        self.dry_run = dry_run
        self.actions = 0

    def _call(self, method, path, body=None):
        cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method, self.url + path,
               "-H", f"xc-token: {self.token}", "-H", "Content-Type: application/json"]
        if body is not None:
            cmd += ["--data-binary", json.dumps(body)]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
        txt, code = out.rsplit("\n", 1)
        if int(code) >= 400:
            raise ApiError(f"{method} {path} -> HTTP {code}: {txt[:500]}")
        return json.loads(txt) if txt else None

    def get(self, path):
        return self._call("GET", path)

    def write(self, method, path, body, desc):
        """Run a write call, or only print it in dry-run mode."""
        self.actions += 1
        if self.dry_run:
            print(f"  [plan] {desc}")
            return None
        result = self._call(method, path, body)
        print(f"  [done] {desc}")
        return result

    # --- meta ---

    def tables(self):
        data = self.get(f"/api/v2/meta/bases/{self.base_id}/tables")
        return {t["title"]: t["id"] for t in data["list"]}

    def table(self, table_id):
        return self.get(f"/api/v2/meta/tables/{table_id}")

    def columns(self, table_id):
        return [c for c in self.table(table_id)["columns"] if not c.get("system")]

    # --- data ---

    def records(self, table_id):
        rows, offset = [], 0
        while True:
            page = self.get(f"/api/v2/tables/{table_id}/records?limit=1000&offset={offset}")
            rows += page["list"]
            if page.get("pageInfo", {}).get("isLastPage", True):
                return rows
            offset += len(page["list"])
