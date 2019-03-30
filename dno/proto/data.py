"""

"""
from dataclasses import dataclass, asdict
from typing import NamedTuple
import numpy as np


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
        return Task(speed=data['speed'],
                    psi=data['psi'],
                    x=data['x'],
                    height=data['height'],
                    y=data['y'])

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
