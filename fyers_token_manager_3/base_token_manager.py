import os
import pyotp

from abc import abstractmethod
from datetime import datetime
from pathlib import Path


class BaseTokenManager:
    def __init__(self) -> None:
        self.file_name: Path | None = None
        self.logs_path: Path | None = None
        self.data_path: Path | None = None

    def get_totp(self, totp_key: str) -> str:
        return pyotp.TOTP(totp_key).now()

    def set_access_token_file_name(self, path_name: str, unique_id: str) -> None:
        home_directory = os.path.expanduser("~")

        self.data_path = Path(
            f"{home_directory}/proalgotrader/{path_name}/data/{unique_id}"
        )

        self.logs_path = Path(
            f"{home_directory}/proalgotrader/{path_name}/logs/{unique_id}"
        )

        if not self.data_path.exists():
            self.data_path.mkdir(parents=True, exist_ok=True)

        if not self.logs_path.exists():
            self.logs_path.mkdir(parents=True, exist_ok=True)

        self.file_name = Path(self.data_path) / datetime.now().strftime("%Y-%m-%d")

    @abstractmethod
    def get_token(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def set_token(self, token: str) -> None:
        raise NotImplementedError

    def initialize(self) -> None:
        try:
            token = self.__read_file()
            self.set_token(token)
        except FileNotFoundError:
            token = self.__setup()
            self.set_token(token)

    def __setup(self) -> str:
        token = self.get_token()
        self.__write_file(token)
        return token

    def __read_file(self) -> str:
        with open(f"{self.file_name}", "r") as f:
            token = f.read()

        return token

    def __write_file(self, token: str) -> None:
        with open(f"{self.file_name}", "w") as f:
            f.write(token)
