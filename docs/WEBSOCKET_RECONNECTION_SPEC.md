# WEBSOCKET_RECONNECTION_SPEC

## 1. Objectif

Fiabiliser le cycle de vie WebSocket de `BaseSFRBoxDriver`
pour garantir une reconnexion automatique et un arrêt propre,
sans bloquer l'initialisation de Home Assistant.

## 2. Périmètre

Fichier concerné :
- `sfr_tv_box_core/base_driver.py`

Tests :
- `tests/test_base_driver_reconnection.py`

## 3. Comportements attendus

### Démarrage
- `start()` doit être idempotente.
- Un seul mécanisme de connexion et d'écoute doit fonctionner.
- Le démarrage ne doit pas attendre indéfiniment une box indisponible.

### Reconnexion
- Reconnexion automatique après une déconnexion.
- Backoff exponentiel : 1, 2, 4, 8 secondes, jusqu'à 60 secondes.
- Ne pas appeler récursivement `start()` depuis la tâche d'écoute.
- Éviter les connexions et tâches concurrentes.

### Arrêt
- `stop()` doit fermer proprement la connexion WebSocket.
- Les tâches internes doivent être annulées et attendues proprement.
- Aucun redémarrage automatique ne doit survenir après un arrêt explicite.
- Les appels répétés à `stop()` doivent être sans danger.

### Compatibilité
- Préserver l'API publique existante autant que possible.
- Préserver le fonctionnement du CLI et du pilote STB8.
- Ne pas introduire de dépendance à Home Assistant dans le cœur.

## 4. Tests obligatoires

- Connexion initiale réussie.
- Connexion initiale impossible puis reconnexion réussie.
- Déconnexion inattendue puis reconnexion.
- Arrêt pendant une tentative de connexion.
- Arrêt pendant l'écoute des messages.
- Plusieurs appels à `start()`.
- Plusieurs appels à `stop()`.
- Vérification de l'absence de tâches résiduelles.
- Vérification de la réception et de la distribution des messages.

Les tests doivent simuler les réponses et déconnexions WebSocket.

## 5. Qualité

Avant validation :
- `python -m pytest -q --no-cov`
- `python -m ruff check .`
- `python -m ruff format --check .`

## 6. Critères d'acceptation

- Tous les tests passent.
- Aucune tâche WebSocket résiduelle après l'arrêt.
- Une seule boucle de reconnexion active.
- Le CLI et le pilote STB8 restent fonctionnels.
- Documentation et PROGRESS.md mis à jour.
- Validation utilisateur avant publication Git.
