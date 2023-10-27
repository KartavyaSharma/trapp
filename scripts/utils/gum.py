import constants

from . import process as sp


class Gum:
    """
    Wrapper class for the gum binary
    """

    path = constants.GUM_PATH

    @staticmethod
    def choose(opts: list[str]):
        """
        Runs the gum choose binary.
        @param opts options to pass onto gum
        @returns the output of gum choose
        """
        return sp.SubprocessService([f"{Gum.path}", "choose", *opts]).run().filter()

    @staticmethod
    def input(placeholder: str = None, opts: list[str] = None):
        """
        Runs gum input binary.
        @param opts options to pass onto gum
        @returns the output of gum input
        """
        if placeholder:
            opts = [f"--placeholder={placeholder}"] + ([*opts] if opts else [])
        return sp.SubprocessService([f"{Gum.path}", "input", *opts]).run().filter()
