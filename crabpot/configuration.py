from crabpot.exceptions import InvalidConfigError
import importlib.util
import sys

class Config:
    @classmethod
    def from_file(cls, filename):
        spec = importlib.util.spec_from_file_location("user_config", filename)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            return module.config
        except SyntaxError:
            raise InvalidConfigError

    def __init__(self):
        self.name = ""
