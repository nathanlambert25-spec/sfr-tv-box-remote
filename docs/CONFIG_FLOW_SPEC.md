# CONFIG_FLOW_SPEC.md

## 1. Objectif

Définir le flux de configuration graphique de l'intégration Home Assistant
SFR Box Remote pour les décodeurs SFR STB8.

L'utilisateur doit pouvoir ajouter son décodeur depuis l'interface Home
Assistant, sans modifier de fichier YAML.

## 2. Informations demandées

| Champ | Type | Valeur par défaut |
|---|---|---|
| Adresse IP | Texte | Aucune |
| Port WebSocket | Nombre | 7682 |
| Identifiant du décodeur | Texte | default-stb8 |

## 3. Fonctionnement

1. L'utilisateur ouvre Paramètres > Appareils et services.
2. Il sélectionne Ajouter une intégration.
3. Il recherche SFR Box Remote.
4. Il renseigne les informations du décodeur.
5. L'intégration valide les paramètres et tente une connexion WebSocket.
6. Si la connexion réussit, l'intégration est ajoutée à Home Assistant.

## 4. Gestion des erreurs

- `cannot_connect` : décodeur inaccessible ou connexion impossible.
- `invalid_host` : adresse IP invalide.
- `invalid_port` : port invalide.
- `already_configured` : décodeur déjà configuré.

## 5. Contraintes techniques

- Utilisation du système ConfigFlow officiel de Home Assistant.
- Aucune dépendance Home Assistant dans `sfr_tv_box_core`.
- Connexion asynchrone.
- Aucun mot de passe demandé.
- Détection des doublons grâce à l'identifiant du décodeur.
- Traductions françaises.
- Tests unitaires avec WebSocket simulé.
- Respect des règles définies dans AGENTS.md.

## 6. Fichiers concernés

- Implémentation : `custom_components/sfr_box_remote/config_flow.py`
- Tests : `tests/test_config_flow.py`

## 7. Critères de validation

- Le formulaire de configuration s'affiche correctement.
- Les paramètres saisis sont validés.
- Une connexion WebSocket fonctionnelle permet de créer l'entrée.
- Une connexion impossible affiche une erreur adaptée.
- Un identifiant déjà configuré est refusé.
- Les tests unitaires passent.
- Ruff ne signale aucune erreur.
