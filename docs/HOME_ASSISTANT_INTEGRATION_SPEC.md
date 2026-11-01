# HOME_ASSISTANT_INTEGRATION_SPEC.md

## 1. Objectif

Créer une intégration personnalisée Home Assistant permettant de piloter les décodeurs SFR, en commençant par la STB8.

L'intégration doit réutiliser la bibliothèque indépendante `sfr_tv_box_core`.

## 2. Configuration

- Ajout depuis l'interface Home Assistant.
- Saisie de l'adresse IP du décodeur.
- Port WebSocket configurable, valeur par défaut : `7682`.
- Identifiant du décodeur configurable, valeur par défaut : `default-stb8`.
- Sélection du modèle : STB8 dans cette première version.

## 3. Architecture

Répertoire : `custom_components/sfr_box_remote/`

- `__init__.py` : initialisation et gestion du cycle de vie.
- `manifest.json` : métadonnées et dépendances.
- `config_flow.py` : configuration depuis l'interface.
- `const.py` : constantes de l'intégration.
- `media_player.py` : entité multimédia.
- `remote.py` : commandes de télécommande.
- `strings.json` : traductions et configuration.

## 4. Fonctionnalités V1

- Connexion WebSocket persistante.
- Reconnexion automatique.
- Allumage et extinction.
- Volume + / − et mute.
- Chaîne + / −.
- Navigation et validation.
- Retour et accueil.
- Pavé numérique 0 à 9.
- Commandes multimédias disponibles.

## 5. Retour d'état

- Interprétation des réponses JSON.
- État marche / arrêt.
- Actualisation des informations à réception des messages.
- Gestion de la perte de connexion.

La chaîne et le volume ne seront exposés que si le protocole fournit réellement ces informations.

## 6. Tests

- Tests unitaires de configuration.
- Tests de connexion WebSocket simulée.
- Tests d'envoi des commandes.
- Tests de réception et d'interprétation des réponses.
- Vérification avec Ruff.

## 7. Contraintes

- Aucune dépendance Home Assistant dans `sfr_tv_box_core`.
- Respect de l'architecture asynchrone.
- Conservation du fonctionnement actuel de la CLI.
- Compatibilité HACS à terme.

## 8. Évolutions ultérieures

- Détection automatique mDNS.
- Gestion multi-box.
- Support STB7, LaBox et EVO.
- Lancement direct des applications.
- Dashboard Lovelace dédié.
