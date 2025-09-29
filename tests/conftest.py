import pytest
import crabpot.runner
import crabpot.util
import pathlib
import shutil
from distutils import file_util

@pytest.fixture(autouse=True)
def create_crabpot_dir():
    path = pathlib.Path(".crabpot")
    if path.exists():
        shutil.rmtree(path)

    path.mkdir()
    yield
    shutil.rmtree(path)

@pytest.fixture(autouse=True)
def cmd_runner():
    crabpot.runner.runner = crabpot.runner.TestRunner()
    yield crabpot.runner.runner
    crabpot.runner.runner = crabpot.runner.CommandRunner()

@pytest.fixture(autouse=True)
def replace_cert():
    crabpot.util.cert = crabpot.util.TestCertification()
    yield
    crabpot.util.cert = crabpot.util.DefaultCertification()

@pytest.fixture()
def set_valid_cmsenv():
    def _set_valid_cmsenv(value):
        crabpot.util.cert.has_valid_cmsenv = value

    return _set_valid_cmsenv

@pytest.fixture()
def set_valid_grid_cert():
    def _set_valid_grid_cert(value):
        crabpot.util.cert.has_valid_grid_cert = value

    return _set_valid_grid_cert

@pytest.fixture
def get_config(tmp_path):
    def _get_config(filename):
        file_util.copy_file(f"tests/fixtures/{filename}", str(tmp_path))
        return tmp_path / filename

    return _get_config
