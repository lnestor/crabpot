from crabpot.cli.main import main
from crabpot.core import create_pot
from click.testing import CliRunner

def test_cli_prints_all_pots():
    create_pot("pot1")
    create_pot("pot2")
    create_pot("pot3")

    runner = CliRunner()
    result = runner.invoke(main, args=["list-pots"])

    assert result.exit_code == 0
    assert "pot1" in result.output
    assert "pot2" in result.output
    assert "pot3" in result.output

def test_cli_when_no_pots_prints_message():
    runner = CliRunner()
    result = runner.invoke(main, args=["list-pots"])

    assert result.exit_code == 0
    assert "No pots found" in result.output
