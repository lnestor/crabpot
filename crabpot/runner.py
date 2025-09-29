import subprocess

class CommandRunner:
    def run(self, *args, **kwargs):
        return subprocess.run(*args, **kwargs)

class TestRunner:
    def __init__(self):
        self.received_commands = []

    def reset(self):
        self.received_commands = []

    def run(self, *args, **kwargs):
        self.received_commands.append((*args, kwargs))

        class DummyResult:
            def __init__(self):
                self.stdout = "fake stdout"
                self.stderr = "fake stderr"
                self.returncode = 0
        return DummyResult()

runner = CommandRunner()
