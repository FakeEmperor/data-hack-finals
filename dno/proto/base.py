"""
Base library for interactions with the backend.
"""
from abc import abstractmethod
from dataclasses import dataclass
from typing import Union, Optional, Tuple

import pandas as pd

from dno.proto.data import Solution, Map, Task, Results


@dataclass
class BaseInteropBackend:

    @property
    @abstractmethod
    def current_task(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def start_task(self, task_name: str) -> Map:
        raise NotImplementedError()

    @abstractmethod
    def send_solution(self, solution: Solution) -> Union[Task, Results]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def session_ended(self) -> bool:
        raise NotImplementedError()

    @property
    @abstractmethod
    def current_iteration(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def results(self) -> Optional[Results]:
        """
        Task results when the last session has ended.
        """
        raise NotImplementedError()

    def get_csv(self, task_name: str) -> Tuple[Map, pd.DataFrame, Results]:
        """
        Get CSVs
        """
        map_data = self.start_task(task_name)
        tasks = []
        while not self.session_ended:
            tasks.append(self.send_solution(Solution(ready=False)))
        result = self.results
        frame = pd.DataFrame(data=[task.to_dict() for task in tasks[:-1]])
        return map_data, frame, result
