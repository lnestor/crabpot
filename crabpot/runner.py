import subprocess

class CommandRunner:
    def run(self, *args, **kwargs):
        return subprocess.run(*args, **kwargs)

class TestRunner:
    def __init__(self):
        self.received_commands = []
        self.stdout = None

    def reset(self):
        self.received_commands = []
        self.stdout = None

    def set_stdout(self, stdout):
        self.stdout = stdout

    def run(self, *args, **kwargs):
        self.received_commands.append((*args, kwargs))

        class DummyResult:
            def __init__(self, stdout):
                self.stdout = stdout if stdout is not None else "fake stdout"
                self.stderr = "fake stderr"
                self.returncode = 0

        return DummyResult(self.stdout)

runner = CommandRunner()
