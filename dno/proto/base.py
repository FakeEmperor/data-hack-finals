"""
Base library for interactions with the backend.
"""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Union

from dno.proto.data import Solution, Map, Task, Results


@dataclass
class BaseInteropBackend:

    @property
    @abstractmethod
    def current_task(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_map(self) -> Map:
        raise NotImplementedError()

    @abstractmethod
    def send_solution(self, solution: Solution) -> Union[Task, Results]:
        raise NotImplementedError()
