# PROGRESS.md : État d'avancement du projet

## 📊 État Global
- **Phase actuelle** : Phase 3 (Intégration Home Assistant)
- **Dernier Step validé** : Phase 3.2 (config_flow.py) + fiabilisation WebSocket

## 📝 Journal des Steps

- [x] **Step 1.1** : base_driver.py (WebSocket Core) - *Priorité Haute*
- [x] **Step 1.2** : discovery.py (mDNS Listener)
- [x] **Step 1.3** : Définir la structure des commandes et créer `sfr_tv_box_core/constants.py` pour les valeurs de commandes partagées.
- [x] **Phase 2.1** : stb8_driver.py - *Priorité Haute*
- [x] **Phase 2.2** : sfr_tv_box_remote.py (Mode "1-shot") - *Priorité Haute*
- [ ] **Phase 2.3** : stb7_driver.py - *Priorité Moyenne*
- [ ] **Phase 3** : Intégration Home Assistant (en cours)
- [x] **Phase 3.1** : manifest.json + tests/test_manifest.py (3 tests réussis, Ruff validé, publié sur GitHub)
- [x] **Phase 3.2** : config_flow.py + tests/test_config_flow.py (6 tests réussis, publié sur GitHub)
- [x] **Step 1.4** : Fiabilisation WebSocket (supervision, reconnexion exponentielle, arrêt propre, 20 tests ciblés réussis)
- [x] **Phase 4.1** : CI (Workflows GitHub Actions)
- [ ] **Phase 4.2** : CD (Publication)
- [ ] **Phase 4.3** : sfr_tv_box_remote.py (Mode interactif) - *Priorité Moyenne*
- [ ] **Phase 4.4** : Créer le workflow de release (Action GitHub) pour synchroniser la version du `pyproject.toml` vers `manifest.json` lors de la création d'un tag Git. - *Priorité Moyenne*
- [ ] **Phase 5.1** : labox_driver.py - *Priorité Basse*
- [ ] **Phase 5.2** : Implémenter la découverte EVO (Router API via MAC) - *Priorité Basse*
- [ ] **Phase 5.3** : evo_driver.py - *Priorité Basse*

## 🚧 Travail en cours (WIP)

- Phase 3 : manifeste et flux de configuration terminés. Reconnexion WebSocket fiabilisée.
- Validation locale actuelle : 43 tests réussis, Ruff sans erreur, 20 fichiers formatés.

## ⏭️ Prochaine Étape (Passage de relais)

- Définir et faire approuver la spécification de la prochaine brique d'intégration Home Assistant avant son implémentation.

## 🗂️ Backlog / V2

- [ ] **Amélioration Discovery**: Compléter la `DISCOVERY_SPEC.md` pour récupérer dynamiquement le port, le nom et l'icône de la box.
- [ ] **Analyse `GET_VERSIONS`**: Analyser la structure de la réponse de la commande `GET_VERSIONS`.
- [ ] **Analyse EVO**: Analyser l'architecture des commandes et réponses spécifiques au modèle EVO.
