import crabpot.core.config
import pytest

@pytest.fixture(autouse=True)
def set_base_dir(tmp_path):
    crabpot.core.config.config.BASE_DIR = tmp_path / ".crabpot"
