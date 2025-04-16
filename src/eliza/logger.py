# logger.py
import sys
import logging

try:
    from rich.console import Console
    from rich.text import Text
    from io import StringIO
    _rich_available = True
except ImportError:
    _rich_available = False

class VerbosityFilter(logging.Filter):
    def __init__(self, verbosity):
        self.verbosity = verbosity
    def filter(self, record):
        return getattr(record, "verbosity", 1) <= self.verbosity

class VerbosityLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        verbosity = None

        # Case: logger.info("...", v=2)
        if "v" in kwargs:
            verbosity = kwargs.pop("v")

        # Default to 1 if not specified
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        if verbosity is not None:
            kwargs["extra"]["verbosity"] = verbosity

        return msg, kwargs

# Internal logger (base)
_base_logger = logging.getLogger("eliza_logger")
_base_logger.setLevel(logging.INFO)

# Public adapter to be imported everywhere
logger = VerbosityLoggerAdapter(_base_logger, {})

def setup_logger(verbosity: int, color: str | None = None) -> None:
    _base_logger.handlers = []

    if verbosity == 0:
        _base_logger.addHandler(logging.NullHandler())
        return

    if color and _rich_available:
        handler = logging.StreamHandler(sys.stdout)

        class RichColorFormatter(logging.Formatter):
            def __init__(self, fmt, style_color):
                super().__init__(fmt)
                self.style_color = style_color

                # Use real console to detect capabilities
                preview_console = Console()
                self.color_system = preview_console.color_system
                self.force_terminal = preview_console.is_terminal

                # Create reusable buffer and rich console
                self.buf = StringIO()
                self.console = Console(
                    file=self.buf,
                    force_terminal=self.force_terminal,
                    color_system=self.color_system
                )
            
            def format(self, record):
                self.buf.seek(0)
                self.buf.truncate(0)
                base = super().format(record)
                self.console.print(Text(base, style=self.style_color), end="")
                return self.buf.getvalue()

        formatter = RichColorFormatter("%(message)s", color)
    else:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("%(message)s")

    handler.setFormatter(formatter)
    _base_logger.addHandler(handler)
    _base_logger.addFilter(VerbosityFilter(verbosity))
