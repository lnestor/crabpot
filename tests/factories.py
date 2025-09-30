from crabpot.pot import Pot
import pytest

@pytest.fixture
def create_pot():
    def _create_pot_impl(name="mypot", crabs=[]):
        pot = Pot(name)
        return pot

    return _create_pot_impl

@pytest.fixture
def create_crab(tmp_path):
    def _create_crab_impl(pot, status="unsubmitted"):
        num_crabs = len(pot.get_crabs())

        config_path = tmp_path / f"crab_config{num_crabs}.py.jinja"
        config_path.write_text("some text")

        crab = pot.create_crab(f"crab{num_crabs}")
        crab.add_template_file(str(config_path), is_crab_config=True)
        crab.status = status

        return crab

    return _create_crab_impl

