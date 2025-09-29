from click.testing import CliRunner
from crabpot.cli import main
from crabpot.pot import Pot
import pytest
from distutils import dir_util

@pytest.fixture
def valid_config(tmp_path):
    dir_util.copy_tree("tests/fixtures", str(tmp_path))
    return tmp_path / "valid_config.py"

@pytest.fixture
def invalid_config(tmp_path):
    dir_util.copy_tree("tests/fixtures", str(tmp_path))
    return tmp_path / "invalid_config.py"

@pytest.fixture
def bad_syntax_config(tmp_path):
    dir_util.copy_tree("tests/fixtures", str(tmp_path))
    return tmp_path / "bad_syntax_config.py"

def test_create_with_valid_config_creates_pot(valid_config):
    runner = CliRunner()
    runner.invoke(
        main,
        args=["create", str(valid_config)],
        catch_exceptions=False
    )

    assert Pot("SampleName").exists_on_disk()

def test_create_with_invalid_config_exits(invalid_config):
    runner = CliRunner()
    result = runner.invoke(
        main,
        args=["create", str(invalid_config)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "invalid config" in result.stdout.lower()

def test_create_with_bad_syntax_config_exists(bad_syntax_config):
    runner = CliRunner()
    result = runner.invoke(
        main,
        args=["create", str(bad_syntax_config)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "syntax error" in result.stdout.lower()

def test_create_when_pot_exists_exits(valid_config):
    runner = CliRunner()
    runner.invoke(
        main,
        args=["create", str(valid_config)],
        catch_exceptions=False
    )

    result = runner.invoke(
        main,
        args=["create", str(valid_config)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "already exists" in result.stdout.lower()
