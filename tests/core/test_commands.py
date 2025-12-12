from crabpot.core.commands import create_pot, get_pots, create_crab, get_crabs, add_template_file, add_substitution, generate
from crabpot.core.exceptions import EmptyNameError, ExistingNameError, InvalidNameError, MissingPotError, MissingTemplateError, MissingCrabError, DuplicateTemplateError
from crabpot.core.config import config
import pytest

def test_create_pot_creates_directory():
    create_pot("mypot")
    path = config.BASE_DIR / "mypot"
    assert path.exists()

def test_create_pot_with_empty_pot_name_throws_exception():
    with pytest.raises(EmptyNameError):
        create_pot("")

def test_create_pot_with_existing_pot_name_throws_exception():
    create_pot("mypot")

    with pytest.raises(ExistingNameError):
        create_pot("mypot")

def test_create_pot_with_invalid_name_throws_exception():
    with pytest.raises(InvalidNameError):
        create_pot(".. !@#$%")

def test_get_pots_returns_all_pots():
    create_pot("pot1")
    create_pot("pot2")
    create_pot("pot3")

    pots = get_pots()

    assert len(pots) == 3
    assert "pot1" in pots
    assert "pot2" in pots
    assert "pot3" in pots

def test_get_pots_when_base_dir_doesnt_exist_returns_empty_list():
    pots = get_pots()
    assert len(pots) == 0

def test_create_crab_creates_directory():
    create_pot("mypot")
    create_crab("mypot", "mycrab")
    path = config.BASE_DIR / "mypot" / "mycrab"
    assert path.exists()

def test_create_crab_with_missing_pot_name_throws_exception():
    with pytest.raises(MissingPotError):
        create_crab("missing", "mycrab")

def test_create_crab_with_empty_crab_name_throws_exception():
    create_pot("mypot")
    with pytest.raises(EmptyNameError):
        create_crab("mypot", "")

def test_create_crab_with_invalid_crab_name_throws_exception():
    create_pot("mypot")
    with pytest.raises(InvalidNameError):
        create_crab("mypot", "@#$@")

def test_create_crab_with_exising_crab_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")
    with pytest.raises(ExistingNameError):
        create_crab("mypot", "mycrab")

def test_get_crabs_returns_all_crabs():
    create_pot("mypot")
    create_crab("mypot", "mycrab1")
    create_crab("mypot", "mycrab2")
    create_crab("mypot", "mycrab3")

    crabs = get_crabs("mypot")

    assert len(crabs) == 3
    assert "mycrab1" in crabs
    assert "mycrab2" in crabs
    assert "mycrab3" in crabs

def test_get_crab_when_no_crabs_returns_empty_array():
    create_pot("mypot")
    crabs = get_crabs("mypot")
    assert len(crabs) == 0

def test_get_crab_when_pot_doesnt_exist_throws_exception():
    with pytest.raises(MissingPotError):
        get_crabs("missing")

def test_add_template_file_copies_file_to_working_directory(tmp_path):
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    template = tmp_path / "myfile.py.jinja"
    template.write_text("some template text")

    add_template_file("mypot", "mycrab", str(template))

    path = config.BASE_DIR / "mypot" / "mycrab" / "templates" / "myfile.py.jinja"
    assert path.exists()
    assert path.read_text() == "some template text"

def test_add_template_file_with_missing_pot_name_throws_exception():
    with pytest.raises(MissingPotError):
        add_template_file("missing", "mycrab", "myfile.py.jinja")

def test_add_template_file_with_missing_crab_name_throws_exception(tmp_path):
    create_pot("mypot")

    template = tmp_path / "myfile.py.jinja"
    template.write_text("some template text")

    with pytest.raises(MissingCrabError):
        add_template_file("mypot", "missing", str(template))

def test_add_template_file_with_missing_file_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(MissingTemplateError):
        add_template_file("mypot", "mycrab", "missing.py.jinja")

def test_add_template_file_with_same_name_as_existing_template_throws_exception(tmp_path):
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    template = tmp_path / "myfile.py.jinja"
    template.write_text("some template text")

    add_template_file("mypot", "mycrab", str(template))

    with pytest.raises(DuplicateTemplateError):
        add_template_file("mypot", "mycrab", str(template))

def test_add_substitution_writes_to_file():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    add_substitution("mypot", "mycrab", "somekey", "somevalue")
    add_substitution("mypot", "mycrab", "otherkey", "othervalue")

    path = config.BASE_DIR / "mypot" / "mycrab" / "substitutions.yaml"
    assert path.exists()
    assert "somekey: somevalue" in path.read_text()
    assert "otherkey: othervalue" in path.read_text()

def test_add_substitution_with_missing_pot_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(MissingPotError):
        add_substitution("missing", "mycrab", "somekey", "somevalue")

def test_add_substitution_with_missing_crab_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(MissingCrabError):
        add_substitution("mypot", "missing", "somekey", "somevalue")

def test_add_substitution_with_empty_key_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(ValueError):
        add_substitution("mypot", "missing", "", "somevalue")

def test_add_substitution_with_empty_value_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(ValueError):
        add_substitution("mypot", "missing", "somekey", "")

def test_add_substitution_subsequent_calls_overwrites_value():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    add_substitution("mypot", "mycrab", "somekey", "somevalue")
    add_substitution("mypot", "mycrab", "somekey", "othervalue")

    path = config.BASE_DIR / "mypot" / "mycrab" / "substitutions.yaml"
    assert path.exists()
    assert "somekey: othervalue" in path.read_text()

def test_generate_renders_template_files(tmp_path):
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    template = tmp_path / "myfile.py.jinja"
    template.write_text("{{ mysub }}")

    add_template_file("mypot", "mycrab", str(template))
    add_substitution("mypot", "mycrab", "mysub", "rendered")

    generate("mypot", "mycrab")

    path = config.BASE_DIR / "mypot" / "mycrab" / "myfile.py"
    assert path.exists()
    assert "rendered" in path.read_text()

def test_generate_with_missing_pot_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(MissingPotError):
        generate("missing", "mycrab")

def test_generate_with_missing_crab_name_throws_exception():
    create_pot("mypot")
    create_crab("mypot", "mycrab")

    with pytest.raises(MissingCrabError):
        generate("mypot", "missing")
