# Décisions d'architecture

Ce dossier tient le journal des décisions du projet, sous forme d'ADR (Architecture Decision Record) : une décision par fichier, numérotée dans l'ordre où elle est consignée. Il sert à retrouver pourquoi un choix a été fait, quelles options ont été écartées et qui y a participé, avant de le remettre en cause. Les ADR demandés par #41 (stack du site public) et #42 (lecture des cas validés) s'écrivent ici.

## Tenir le journal

- **Quoi consigner.** Une décision coûteuse à défaire ou qui engage d'autres personnes : hébergement, modèle de données, vocabulaire publié, règle de publication. Pas les choix d'implémentation qu'une pull request suffit à expliquer.
- **Comment.** Créer un fichier `NNN-titre-court.md` avec le numéro suivant, sur le modèle ci-dessous, puis ajouter sa ligne en bas du tableau. Écrire « non documenté » plutôt que deviner, et citer les issues et pull requests d'où vient l'information.
- **Quand.** Dans la pull request qui met la décision en œuvre, ou juste après la réunion qui l'a prise.
- **Réviser.** Une décision ne s'efface jamais. Quand une autre la remplace, passer son statut à « Remplacée par NNN » et ajouter la nouvelle entrée.
- **Relire.** Relire le journal avec l'équipe avant chaque nouvelle étape (V2 du schéma, ouverture du site), pour vérifier que les décisions tiennent toujours.

## Modèle d'une entrée

```markdown
# NNN. La décision, en une phrase

AAAA-MM-JJ · Catégorie · Statut · Porteur, avec les parties prenantes

## Contexte

Le problème à résoudre et les contraintes, sans la solution.

## Décision

Ce qui a été décidé, et pourquoi.

## Options écartées

- **Option** : pourquoi elle a été écartée.

## Conséquences

Ce que la décision rend possible ou impose, et ce qui reste à trancher.

Voir les fichiers, issues et pull requests concernés.
```

« Options écartées » ne figure que si d'autres options ont été envisagées. Dans une entrée, `#N` désigne une issue ou une pull request, et un lien comme `[002](002-titre-court.md)` une autre entrée du journal.

## Vue d'ensemble

| # | Date | Décision | Catégorie | Porteur | Statut |
|---|---|---|---|---|---|
