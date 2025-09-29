from crabpot.constants import CRABPOT_DIR
from crabpot.configuration import Config
import pathlib
import pickle as pkl
from crabpot.crab import Crab


class Pot:
    def __init__(self, name=""):
        self.name = name
        self.defaults = {}
        self._crabs = []

    def exists_on_disk(self):
        path = pathlib.Path(f"{CRABPOT_DIR}/{self.name}")
        return path.exists()

    def save(self):
        path = pathlib.Path(f"{CRABPOT_DIR}/{self.name}")
        path.mkdir()

        with open(f"{CRABPOT_DIR}/{self.name}/pot.pkl", "wb") as f:
            pkl.dump(self, f)

    def create_crab(self, name):
        crab = Crab(name, self)
        self._crabs.append(crab)
        return crab

    def get_unsubmitted_crabs(self):
        return self._crabs
