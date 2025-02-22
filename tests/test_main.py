from unittest.mock import patch


@patch("connectai.cli.commands.cli")
def test_cli_called(mock_cli):
    """Test if the cli() function is called when main.py is executed as __main__."""
    from connectai.__main__ import cli as main_cli_call

    main_cli_call()
    mock_cli.assert_called_once()
