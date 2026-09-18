"""Unit tests for taintrace configuration file loading, validation, and CLI overrides."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from taintrace.cli import cli
from taintrace.config import (
    load_config,
    get_ignored_packages,
    interpolate_env_vars,
    validate_config,
    find_default_config,
)


class TestConfigLoadingAndFormats:
    """Test loading configs across various standard file formats."""

    def test_load_toml_config(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / ".taintrace.toml"
        cfg_file.write_text(
            """
[taintrace]
threshold = 0.85
output_format = "json"
ecosystem = "python"
no_informational = true
ignore = ["safe-pkg-1", "safe-pkg-2"]
"""
        )
        cfg = load_config(cwd=tmp_path)
        assert cfg["threshold"] == 0.85
        assert cfg["output_format"] == "json"
        assert cfg["ecosystem"] == "python"
        assert cfg["no_informational"] is True
        assert cfg["ignore"] == ["safe-pkg-1", "safe-pkg-2"]

    def test_load_yaml_config(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / ".taintrace.yaml"
        cfg_file.write_text(
            """
threshold: 0.75
output_format: sarif
ecosystem: node
no_informational: false
ignore:
  - lodash-safe
  - express-safe
"""
        )
        cfg = load_config(cwd=tmp_path)
        assert cfg["threshold"] == 0.75
        assert cfg["output_format"] == "sarif"
        assert cfg["ecosystem"] == "node"
        assert cfg["no_informational"] is False
        assert "lodash-safe" in cfg["ignore"]

    def test_load_pyproject_toml(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / "pyproject.toml"
        cfg_file.write_text(
            """
[tool.taintrace]
threshold = 0.9
ignore = ["pyproject-ignored"]
"""
        )
        cfg = load_config(cwd=tmp_path)
        assert cfg["threshold"] == 0.9
        assert cfg["ignore"] == ["pyproject-ignored"]

    def test_load_custom_config_path(self, tmp_path: Path) -> None:
        custom = tmp_path / "custom_dir" / "my_config.toml"
        custom.parent.mkdir(parents=True)
        custom.write_text(
            """
threshold = 0.65
ignore = ["custom-pkg"]
"""
        )
        cfg = load_config(config_path=custom)
        assert cfg["threshold"] == 0.65
        assert cfg["ignore"] == ["custom-pkg"]


class TestEnvVarInterpolation:
    """Test environment variable interpolation in config files."""

    def test_interpolate_env_vars_in_strings_and_lists(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MY_TEST_TOKEN", "secret123")
        monkeypatch.setenv("MY_APP_ECOSYSTEM", "rust")

        raw = {
            "token": "${MY_TEST_TOKEN}",
            "ecosystem": "$MY_APP_ECOSYSTEM",
            "nested": ["$MY_TEST_TOKEN", "literal"],
        }
        interpolated = interpolate_env_vars(raw)
        assert interpolated["token"] == "secret123"
        assert interpolated["ecosystem"] == "rust"
        assert interpolated["nested"] == ["secret123", "literal"]


class TestConfigValidation:
    """Test schema validation and sanitization of config values."""

    def test_validate_valid_config(self) -> None:
        raw = {
            "threshold": "0.8",
            "format": "json",
            "ecosystem": "PYTHON",
            "no_informational": "true",
            "ignore": ["pkg-a", "pkg-b"],
            "unknown_future_key": "ignore_me",
        }
        validated = validate_config(raw)
        assert validated["threshold"] == 0.8
        assert validated["output_format"] == "json"
        assert validated["ecosystem"] == "python"
        assert validated["no_informational"] is True
        assert validated["ignore"] == ["pkg-a", "pkg-b"]
        assert "unknown_future_key" not in validated

    def test_validate_invalid_threshold_and_choices(self) -> None:
        raw = {
            "threshold": 1.5,  # Out of range (must be 0.0 - 1.0)
            "output_format": "invalid_format",
            "ecosystem": "non_existent_eco",
        }
        validated = validate_config(raw)
        assert "threshold" not in validated
        assert "output_format" not in validated
        assert "ecosystem" not in validated


class TestCliIntegrationAndOverrides:
    """Test CLI flags overriding config file defaults."""

    def test_cli_help_shows_config_option(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["check", "--help"])
        assert "--config" in result.output or "-c" in result.output

    def test_cli_flag_overrides_config_file(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / ".taintrace.toml"
        cfg_file.write_text(
            """
[taintrace]
threshold = 0.95
ignore = ["config-ignored-pkg"]
"""
        )

        lockfile = tmp_path / "requirements.txt"
        lockfile.write_text("requests==2.31.0\n")

        runner = CliRunner()
        # Explicit CLI threshold 0.50 should override config file threshold 0.95
        result = runner.invoke(
            cli,
            [
                "check",
                "--config",
                str(cfg_file),
                "--threshold",
                "0.50",
                str(lockfile),
            ],
        )
        assert result.exit_code == 0

    def test_config_ignore_merges_with_cli_ignore(self, tmp_path: Path) -> None:
        cfg_file = tmp_path / "custom.toml"
        cfg_file.write_text(
            """
[taintrace]
ignore = ["pkg-from-config"]
"""
        )

        lockfile = tmp_path / "requirements.txt"
        lockfile.write_text("pkg-from-config==1.0.0\npkg-from-cli==1.0.0\n")

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "check",
                "--config",
                str(cfg_file),
                "--ignore",
                "pkg-from-cli",
                str(lockfile),
            ],
        )
        assert result.exit_code == 0
