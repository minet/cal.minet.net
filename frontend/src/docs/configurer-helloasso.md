---
title: Connecter HelloAsso à une organisation
scope: organisation
audience: treasury
category: Trésorerie
order: 1
summary: Reliez le compte HelloAsso de l'organisation pour activer la billetterie.
---

# Connecter HelloAsso à une organisation

La billetterie de Calend'INT s'appuie sur **HelloAsso**. La configuration des
identifiants est réservée aux personnes disposant du droit **trésorerie**
(`can_manage_payment_forms`) dans l'organisation ([[gerer-les-membres]]).

## Connecter le compte

1. Sur la page de l'organisation, ouvrez la configuration **HelloAsso**
   (`/organizations/<id>/helloasso`).
2. Renseignez le **slug HelloAsso** de l'organisation ainsi que ses identifiants d'API
   (client id / client secret).
3. Enregistrez.

Le secret d'API est **chiffré** au repos et n'est jamais réaffiché par l'application.

## Hiérarchie des organisations

Une organisation parente peut détenir la connexion HelloAsso pour ses organisations
filles : un formulaire de paiement proposé par une organisation fille peut s'appuyer sur
les identifiants d'une organisation parente de sa hiérarchie.

## Retirer la connexion

Vous pouvez **supprimer** les identifiants HelloAsso depuis la même page. Les billetteries
liées qui en dépendent sont alors retirées.

> Le droit trésorerie s'attribue membre par membre. La liste ci-dessus indique les
> organisations où vous en disposez. Étape suivante : [[proposer-formulaire-paiement]].
