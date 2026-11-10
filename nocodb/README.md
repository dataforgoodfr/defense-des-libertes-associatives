# NocoDB

Back-office de saisie et de qualification des cas, déployé sur Clever Cloud
(organisation SMA) au-dessus de l'add-on PostgreSQL `postgres-nocodb-sma`.

- `Dockerfile` : image officielle NocoDB, version épinglée.
- `start-clever.sh` : construit `NC_DB` à partir des variables `POSTGRESQL_ADDON_*`
  injectées par Clever Cloud, puis lance NocoDB.
- `.env.example` : les variables à définir sur l'app.
- `docker-compose.yaml` : test local contre un PostgreSQL 18.

NocoDB stocke tout dans PostgreSQL : ses propres tables (`nc_*`, dans `public`) et
une table de données par schéma de base (un schéma par base NocoDB). Rien n'est
écrit sur le disque de l'app, qui est effacé à chaque redéploiement.

## Tester en local

```sh
docker compose -f nocodb/docker-compose.yaml up --build
# http://localhost:8080 ; arrêter et tout effacer :
docker compose -f nocodb/docker-compose.yaml down -v
```

## Premier déploiement

Depuis la racine du dépôt, avec [clever-tools](https://www.clever-cloud.com/developers/doc/cli/) :

```sh
clever create --type docker --org SMA --region par nocodb-sma
clever service link-addon postgres-nocodb-sma
clever env set APP_FOLDER nocodb
clever env set NC_AUTH_JWT_SECRET "$(openssl rand -hex 32)"
clever env set NC_PUBLIC_URL https://nocodb-sma.cleverapps.io
clever env set NC_DISABLE_TELE true
clever domain add nocodb-sma.cleverapps.io
clever scale --flavor XS
clever deploy
clever logs
```

Dès que l'app répond, créer le compte administrateur : le premier compte inscrit
devient super admin. Puis inviter les autres utilisateurs depuis NocoDB.

## Mettre à jour NocoDB

1. Lire les notes de version : https://github.com/nocodb/nocodb/releases
2. Changer le tag dans `Dockerfile` et tester en local.
3. Committer, puis `clever deploy`. NocoDB migre ses tables au démarrage :
   vérifier qu'une sauvegarde récente de l'add-on existe avant.

## Limites connues

- Pas de stockage de pièces jointes : tant qu'un bucket Cellar n'est pas configuré
  (`NC_S3_*`), un fichier téléversé dans NocoDB est perdu au redéploiement.
- Le support de PostgreSQL 18 n'est pas documenté par NocoDB ; il a été vérifié
  en local avec la version 2026.10.1 (démarrage, création de base et de table,
  sessions conservées après redémarrage).
