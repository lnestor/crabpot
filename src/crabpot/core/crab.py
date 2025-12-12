import shutil
import yaml

class Crab:
    def __init__(self, name, pot):
        self.pot = pot
        self.name = name
        self._read_substitutions()

    def create(self):
        self.get_path().mkdir(exist_ok=False)
        self.get_template_path().mkdir()
        self.get_substitution_path().touch()
        self.substitutions = {}

    def get_path(self):
        return self.pot.get_path() / self.name

    def get_template_path(self):
        return self.get_path() / "templates"

    def get_substitution_path(self):
        return self.get_path() / "substitutions.yaml"

    def has_template_file(self, filename):
        all_files = [path.name for path in self.get_template_path().iterdir() if path.is_file()]
        return filename in all_files

    def add_template(self, source_path):
        target_path = self.get_template_path() / source_path.name
        shutil.copy(source_path, target_path)

    def add_substitution(self, key, value):
        self.substitutions[key] = value
        self._write_substitutions()

    def _read_substitutions(self):
        if not self.get_substitution_path().exists():
            self.substitutions = {}
        else:
            with open(self.get_substitution_path()) as f:
                data = yaml.safe_load(f)
                self.substitutions = data if data is not None else {}

    def _write_substitutions(self):
        with open(self.get_substitution_path(), "w") as f:
            yaml.dump(self.substitutions, f)

    def __eq__(self, other):
        return self.name == other.name
