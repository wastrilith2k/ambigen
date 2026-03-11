"""Tests for CLI commands."""

from click.testing import CliRunner

from ambigen.cli import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "ambigen" in result.output


def test_generate_dry_run():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate", "presets/cozy_tavern.yaml", "--dry-run"])
    assert result.exit_code == 0
    assert "Cozy Tavern" in result.output
    assert "dry run" in result.output


def test_validate():
    runner = CliRunner()
    result = runner.invoke(cli, ["validate", "presets/cozy_tavern.yaml"])
    assert result.exit_code == 0
    assert "Cozy Tavern" in result.output
