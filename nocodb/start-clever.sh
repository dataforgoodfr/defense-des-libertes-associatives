#!/bin/sh
# Builds NC_DB from the variables Clever Cloud injects when the PostgreSQL add-on
# is linked to the app, so the database password lives in one place only.
# An explicit NC_DB still wins.
if [ -z "${NC_DB}" ] && [ -n "${POSTGRESQL_ADDON_HOST}" ]; then
  export NC_DB="pg://${POSTGRESQL_ADDON_HOST}:${POSTGRESQL_ADDON_PORT}?u=${POSTGRESQL_ADDON_USER}&p=${POSTGRESQL_ADDON_PASSWORD}&d=${POSTGRESQL_ADDON_DB}"
fi

exec /usr/src/appEntry/start.sh
