import click
import subprocess
import pathlib
import pickle as pkl
from crabpot.constants import CRABPOT_DIR

def load_pot(pot_name):
    path = pathlib.Path(f"{CRABPOT_DIR}/{pot_name}/pot.pkl")
    if not path.exists():
        return None
    else:
        with open(str(path), "rb") as f:
            return pkl.load(f)
    
class DefaultCertification():
    def check_cmsenv(self):
        result = subprocess.run(
            ["bash", "-c", "echo $CMSSW_BASE"],
            capture_output=True,
            text=True,
            check=True
        )

        return len(result.stdout.strip()) > 0

    def check_grid_cert(self):
        try:
            result = subprocess.run(
                ["voms-proxy-info", "-timeleft"],
                capture_output=True,
                text=True,
                check=True
            )

            timeleft_str = result.stdout.strip()

            if not timeleft_str.isdigit():
                return False

            timeleft = int(timeleft_str)
            return timeleft > 0
        except FileNotFoundError:
            raise click.ClickException(
                "Could not find `voms-proxy-info`."
                "Make sure the grid tools are installed and available in your PATH."
            )

class TestCertification():
    def __init__(self):
        self.has_valid_cmsenv = True
        self.has_valid_grid_cert = True

    def check_cmsenv(self):
        return self.has_valid_cmsenv

    def check_grid_cert(self):
        return self.has_valid_grid_cert

cert = DefaultCertification()
