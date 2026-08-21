---
title: Maintenance de l'instance
scope: application
audience: superadmin
category: Administration
order: 5
summary: Synchronisation de l'annuaire, ménage des organisations et des comptes.
---

# Maintenance de l'instance

La page [**Instance**](/admin/instance) regroupe les opérations de maintenance réservées
aux **super-administrateurs**.

## Synchronisation de l'annuaire (LDAP)

La **synchronisation LDAP** met à jour un instantané local de l'annuaire de l'école. Elle
est nécessaire au respect du **RGPD** : elle permet de s'assurer que les **anciens
étudiants**, qui ne font plus partie de l'école, ne restent pas dans la base de données.

Concrètement, la synchronisation rafraîchit la liste de référence ; les comptes
**orphelins** (présents dans Calend'INT mais absents de l'annuaire et non exemptés) sont
ensuite supprimés par le **ménage** (voir ci-dessous).

### Identifiants

Utilisez le **nom d'utilisateur (uid) et le mot de passe de votre compte du portail
scolaire**. Ces identifiants ne sont **ni enregistrés sur le serveur, ni sur le poste
client** : ils servent une seule fois, le temps de se connecter à l'annuaire et d'importer
les données.

### Quand la lancer

Nous recommandons de lancer la synchronisation **plusieurs fois en début d'année scolaire**
(le temps que les comptes de l'annuaire se stabilisent), puis **une fois en fin d'année**.

## Ménage (housekeeping)

L'opération de **ménage** :

- supprime les organisations dont la **date de suppression différée** est dépassée (leurs
  événements sont rattachés à l'organisation parente) ;
- en option, supprime les **comptes orphelins** non exemptés (l'historique de paiement est
  préservé via un compte « fantôme »).

Les comptes peuvent être protégés de cette suppression via l'option d'**exemption RGPD**
([[gerer-les-utilisateurs]]).

## Rappels de passation

Le bouton **Envoyer les rappels de passation** envoie un e-mail à tous les
administrateur·rice·s d'organisation en poste depuis plus de 8 mois, avec un lien direct
vers la page de passation de chacune de leurs organisations (voir
[[passation-de-mandat]]). Utile en fin d'année scolaire pour rattraper les organisations
qui n'ont pas encore préparé leur relève.

## Tags auto-approuvés

L'administration des tags **auto-approuvés** (publication d'événements sans validation) se
gère également au niveau de l'instance, sur la page [Tags](/admin/tags) — voir
[[approbations]].

> Ces opérations sont réservées aux super-administrateurs et peuvent affecter l'ensemble
> de l'instance : procédez avec précaution.
