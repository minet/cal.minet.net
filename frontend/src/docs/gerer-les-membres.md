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
