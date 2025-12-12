from crabpot.core.config import config
from crabpot.core.exceptions import MissingPotError
from crabpot.core.crab import Crab

class Pot:
    def __init__(self, name):
        self.name = name

    def exists(self):
        return self.get_path().exists()

    def create(self):
        self.get_path().mkdir(parents=True, exist_ok=False)

    def get_path(self):
        return config.BASE_DIR / self.name

    def get_crab(self, crab_name):
        all_crabs = self.get_crabs()
        crab = [c for c in all_crabs if c.name == crab_name]
        return crab[0]

    def get_crabs(self):
        return [Crab(subpath.name, self) for subpath in self.get_path().iterdir() if subpath.is_dir()]

    def has_crab(self, crab_name):
        return crab_name in [c.name for c in self.get_crabs()]

    def create_crab(self, name):
        crab = Crab(name, self)
        crab.create()
        return crab

    def __eq__(self, other):
        return self.name == other.name
