#!/bin/sh
# Builds NC_DB from the variables Clever Cloud injects when the PostgreSQL add-on
# is linked to the app, so the database password lives in one place only.
# An explicit NC_DB still wins.
if [ -z "${NC_DB}" ] && [ -n "${POSTGRESQL_ADDON_HOST}" ]; then
  # The password goes in a query string: encode it so &, #, % and the like survive.
  password=$(node -e 'process.stdout.write(encodeURIComponent(process.argv[1]))' "${POSTGRESQL_ADDON_PASSWORD}")
  export NC_DB="pg://${POSTGRESQL_ADDON_HOST}:${POSTGRESQL_ADDON_PORT}?u=${POSTGRESQL_ADDON_USER}&p=${password}&d=${POSTGRESQL_ADDON_DB}"
fi

# Without NC_DB, NocoDB silently falls back to SQLite on the container's disk,
# which Clever Cloud wipes on every redeploy.
if [ -z "${NC_DB}" ]; then
  echo "start-clever.sh: no database configured. Link the PostgreSQL add-on or set NC_DB." >&2
  exit 1
fi

exec /usr/src/appEntry/start.sh
