from unittest.mock import patch

import pytest
from click.testing import CliRunner

from connectai.cli.commands import cli, start_fastapi_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_init(runner):
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert "Usage" in result.output


def test_start_group(runner):
    result = runner.invoke(cli, ["start"])
    assert result.exit_code == 0
    assert "Commands to start various entrypoints." in result.output


@patch("connectai.cli.commands.run")
def test_start_fastapi_cmd(mock_run):
    start_fastapi_cmd()
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "uvicorn" in args[0]
    assert "connectai.handlers.api.main:app" in args[0]


@patch("connectai.cli.commands.start_fastapi_cmd")
def test_start_fastapi(mock_start_fastapi_cmd, runner):
    result = runner.invoke(cli, ["start", "fastapi"])
    assert result.exit_code == 0
    mock_start_fastapi_cmd.assert_called_once()


@patch("connectai.cli.commands.start_fastapi_cmd")
def test_start_backend(mock_start_fastapi_cmd, runner):
    result = runner.invoke(cli, ["start", "backend"])
    assert result.exit_code == 0
    mock_start_fastapi_cmd.assert_called_once()
