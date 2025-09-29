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

def test_create_with_invalid_config_exits_as_failure(invalid_config):
    runner = CliRunner()
    result = runner.invoke(
        main,
        args=["create", str(invalid_config)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "invalid config" in result.stdout.lower()

def test_create_with_missing_template_exits_as_failure(tmp_path):
    path = tmp_path / "crabpot_config.py"
    path.write_text("""
from crabpot import Pot
pot = Pot()
pot.name = "mypot"
crab = pot.create_crab("mycrab")
crab.add_template_file("my_template.py.jinja", is_crab_config=True)
    """)

    runner = CliRunner()
    result = runner.invoke(
        main,
        args=["create", str(path)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "missing template" in result.stdout.lower()
    assert "mycrab: my_template.py.jinja" in result.stdout.lower()

def test_create_with_bad_syntax_config_exits_as_failure(tmp_path):
    path = tmp_path / "crabpot_config.py"
    path.write_text("""

    some error

    """)

    runner = CliRunner()
    result = runner.invoke(
        main,
        args=["create", str(path)],
        catch_exceptions=False
    )

    assert result.exit_code != 0
    assert "syntax error" in result.stdout.lower()
    assert "IndentationError" in result.stdout

def test_create_when_pot_exists_exits_as_failure(valid_config):
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
