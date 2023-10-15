import sys
from rich.console import Console
from rich import inspect
from rich.traceback import Traceback
from neo4j.exceptions import ServiceUnavailable
from utils.config_loader import ConfigLoader

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

    def handle_error(self, error):
        error_type = type(error)
        handler = self.error_handlers.get(error_type, self.generic_error)
        handler(error)

    def inspect_object(self, obj):
        self.console.print(f"[bold blue]Inspecting object[/bold blue]")
        self.console.print(f"{inspect(obj)}")

    def service_unavailable(self, error):
        self.console.print(f"[bold red]Service Unavailable:[/bold red] {error}")

    def key_error(self, error):
        self.console.print(f"[bold red]Key Error:[/bold red] {error}")

    def type_error(self, error):
        self.console.print(f"[bold red]Type Error:[/bold red] {error}")

    def value_error(self, error):
        self.console.print(f"[bold red]Value Error:[/bold red] {error}")

    def generic_error(self, message, exception=None):
        self.console.print(f"[bold red]Error:[/bold red] {message}")
        if exception:
            print(f"Error: {message}. Exception: {exception}")
        else:
            print(f"Error: {message}")

    def exception(self, exc_info):
        self.console.print(Traceback.from_exception(*exc_info))

    def success(self, message):
        # only print when GENERAL_CONFIG / DEBUG is set to True
        if self.config.get_general_config()['DEBUG']:
            self.console.print(f"[bold green]{message}[/bold green]")

    def debug_info(self, message):
        # only print when GENERAL_CONFIG / DEBUG is set to True
        if self.config.get_general_config()['DEBUG']:
            self.console.print(f"{message}")

    def warning(self, message):
        self.console.print(f"[bold yellow]{message}[/bold yellow]")


if __name__ == "__main__":
    error_handler = ErrorHandler()

    try:
        # Simulate a KeyError
        d = {}
        print(d['nonexistent_key'])
    except Exception as e:  # Catch all exceptions and pass to the handler
        error_handler.handle_error(e)
