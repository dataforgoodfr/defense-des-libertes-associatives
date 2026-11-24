# Défense des libertés culturelles

Base des atteintes aux libertés culturelles recensées par le SMA et l'OLA, qui saisissent les cas dans NocoDB ; le futur site public ne montrera que les cas validés.

## Contenu du dépôt

| Dossier | Contenu |
|---|---|
| `nocodb/` | Déploiement de NocoDB sur Clever Cloud et environnement local (voir `nocodb/README.md`) |
| `nocodb/schema/` | Scripts qui créent et font évoluer le schéma de la base (voir `nocodb/schema/README.md`) |

## Installation

Les scripts n'utilisent que la bibliothèque standard de Python (3.12 ou plus) et curl. [uv](https://docs.astral.sh/uv/) installe la bonne version de Python :

```bash
uv sync
uv run nocodb/schema/apply.py --dry-run
```

Les scripts de schéma lisent l'adresse de l'instance NocoDB, un token d'API et l'identifiant de la base dans `~/.config/d4g/nocodb.env`, hors du dépôt ; `nocodb/schema/README.md` détaille ce fichier.

## Vérifications

Une pull request qui modifie du code Python passe par Ruff ; une pull request qui modifie les workflows passe par yamllint. Pour lancer les mêmes vérifications en local :

```bash
uvx ruff check .
uvx yamllint .github/workflows/
```

Pour que Ruff corrige le code à chaque commit, installer les hooks [pre-commit](https://pre-commit.com/) une fois :

```bash
uvx pre-commit install
```
