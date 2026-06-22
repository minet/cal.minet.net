---
title: Créer une organisation
scope: application
audience: superadmin
category: Administration
order: 1
summary: Seuls les super-administrateurs créent les organisations.
---

# Créer une organisation

La **création** d'une organisation est réservée aux **super-administrateurs**. Une fois
créée, l'organisation peut ensuite être gérée par ses propres administrateurs
([[personnaliser-organisation]], [[gerer-les-membres]]).

## Créer

1. Depuis la liste des organisations, ouvrez la
   [création d'organisation](/organizations/create).
2. Renseignez le **nom**, l'**identifiant court** (slug), le **type** (association, club,
   liste, administration…) et, si besoin, l'**organisation parente**.
3. Ajoutez logo, couleurs et description selon vos besoins.

## Hiérarchie

Le champ **organisation parente** structure les organisations en arborescence. Cette
hiérarchie est utilisée notamment :

- pour la délégation d'administration (un administrateur de l'organisation parente peut
  modifier une organisation fille) ;
- pour le circuit d'approbation des formulaires de paiement
  ([[proposer-formulaire-paiement]]).

## Suppression

Une organisation peut être supprimée par ses administrateurs ou un super-administrateur ;
ses événements sont alors rattachés à l'organisation parente. Une suppression différée est
aussi traitée automatiquement par la maintenance ([[administration-instance]]).

