# MANIFEST_SPEC.md

## 1. Objectif

Définir les métadonnées de l'intégration Home Assistant SFR Box Remote.

## 2. Paramètres

- `domain` : `sfr_box_remote`
- `name` : `SFR Box Remote`
- `version` : `0.1.0`
- `config_flow` : `true`
- `integration_type` : `device`
- `iot_class` : `local_push`

## 3. Dépendances

- `websockets>=12.0`

La bibliothèque `sfr_tv_box_core` reste indépendante de Home Assistant.

## 4. Contraintes

- Respect du format officiel du manifest Home Assistant.
- Compatibilité avec HACS.
- Version synchronisée ultérieurement avec `pyproject.toml`.
- Aucune dépendance superflue.
