"""Tests for the Home Assistant integration manifest."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "custom_components" / "sfr_box_remote" / "manifest.json"


def test_manifest_is_valid_json():
    """Check that the manifest contains valid JSON."""
    with MANIFEST_PATH.open(encoding="utf-8") as file:
        manifest = json.load(file)

    assert isinstance(manifest, dict)


def test_manifest_contains_required_fields():
    """Check that all required manifest fields are present."""
    with MANIFEST_PATH.open(encoding="utf-8") as file:
        manifest = json.load(file)

    required_fields = {
        "domain",
        "name",
        "codeowners",
        "config_flow",
        "documentation",
        "integration_type",
        "iot_class",
        "requirements",
        "version",
    }

    assert required_fields.issubset(manifest)


def test_manifest_matches_project_specification():
    """Check that manifest values match the approved specification."""
    with MANIFEST_PATH.open(encoding="utf-8") as file:
        manifest = json.load(file)

    assert manifest["domain"] == "sfr_box_remote"
    assert manifest["name"] == "SFR Box Remote"
    assert manifest["version"] == "0.1.0"
    assert manifest["config_flow"] is True
    assert manifest["integration_type"] == "device"
    assert manifest["iot_class"] == "local_push"
    assert manifest["requirements"] == [
        "sfr-tv-box-remote @ git+https://github.com/nathanlambert25-spec/sfr-tv-box-remote.git@a57a8b983ee2a1ef7b81ab19d8af4b6738bba58d"
    ]
