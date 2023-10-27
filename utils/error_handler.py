import sys
from rich.console import Console
from rich import inspect
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.status import Status
from rich.traceback import Traceback
from rich.live import Live
from neo4j.exceptions import ServiceUnavailable
from utils.config_loader import ConfigLoader

class Timestamp:
    def __init__(self):
        from datetime import datetime
        self.now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ErrorHandler:
    def __init__(self):
        self.console = Console()
        self.config = ConfigLoader()
        self.error_handlers = {
            ServiceUnavailable: self.service_unavailable,
            KeyError: self.key_error,
            TypeError: self.type_error,
            ValueError: self.value_error,
            Exception: self.exception
            # ... other error types ...
        }
        self.timestamp = "[grey30][" + Timestamp().now + f"][/grey30]"
        self.timestamp_success = "[green][" + Timestamp().now + f"] •[/green]"
        self.timestamp_warning = "[orange][" + Timestamp().now + f"] •[/orange]"
        self.timestamp_error = "[red][" + Timestamp().now + f"] •[/red]"

    def handle_error(self, error):
        error_type = type(error)
        handler = self.error_handlers.get(error_type, self.generic_error)
        handler(error)

    def inspect_object(self, obj):
        self.console.print(f"[bold blue]Inspecting object[/bold blue]")
        self.console.print(f"{inspect(obj)}")

    def track_status(self, func, *args, description="Processing..."):
        """
        Display a progress bar with the given description while executing the provided function.
        Returns the result of the executed function.
        """
        result = None
        self.console.print(self.timestamp + f" {description}")
        # with Status(f"Running – {description}", spinner="point") as status:
        with Progress(
            SpinnerColumn(spinner_name="point", style="bold blue"),
            TextColumn("        "),
            TimeElapsedColumn(),
            # *Progress.get_default_columns(),
            TextColumn(" [progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task(f"Running...", total=None)
            try:
                result = func(*args)
            except Exception as e:
                self.console.print(self.timestamp_error + f"Error: {e}")
                self.exception(sys.exc_info())
                raise e
        return result

    def service_unavailable(self, error):
        self.console.print(f"[bold red]Service Unavailable:[/bold red] {error}")

    def key_error(self, error):
        self.console.print(f"[bold red]Key Error:[/bold red] {error}")

    def type_error(self, error):
        self.console.print(f"[bold red]Type Error:[/bold red] {error}")

    def value_error(self, error):
        self.console.print(f"[bold red]Value Error:[/bold red] {error}")

    def generic_error(self, message, exception=None):
        self.console.print(self.timestamp_error + f" {message}")
        if exception:
            self.console.inspect(exception)

    def exception(self, exc_info):
        self.console.print(Traceback.from_exception(*exc_info))

    def success(self, message):
        # only print when GENERAL_CONFIG / DEBUG is set to True
        if self.config.get_general_config()['DEBUG']:
            self.console.print(self.timestamp_success + f" {message}")

    def debug_info(self, message):
        # only print when GENERAL_CONFIG / DEBUG is set to True
        if self.config.get_general_config()['DEBUG']:
            self.console.print(self.timestamp + f" {message}")

    def warning(self, message):
            self.console.print(self.timestamp_warning + f" {message}")


if __name__ == "__main__":
    error_handler = ErrorHandler()

    try:
        # Simulate a KeyError
        d = {}
        print(d['nonexistent_key'])
    except Exception as e:  # Catch all exceptions and pass to the handler
        error_handler.handle_error(e)
