import subprocess

class CommandRunner:
    def run(self, *args, **kwargs):
        return subprocess.run(*args, **kwargs)

class TestRunner:
    def __init__(self):
        self.recv_cmds = []
        self.mocks = {}

    def reset(self):
        self.recv_cmds = []
        self.mocks = {}

    def mock_return(self, command, stdout):
        self.mocks[command] = stdout

    def cmd(self, command, **kwargs):
        class DummyResult:
            def __init__(self, stdout="fake stdout", stderr="fake stderr", exit_code=0):
                self.stdout = stdout if stdout is not None else "fake stdout"
                self.stderr = stderr
                self.returncode = exit_code

        self.recv_cmds.append((command, kwargs))
        return DummyResult(stdout=self.mocks.get(command, ""))

runner = CommandRunner()
