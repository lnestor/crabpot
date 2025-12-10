import pathlib

class CrabpotConfig:
    BASE_DIR = pathlib.Path.home() / ".crabpot"

config = CrabpotConfig()
