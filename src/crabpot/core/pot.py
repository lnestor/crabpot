from crabpot.core.config import config
from crabpot.core.exceptions import MissingPotError

class Pot:
    def __init__(self, name):
        self.name = name

    @classmethod
    def load(cls, name):
        pot = Pot(name)
        if not pot.exists():
            raise MissingPotError

        return pot

    def exists(self):
        return self.get_path().exists()

    def create(self):
        self.get_path().mkdir(parents=True, exist_ok=False)

    def get_path(self):
        return config.BASE_DIR / self.name

    def get_crabs(self):
        return [subpath.name for subpath in self.get_path().iterdir() if subpath.is_dir()]

    def create_crab(self, name):
        path = self.get_path() / name
        path.mkdir(exist_ok=False)

    def __eq__(self, other):
        return self.name == other.name
