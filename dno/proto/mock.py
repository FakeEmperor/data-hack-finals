from pathlib import Path
from typing import Union, List, Optional
from loguru import logger

from dno.proto.data import Map, Solution, Task, Results, TaskReader
from dno.proto.base import BaseInteropBackend


class MockInterop(BaseInteropBackend):
    """
    MockInterop for interactions with local storage.
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

<<<<<<< HEAD
    def __init__(self, base_dir: Union[Path, str]):
        self.base_dir = Path(base_dir)

        self._map, self._tasks, self._score = None, None, None
        self._task = None
=======
    def __init__(self, base_dir: Union[Path, str], task_name: str):
        self.base_dir = Path(base_dir)
        self.task = task_name
        self._reader = TaskReader(base_dir / task_name)
        self._map, self._tasks, self._score = self._reader.read_all()
>>>>>>> 2650d543c790d66a33f3d51864b81b247b9dc65e
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
<<<<<<< HEAD
=======


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

    def read_all(self) -> Tuple[dict, Sequence[dict], dict]:
        with self:
            land_map = self.read_next_response(self._io_wrapper)
            tasks = []
            while True:
                next_size = self._io_wrapper.read(4)
                if len(next_size) < 4:
                    break
                tasks.append(self.read_next_response(self._io_wrapper, next_size))

        return land_map, tasks[:-1], tasks[-1]

    @staticmethod
    def to_int(data: Union[bytes, str]):
        data = bytes(data)
        if len(data) != 4:
            raise ValueError("Data should be 4 bytes long")
        return int.from_bytes(data, byteorder="little")

    @staticmethod
    def read_next_response(stream: IO, packet_size: bytes=None) -> dict:
        size = TaskReader.to_int(packet_size or stream.read(4))
        return json.loads(stream.read(size))


if __name__ == "__main__":
    test = TaskReader(r"E:\Source\Repos\ARGUS\PROJECTS\BEST.Hack\Finals\data\besthack19\task1")
    tests = test.read_all()
    logger.debug(tests)
>>>>>>> 2650d543c790d66a33f3d51864b81b247b9dc65e
