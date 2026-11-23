# Le schéma NocoDB comme du code

`schema_v1.py` décrit la base NocoDB du projet, et des scripts l'y conforment, jamais une modification à la main dans l'interface. Les mêmes scripts reconstruisent la base de zéro sur n'importe quelle instance NocoDB (par exemple celle de Clever Cloud déployée depuis `nocodb/`).

| Fichier | Rôle |
|---|---|
| `schema_v1.py` | Schéma cible de la V1 : tables, champs, liens, valeurs de référence. C'est ce fichier qu'on modifie pour changer le schéma |
| `apply.py` | Crée tout ce qui manque par rapport à la spécification. Se relance sans risque ; ne supprime jamais rien, ne change jamais un type, et signale les écarts en `DRIFT` |
| `seed_communes.py` | Remplit `commune` avec toutes les communes des 18 régions depuis geo.api.gouv.fr (nom, code INSEE, département, coordonnées, lien vers la région). Se relance sans risque ; la correspondance se fait sur le code INSEE |
| `drop.py` | Supprime les valeurs de référence et les champs retirés de `schema_v1.py`, que `apply.py` ne supprime jamais. Se relance sans risque ; refuse de supprimer une valeur encore liée à un enregistrement ou un champ qui contient encore des données, sauf si l'entrée en donne la raison. Inutile sur une base vide |
| `client.py` | Petit client d'API partagé par les scripts |

## Configuration

Un token d'API (dans NocoDB : avatar, « Account settings », « Tokens ») et l'identifiant de la base cible, dans `~/.config/d4g/nocodb.env`, hors du dépôt :

```
NOCODB_URL=https://<votre instance NocoDB>
NOCODB_TOKEN=...
NOCODB_BASE_ID=...
```

Facultatif : `NOCODB_ENV` pour lire un autre fichier d'environnement. Les scripts ne demandent que Python 3 et curl, sans autre dépendance. Ne jamais commiter le token.

## Utilisation

Toute modification de la base passe par ces scripts, jamais par l'interface ni par des appels d'API ponctuels : la base doit pouvoir être reconstruite de zéro. Modifier `schema_v1.py`, puis appliquer. Toujours lire le résultat du `--dry-run` avant d'appliquer.

À partir d'une base vide :

```
python3 nocodb/schema/apply.py --dry-run
python3 nocodb/schema/apply.py
python3 nocodb/schema/seed_communes.py --dry-run
python3 nocodb/schema/seed_communes.py    # environ 25 minutes : NocoDB accepte 100 lignes par requête
```

`apply.py --dry-run` doit ensuite annoncer 0 modification.

Les deux scripts s'arrêtent à la première erreur d'API et se relancent sans risque : les étapes terminées sont sautées.

Pour retirer une valeur ou un champ : le supprimer de `schema_v1.py`, ajouter dans `drop.py` une entrée avec la date et la raison, puis lancer `drop.py --dry-run` et `drop.py`.
