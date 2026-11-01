# Spécification - Dépendance du moteur Python Home Assistant

## Problème
Home Assistant ne trouve pas le module `sfr_tv_box_core`,
car il est distribué séparément de l'intégration.

## Solution retenue
Déclarer le paquet Python du dépôt comme dépendance
Git PEP 508 dans le manifest de l'intégration.

La dépendance sera épinglée sur le commit a57a8b9.

## Modifications prévues
- Mettre à jour manifest.json.
- Ajouter un test de validation de la dépendance.
- Conserver les imports actuels du moteur.
- Mettre à jour PROGRESS.md.

## Validation
- Tests automatisés réussis.
- Ruff sans erreur.
- Installation réelle dans Home Assistant.
- Chargement du flux de configuration.
- Connexion au décodeur SFR Box 8.

## Limite
Cette solution nécessite que Home Assistant puisse installer
le paquet depuis le dépôt GitHub.
