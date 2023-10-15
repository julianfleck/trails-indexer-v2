from unittest import TestCase
from unittest.mock import patch, Mock
from utils.error_handler import ErrorHandler  # Adjust the import path as needed

class TestErrorHandler(TestCase):
    def setUp(self):
        self.error_handler = ErrorHandler()
        self.mock_console = Mock()
        self.error_handler.console = self.mock_console  # Mock the console object in the ErrorHandler instance

    def test_service_unavailable(self):
        error_message = "Service Unavailable: Test Error"
        self.error_handler.service_unavailable(error_message)
        self.mock_console.print.assert_called_once_with("[bold red]Service Unavailable:[/bold red] " + error_message)

    def test_key_error(self):
        error_message = "Key Error: Test Error"
        self.error_handler.key_error(error_message)
        self.mock_console.print.assert_called_once_with("[bold red]Key Error:[/bold red] " + error_message)

    def test_type_error(self):
        error_message = "Type Error: Test Error"
        self.error_handler.type_error(error_message)
        self.mock_console.print.assert_called_once_with("[bold red]Type Error:[/bold red] " + error_message)

    def test_generic_error(self):
        error_message = "Error: Test Error"
        self.error_handler.generic_error(error_message)
        self.mock_console.print.assert_called_once_with("[bold red]Error:[/bold red] " + error_message)

    def test_exception(self):
        try:
            1 / 0  # This will raise a ZeroDivisionError
        except Exception as e:
            exc_info = (type(e), e, e.__traceback__)
            self.error_handler.exception(exc_info)
        
        self.mock_console.print.assert_called_once()
