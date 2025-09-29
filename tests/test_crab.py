from crabpot.pot import Pot
import pytest
from crabpot.exceptions import CrabpotError

def test_generate_when_no_substitutions_creates_exact_file_with_extension(tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("some generic text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)
    crab.generate()

    files = crab.get_generated_files()
    assert len(files) == 1

    with open(files[0]) as f:
        content = f.read()

    assert "some generic text" in content
    assert "config.General.workArea = \".crabpot/mypot/crab/crab_dir\"" in content

def test_generate_when_substitutions_replaces_values(tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("aaaa {{ test1 }} {{ test2 }}")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)
    crab.substitutions = {"test1": "hey1", "test2": "hey2"}
    crab.generate()

    files = crab.get_generated_files()
    assert len(files) == 1

    with open(files[0]) as f:
        content = f.read()

    assert "aaa hey1 hey2" in content

def test_generate_with_multiple_templates_creates_all(tmp_path):
    path1 = tmp_path / "crab_config.py.jinja"
    path1.write_text("aaaa {{ unique1 }} {{ shared }}")

    path2 = tmp_path / "other_file.py.jinja"
    path2.write_text("aaaa {{ unique2 }} {{ shared }}")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path1), is_crab_config=True)
    crab.add_template_file(str(path2))
    crab.substitutions = {"unique1": "test1", "unique2": "test2", "shared": "test3"}
    crab.generate()

    files = crab.get_generated_files()
    assert len(files) == 2

    with open(files[0]) as f:
        content = f.read()

    assert "aaaa test1 test3" in content
    assert "config.General.workArea = \".crabpot/mypot/crab/crab_dir\"" in content

    with open(files[1]) as f:
        content = f.read()

    assert content == "aaaa test2 test3"

def test_generate_with_no_crab_config_throws_error(tmp_path):
    path = tmp_path / "some_file.py.jinja"
    path.write_text("some generic text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path))

    with pytest.raises(CrabpotError):
        crab.generate()

def test_generate_With_multiple_crab_configs_throws_error(tmp_path):
    path1 = tmp_path / "crab_config1.py.jinja"
    path1.write_text("some generic text")

    path2 = tmp_path / "crab_config2.py.jinja"
    path2.write_text("some generic text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path1), is_crab_config=True)
    crab.add_template_file(str(path2), is_crab_config=True)

    with pytest.raises(CrabpotError):
        crab.generate()

def test_generate_with_missing_substitutions_throws_error(tmp_path):
    path = tmp_path / "crab_config.py.jinja"
    path.write_text("aaaa {{ test1 }} {{ test2 }}")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)
    crab.substitutions = {"test1": "hey1"}

    with pytest.raises(CrabpotError):
        crab.generate()

def test_get_crab_config_returns_proper_filename(tmp_path):
    path = tmp_path / "special_name.py.jinja"
    path.write_text("some text")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path), is_crab_config=True)

    assert crab.get_crab_config() == ".crabpot/mypot/crab/special_name.py"

def test_get_generated_files_returns_all_files(tmp_path):
    path1 = tmp_path / "crab_config.py.jinja"
    path1.write_text("aaaa {{ unique1 }} {{ shared }}")

    path2 = tmp_path / "other_file.py.jinja"
    path2.write_text("aaaa {{ unique2 }} {{ shared }}")

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.add_template_file(str(path1), is_crab_config=True)
    crab.add_template_file(str(path2))
    crab.substitutions = {"unique1": "test1", "unique2": "test2", "shared": "test3"}
    crab.generate()

    files = crab.get_generated_files()
    assert len(files) == 2

    assert files[0] == ".crabpot/mypot/crab/crab_config.py"
    assert files[1] == ".crabpot/mypot/crab/other_file.py"

def test_get_crab_dir_returns_crab_directory():
    pot = Pot("mypot")
    crab = pot.create_crab("crab")

    assert crab.get_crab_dir() == ".crabpot/mypot/crab/crab_dir"

def test_set_crab_dir_overrides_crab_directory():
    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.set_crab_dir("path/to/some/dir")

    assert crab.get_crab_dir() == "path/to/some/dir"

def test_set_crab_dir_when_dir_exists_sets_status_to_submitted(tmp_path):
    path = tmp_path / "some/dir"
    path.mkdir(parents=True)

    pot = Pot("mypot")
    crab = pot.create_crab("crab")
    crab.set_crab_dir(str(path))

    assert crab.status == "submitted"

