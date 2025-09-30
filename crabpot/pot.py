from crabpot.constants import CRABPOT_DIR
from crabpot.configuration import Config
import pathlib
import pickle as pkl
from crabpot.crab import Crab
from pathlib import Path

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
        path.mkdir(parents=True, exist_ok=True)

        with open(f"{CRABPOT_DIR}/{self.name}/pot.pkl", "wb") as f:
            pkl.dump(self, f)

    def create_crab(self, name):
        crab = Crab(name, self)
        self._crabs.append(crab)
        return crab

    def get_unsubmitted_crabs(self):
        return self._crabs

    def get_crab(self, name):
        for c in self._crabs:
            if c.name == name:
                return c

        return None

    def get_crabs(self, status=None):
        if status is None:
            return self._crabs
        else:
            return [c for c in self._crabs if c.status == status]
