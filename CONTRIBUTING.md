# Contribuer

Le projet est mené par des bénévoles de Data For Good avec le SMA et l'OLA. Ce guide explique comment prendre une issue, ouvrir une pull request et la faire relire. L'installation est décrite dans le [README](README.md).

## Le dépôt est public : aucune donnée, aucun secret

Aucun cas, fichier de données (tableurs du SMA ou de l'OLA), export de base, sauvegarde, résultat d'analyse nominatif ni secret n'entre dans le dépôt, même temporairement. Un fichier retiré reste dans l'historique git, dans les forks et dans les clones : le supprimer après coup ne sert à rien.

- Les fichiers de données vivent hors du dépôt, et les scripts reçoivent leur chemin en argument. Le `.gitignore` exclut les formats courants (`*.csv`, `*.xlsx`, `*.ods`, `*.sql`, `data/`…), mais il ne remplace pas la vigilance.
- Chaque personne crée son propre token NocoDB et le garde dans `~/.config/d4g/nocodb.env` (voir `nocodb/schema/README.md`).
- Les variables de l'app NocoDB (`NC_AUTH_JWT_SECRET`, `NC_PUBLIC_URL`…) sont définies dans la configuration Clever Cloud, sur le compte du SMA, jamais dans le dépôt.
- Le dépôt n'a aucun secret GitHub Actions.

Si un secret ou une donnée a été poussé par erreur, prévenir tout de suite les tech leads et révoquer le token concerné.

## Prendre une issue

Le travail est suivi dans les [issues GitHub](https://github.com/dataforgoodfr/defense-des-libertes-associatives/issues). Les issues marquées `good first issue` conviennent pour commencer, et les labels `front`, `back`, `data`, `devops`… indiquent l'équipe concernée.

Avant de commencer, commenter l'issue pour la prendre. Pas d'issue pour ce que vous voulez faire ? En créer une d'abord.

## Nommer la branche

`<type>/<n° issue>-<description>`, par exemple `feat/34-base-production` ou `poc/29-presse-rss`.

- **Types :** `feat`, `fix`, `poc` (exploration du Lab), `docs`, `chore` (configuration, CI, déploiement).
- **Numéro d'issue** obligatoire.
- **Description** en français, en minuscules, en kebab-case, sans accents, de 2 à 4 mots.
- Pas d'équipe dans le nom : les labels la portent.

Une branche = une issue = une pull request.

## Ouvrir une pull request

- **Titre.** Clair et en français : au merge, il devient le commit sur `main`.
- **Description.** Ce qui change, pourquoi, comment le vérifier, et `Closes #N` pour fermer l'issue au merge.
- **Vérifications.** Ruff relit le code Python et yamllint les workflows ; les deux doivent passer. Pour les lancer avant de pousser, voir la section « Vérifications » du [README](README.md).

## Relecture et merge

La règle « Protection de main » impose :

- une pull request pour tout changement sur `main`, sans push direct ni force-push ;
- une approbation, par une autre personne que l'auteur ou l'autrice de la PR ;
- une nouvelle approbation après chaque nouveau push ;
- toutes les discussions de relecture résolues ;
- un merge en squash uniquement. La branche est supprimée après le merge.

Relecteurs : les tech leads, Jun Suzuki ([szkjn](https://github.com/szkjn)) et Séverine Leguy ([SeverineLEGUY](https://github.com/SeverineLEGUY)).
