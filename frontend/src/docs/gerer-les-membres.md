---
title: Gérer les membres d'une organisation
scope: organisation
audience: org_admin_plus
category: Gérer une organisation
order: 1
summary: Ajoutez des membres, attribuez les rôles, titres et droits de trésorerie.
---

# Gérer les membres d'une organisation

La gestion des membres est réservée aux **administrateurs** de l'organisation (et aux
super-administrateurs).

## Accéder à la gestion des membres

Sur la page de l'organisation, cliquez sur **Membres** (`/organizations/<id>/members`).

## Ajouter un membre

1. Saisissez l'**adresse e-mail** de la personne (elle doit déjà avoir un compte).
2. Choisissez son **rôle**.
3. Ajoutez éventuellement un **titre** (ex. « Président », « Trésorier »).

## Les rôles

- **Administrateur** : gère l'organisation, ses membres, ses tags, ses groupes et ses
  événements.
- **Membre** : peut créer et modérer des événements.
- **Lecteur** : accès en consultation aux contenus internes de l'organisation.

## Titres, ordre et trésorerie

- Vous pouvez modifier le **rôle** et le **titre** d'un membre, et **réordonner** la liste
  (affichage public).
- Vous pouvez accorder à un membre le droit de **gérer la trésorerie**
  (`can_manage_payment_forms`), nécessaire pour les formulaires de paiement et la
  billetterie ([[configurer-helloasso]], [[proposer-formulaire-paiement]]).

> Donnez le rôle administrateur et le droit de trésorerie avec parcimonie. La gestion des
> membres requiert d'être administrateur **de cette organisation** ; la liste ci-dessus
> indique lesquelles.

## Confidentialité selon l'année d'étude

Le bloc **Confidentialité de la liste des membres** permet de masquer toute la liste aux
étudiants de **1re**, **2e** ou **3e année**. Il est aussi possible de masquer une seule
personne à certaines années avec les boutons situés sous son nom. Les restrictions
individuelles s'ajoutent à celles de l'organisation.

Les membres de l'organisation, ses administrateurs et les super-administrateurs voient
toujours la liste complète. Pour les autres visiteurs :

- l'année d'étude provient de la dernière synchronisation LDAP ;
- un étudiant ne voit pas les membres masqués pour son année ;
- un visiteur anonyme, ou un compte dont l'année est inconnue, ne voit aucun membre faisant
  l'objet d'au moins une restriction.

Après un changement d'année scolaire, un super-administrateur doit relancer la
**synchronisation LDAP** afin d'actualiser les années des étudiants.

## Passation de mandat

Pour transférer un poste à un·e remplaçant·e en fin de mandat (le vôtre ou celui d'un autre
membre), voir [[passation-de-mandat]]. Chaque membre peut transférer son propre poste
depuis cette même page, sans passer par vous.
