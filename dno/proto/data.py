"""

"""
import json
from dataclasses import dataclass, asdict
from io import RawIOBase
from pathlib import Path
from typing import NamedTuple, Union, Tuple, Sequence, BinaryIO, IO
import numpy as np
from loguru import logger


@dataclass
class Map:
    data: np.ndarray

    def region(self, x: int, y: int, size: tuple) -> np.ndarray:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict):
        size = int(np.sqrt(len(data["map"])))
        return cls(data=np.asarray(data["map"]).reshape(size, size))


@dataclass
class Task:
    """
    Data point
    """
    x: int = 0
    y: int = 0
    height: int = 0
    speed: int = 0
    psi: int = 0
    _psi_cos: np.float = 0
    _psi_sin: np.float = 0

    def __post_init__(self):
        self._psi_cos = np.cos(np.deg2rad(self.psi))
        self._psi_sin = np.sin(np.deg2rad(self.psi))

    @property
    def vy(self) -> float:
        """
        Since 0 grad is east ( ---> ), and 90 grad is north (^):
          multuply by COSINE to get VY.
        """
        return self.speed * self._psi_cos

    @property
    def vx(self) -> float:
        """
        Since 0 grad is east ( ---> ), and 90 grad is north (^):
         multiply by SINE to get VX.
        """
        return self.speed * self._psi_sin

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """
        Deserialize from data dictionary.
        """
        try:
            return Task(speed=data['speed'],
                        psi=data['psi'],
                        x=data['x'],
                        height=data['height'],
                        y=data['y'])
        except KeyError as e:
            raise KeyError(f"Invalid data {data} to deserialize from task: {e.args[0]}")

    def to_dict(self) -> dict:
        """
        Serialize into dictionary.
        """
        return {
            **asdict(self),
            **{
                "vx": self.vx,
                "vy": self.vy
            }
        }


class Solution(NamedTuple):
    """
    Solution to the task point.
    """
    x: int = 0
    y: int = 0
    ready: bool = True

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "ready": self.ready,
        }


class Results(NamedTuple):
    """
    Results after task finishes
    """
    score: float

    @classmethod
    def from_dict(cls, data: dict) -> 'Results':
        """
        Deserialize from data dictionary.
        """
        return Results(score=data['scores'])


class TaskReader:
    """
    Govno dlya chteniya govna
    """

    def __init__(self, task_path: Union[str, Path]):
        self.task_path = Path(task_path)
        if not self.task_path.exists():
            raise FileNotFoundError(f"Error: can't find file \"{task_path}\"")
        self._io_wrapper: RawIOBase = None

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
    def read_next_response(file: RawIOBase, packet_size: bytes=None):
        logger.debug("Reading response...")
        size = TaskReader.to_int(packet_size or file.read(4))
        logger.debug(f"Response size is '{size}' bytes...")
        data = b''
        while len(data) < size:
            to_read = size - len(data)
            chunk = file.read(to_read)
            data += chunk
            if len(chunk) == 0:
                raise ValueError(f"Received a null-length data when expecting {to_read} bytes!")
            logger.debug(f"Chunk size: {len(chunk)}")
        data = data.decode()
        logger.debug(f"Response data is {data}")
        return json.loads(data)


if __name__ == "__main__":
    test = TaskReader(r"E:\Source\Repos\ARGUS\PROJECTS\BEST.Hack\Finals\data\besthack19\task1")
    tests = test.read_all()
    logger.debug(tests)
