from pathlib import Path
from typing import Union, List, Optional
from loguru import logger

from dno.proto.data import Map, Solution, Task, Results, TaskReader
from dno.proto.base import BaseInteropBackend


class MockInterop(BaseInteropBackend):
    """
    MockInterop
    """

    @property
    def session_ended(self) -> bool:
        """
        True when session has ended.
        """
        return len(self._solutions) >= len(self._tasks)

    @property
    def current_iteration(self) -> int:
        return len(self._solutions)

    def __init__(self, base_dir: Union[Path, str]):
        self.base_dir = Path(base_dir)

        self._map, self._tasks, self._score = None, None, None
        self._task = None
        self._solutions: List[dict] = []
        self._actual_score: Results = None

    @property
    def results(self) -> Optional[Results]:
        return self._actual_score

    @property
    def current_task(self) -> str:
        """
        Current task name.
        """
        return self._task

    @property
    def num_tasks(self) -> int:
        """
        Get number of tasks in the mock.
        """
        return len(self._tasks)

    def start_task(self, task_name: str) -> Map:
        """
        Start task session and get the current map.
        :return: Map instance.
        """
        logger.debug(f"Starting mock backend interaction {task_name}")
        reader = TaskReader(self.base_dir / task_name)
        self._solutions = []
        self._task = task_name
        self._actual_score = None
        self._map, self._tasks, self._score = reader.read_all()
        return Map.from_dict(self._map)

    def send_solution(self, solution: Solution) -> Union[Task, Results]:
        """
        Send solution to the backend and receive either new task or results.
        :param solution:  Solution to send.
        :return:          Either task or results.
        """
        if self.session_ended:
            raise RuntimeError("You should stahp!")
        self._solutions.append(solution.to_dict())
        if self.session_ended:  # last iteration
            self._actual_score = Results.from_dict(self._score)
            return self._actual_score
        else:
            return Task.from_dict(self._tasks[len(self._solutions)]['data'])
