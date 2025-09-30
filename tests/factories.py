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
        num_crabs = pot.get_crabs()

        config_path = tmp_path / f"crab_config{num_crabs}.py"
        config_path.write_text("some text")

        crab = pot.create_crab(f"crab{num_crabs}")
        crab.add_template_file(str(config_path))
        crab.status = status

    return _create_crab_impl

