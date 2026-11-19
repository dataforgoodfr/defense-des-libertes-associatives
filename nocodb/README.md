# NocoDB

Back-office de saisie et de qualification des cas, déployé sur Clever Cloud
(organisation SMA, app `nocodb-sma`, taille S) au-dessus de l'add-on PostgreSQL
`postgres-nocodb-sma` : https://nocodb-sma.cleverapps.io

- `Dockerfile` : image officielle NocoDB, version épinglée.
- `start-clever.sh` : construit `NC_DB` à partir des variables `POSTGRESQL_ADDON_*`
  injectées par Clever Cloud (mot de passe encodé), puis lance NocoDB. S'arrête en
  erreur si aucune base n'est configurée, plutôt que de démarrer sur SQLite.
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
clever env set CC_APP_FOLDER nocodb
clever env set NC_AUTH_JWT_SECRET "$(openssl rand -hex 32)"
clever env set NC_PUBLIC_URL https://nocodb-sma.cleverapps.io
clever env set NC_DISABLE_TELE true
clever domain add nocodb-sma.cleverapps.io
clever scale --flavor S
clever deploy
clever logs
```

`clever create` écrit un `.clever.json` à la racine du dépôt, qui relie le dossier
local à l'app. Il ne contient pas de secret mais reste propre à chacun : ne pas le
committer (par exemple `echo .clever.json >> .git/info/exclude`). Pour relier un
autre poste à l'app existante : `clever link nocodb-sma --org SMA`.

Dès que l'app répond, créer le compte administrateur : le premier compte inscrit
devient super admin. Puis inviter les autres utilisateurs depuis NocoDB.

## Taille de l'instance

NocoDB utilise environ 600 à 750 Mo de mémoire au repos (mesuré en local). Sur une
instance XS (1 Go, partagé avec le système et Docker), Node.js plafonne sa mémoire
vers 330 Mo et NocoDB plante au démarrage (`JavaScript heap out of memory`). La
taille S (2 Go) suffit avec les réglages par défaut.

## Redéployer

- Après un changement de variable (`clever env set`) : `clever restart`. Les
  variables ne sont lues qu'au démarrage.
- Après un merge sur `main` : `clever deploy` depuis `main` à jour.

## Mettre à jour NocoDB

1. Lire les notes de version : https://github.com/nocodb/nocodb/releases
2. Changer le tag dans `Dockerfile` et tester en local.
3. Merger, puis `clever deploy` depuis `main`. NocoDB migre ses tables au démarrage :
   vérifier qu'une sauvegarde récente de l'add-on existe avant.

## Limites connues

- Pas de stockage de pièces jointes : tant qu'un bucket Cellar n'est pas configuré
  (`NC_S3_*`), un fichier téléversé dans NocoDB est perdu au redéploiement.
- Le support de PostgreSQL 18 n'est pas documenté par NocoDB ; il a été vérifié
  en local avec la version 2026.10.1 (démarrage, création de base et de table,
  sessions conservées après redémarrage).
