# REMOTE_SPEC.md — Entité Remote Home Assistant

## 1. Objectif

Ajouter une plateforme `remote` à l'intégration Home Assistant
`SFR Box Remote`, afin de piloter le décodeur STB8 depuis Home Assistant.

L'intégration réutilise exclusivement le pilote existant
`STB8Driver` et les commandes abstraites `KeyCode`.

## 2. Périmètre fonctionnel

L'entité Remote doit permettre l'envoi des commandes suivantes :

- Navigation : UP, DOWN, LEFT, RIGHT, OK, BACK, HOME.
- Volume : VOL_UP, VOL_DOWN, MUTE.
- Chaînes : CHAN_UP, CHAN_DOWN.
- Média : PLAY_PAUSE, FFWD, REWIND, STOP, RECORD.
- Alimentation : POWER.
- Numérotation : NUM_0 à NUM_9.

Les touches DELETE et OPTIONS sont exclues : leur mapping STB8
n'est pas actuellement confirmé.

## 3. Architecture

Fichier principal :

- `custom_components/sfr_box_remote/remote.py`

Fichiers complémentaires concernés :

- `custom_components/sfr_box_remote/__init__.py`
- `custom_components/sfr_box_remote/const.py`
- `custom_components/sfr_box_remote/strings.json`
- `tests/test_remote.py`

La plateforme Remote doit :

- Utiliser l'API Remote de Home Assistant.
- Récupérer l'instance STB8Driver créée pour l'entrée de configuration.
- Convertir les commandes Home Assistant en valeurs `KeyCode`.
- Envoyer les commandes avec `STB8Driver.send_command()`.
- Ne pas reproduire le mapping du protocole STB8 dans l'intégration.
- Utiliser un identifiant unique stable basé sur l'entrée de configuration.

## 4. Connexion et disponibilité

L'entité doit être indisponible lorsque le WebSocket du décodeur
n'est pas connecté.

Le pilote devra exposer un indicateur public de connexion si
aucune propriété publique adaptée n'existe actuellement.

L'entité ne doit pas accéder directement aux attributs privés
du pilote pour déterminer sa disponibilité.

Une commande envoyée lorsque le décodeur est déconnecté ne doit
pas provoquer de plantage de Home Assistant.

## 5. États et limites

L'entité Remote sert uniquement au pilotage.

Elle ne doit pas prétendre connaître :

- La chaîne actuellement regardée.
- L'état réel de lecture ou de pause.
- Le niveau sonore réel.
- L'état réel de l'alimentation.

Ces informations ne sont pas encore interprétées par le pilote STB8.

## 6. Tests obligatoires

Créer `tests/test_remote.py` avec des tests simulant le pilote :

- Création de l'entité Remote.
- Vérification de l'identifiant unique.
- Vérification du mapping des commandes.
- Vérification de l'appel à `send_command()`.
- Vérification de l'indisponibilité lorsque le WebSocket est déconnecté.
- Vérification du comportement lors d'une commande en étant déconnecté.
- Vérification de l'enregistrement et du déchargement de la plateforme.

Les tests doivent utiliser des simulations, sans connexion réelle
au décodeur.

## 7. Qualité et validation

Après implémentation :

- Exécuter les tests unitaires.
- Exécuter `python -m ruff check .`.
- Exécuter `python -m ruff format .`.
- Vérifier le formatage avec `python -m ruff format --check .`.
- Mettre à jour `PROGRESS.md`.
- Mettre à jour la documentation si nécessaire.

Respecter le principe TDD : les tests sont écrits avant
l'implémentation.

## 8. Ordre de réalisation

1. Créer et valider cette spécification.
2. Créer les tests de l'entité Remote.
3. Implémenter `remote.py`.
4. Adapter le cycle de vie de l'intégration si nécessaire.
5. Exécuter les contrôles qualité.
6. Mettre à jour `PROGRESS.md`.
7. Attendre la validation et la publication Git avant la prochaine brique.
