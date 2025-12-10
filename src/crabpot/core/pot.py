from crabpot.core.config import config

class Pot:
    def __init__(self, name):
        self.name = name

    def create(self):
        path = config.BASE_DIR / self.name
        path.mkdir(parents=True, exist_ok=False)

    def __eq__(self, other):
        return self.name == other.name
