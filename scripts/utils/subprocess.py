import subprocess


class SubprocessService:
    """
    Wrapper class for the subprocess module
    """

    DEFAULT_OPTS = {"stdout": subprocess.PIPE, "shell": False}

    def __init__(self, command: list[str], options: dict = None):
        self.command = command
        self.options = options or SubprocessService.DEFAULT_OPTS
        self.output = None

    def popen(self):
        """
        Run command in subprocess
        """
        self.output = subprocess.Popen(self.command, **self.options)
        return self

    def call(self) -> any:
        """
        Run command in subprocess
        """
        self.output = subprocess.call(self.command, **self.options)
        return self

    def check_output(self) -> any:
        """
        Run command in subprocess
        """
        self.output = subprocess.check_output(self.command, **self.options)
        return self

    def check_call(self) -> any:
        """
        Run command in subprocess
        """
        self.output = subprocess.check_call(self.command, **self.options)
        return self

    def run(self) -> any:
        """
        Run command in subprocess
        """
        self.output = subprocess.run(self.command, **self.options)
        return self

    def filter(self, toFilter: bool = True) -> any:
        """
        Filter output from subprocess
        """
        if toFilter:
            return SubprocessService.filter_output(self.output)
        return self.output

    @staticmethod
    def filter_output(subprocess_output):
        return subprocess_output.stdout.decode("utf-8").strip()
