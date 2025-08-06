from Modules import FileHandling
import os


class PasswordManager:
    def __init__(self, filename: str = "") -> None:
        """
        Initialize the PasswordManager with a filename.

        Args:
            - filename (str): The name of the file.

        Returns:
            - None
        """
        self.filename = filename

    def getValue(self, key: str) -> str:
        """
        Get the value of a key from the file.

        Args:
            - key (str): The key to get the value for.

        Returns:
            - str: The value of the key.
        """
        try:
            return FileHandling.openJson(self.filename)[key]
        except Exception as e:
            return os.getenv(key)
