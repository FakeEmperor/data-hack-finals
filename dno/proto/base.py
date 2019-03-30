"""
Base library for interactions with the backend.
"""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Union


@dataclass
class BaseInteropBackend:

    @abstractmethod
    def get_map(self) -> dict:
        raise NotImplementedError()

    @abstractmethod
    def send_solution(self, solution: dict) -> Union[Map, Task]:
        raise NotImplementedError()
