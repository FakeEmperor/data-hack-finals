import json
from pathlib import Path
from typing import Union, Sequence, Tuple, IO, BinaryIO, List
from loguru import logger

from dno.proto.data import Map, Solution, Task, Results
from dno.proto.base import BaseInteropBackend


class MockInterop(BaseInteropBackend):
    """
    MockInterop
    """
    def __init__(self, base_dir: Union[Path, str], task: str):
        self.base_dir = Path(base_dir)
        self.task = task
        self._reader = TaskReader(base_dir / task)
        self._map, self._tasks_and_score = self._reader.read_all()
        self.current_task_index = 0
        self._solutions: List[dict] = []

    @property
    def current_task(self) -> str:
        return self.task

    @property
    def num_tasks(self) -> int:
        """
        Get number of tasks in the mock
        """
        return len(self._tasks_and_score)

    def get_map(self) -> Map:
        """
        Get current map in mocked data
        :return: Map
        """
        return Map.from_dict(self._map)

    def send_solution(self, solution: Solution) -> Union[Task, Results]:
        if self.current_task_index > len(self._tasks_and_score):
            raise RuntimeError("You should stahp!")
        self._solutions.append(solution.to_dict())
        task_or_score = self._tasks_and_score[self.current_task_index]
        self.current_task_index += 1
        if "score" in task_or_score:
            return Results.from_dict(task_or_score)
        else:
            return Task.from_dict(task_or_score)


class TaskReader:
    """
    Govno dlya chteniya govna
    """

    def __init__(self, task_path: Union[str, Path]):
        self.task_path = Path(task_path)
        if not self.task_path.exists():
            raise FileNotFoundError(f"Error: can't find file \"{task_path}\"")
        self._io_wrapper: BinaryIO = None

    def __enter__(self):
        self._io_wrapper = open(self.task_path, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._io_wrapper.close()

    def read_all(self) -> Tuple[dict, Sequence[dict]]:
        with self:
            land_map = self.read_next_response(self._io_wrapper)
            tasks = []
            while True:
                next_size = self._io_wrapper.read(4)
                if len(next_size) < 4:
                    break
                tasks.append(self.read_next_response(self._io_wrapper, next_size))

        return land_map, tasks

    @staticmethod
    def to_int(data: Union[bytes, str]):
        data = bytes(data)
        if len(data) != 4:
            raise ValueError("Data should be 4 bytes long")
        return int.from_bytes(data, byteorder="little")

    @staticmethod
    def read_next_response(file: IO, packet_size: bytes=None):
        size = TaskReader.to_int(packet_size or file.read(4))
        return json.loads(file.read(size))


if __name__ == "__main__":
    test = TaskReader(r"E:\Source\Repos\ARGUS\PROJECTS\BEST.Hack\Finals\data\besthack19\task1")
    tests = test.read_all()
    logger.debug(tests)
