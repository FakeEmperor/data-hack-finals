from math import sqrt
from dno.proto.data import Task, Solution, Map
from dno.proto.mock import TaskReader
import numpy as np
from typing import List, Optional
from time import time
from loguru import logger

class Model:
    def __init__(self, map_raw: Map, c: int=400, max_candidates: int=500_000,
                 time_limit: Optional[float]=1.8):
        self.max_candidates = max_candidates
        self.n: int = map_raw.data.shape[0]
        self.map_arr: np.ndarray = map_raw.data
        self.candidates: List[(int, int)] = []
        self.prev_cands: List[(int, int)] = []
        self.c: int = c
        self.ready: bool = False
        self.coords: (int, int) = None
        # TIME LIMITS HANDLING
        self._task_handle_start_time = None
        self._time_limit = time_limit

    def start_timing(self):
        self._task_handle_start_time = time()

    @property
    def has_time(self) -> bool:
        """
        Check if has time in time limit
        """
        if self._time_limit is not None:
            return (time() - self._task_handle_start_time) < self._time_limit
        return True

    def handle_task(self, task: Task) -> Solution:
        self.start_timing()
        if not self.ready:
            self._find_candidates(task)
            if len(self.candidates) == 1:
                self.ready = True
                y, x = self.candidates[0]
                self.coords = x, y
        else:
            x, y = self.coords
            new_x, new_y = x + task.vx, y + task.vy
            if new_x < 0:
                new_x += self.n/2
            if new_x > self.n:
                new_x -= self.n/2
            if new_y < 0:
                new_y += self.n/2
            if new_y > self.n:
                new_y -= self.n/2
            self.coords = max(0, new_x), max(0, new_y)  # KOSTYL for negative solutions
        return self._get_solution()

    def _get_solution(self) -> Solution:
        if not self.ready:
            return Solution(ready=False)
        else:
            return Solution(x=self.coords[0], y=self.coords[1], ready=True)

    # if [task.y, task.x] in self.candidates:
    #     print("Right point into candidates")

    def _find_candidates(self, task: Task):
        if not self.candidates:
            self._init_candidates(task)
        else:
            self.prev_cands = self.candidates
            self.candidates = self._filter_by_task(task)
        logger.info(f"Find candidates returned: {len(self.candidates)}")

    def _init_candidates(self, task: Task):
        for i in range(0, self.n):
            for j in range(0, self.n):
                delta = task.height - self.map_arr[j][i]
                # noinspection PyChainedComparisons
                if delta >= -self.c and delta <= self.c:
                    self.candidates.append([j, i])
            if not self.has_time:
                logger.warning(f"[candidates: {len(self.candidates)}] Breaking due to time limit ({self._time_limit})")
                return
            if self.max_candidates is not None and len(self.candidates) > self.max_candidates:
                logger.warning(f"[candidates: {len(self.candidates)}] Breaking since "
                               f"number of candidates > max ({self.max_candidates})...")
                return
                self.candidates = [(self.map_arr.shape[0] // 2, self.map_arr.shape[1] // 2)]

    def _filter_by_task(self, task: Task):
        next_candidates = []
        vx = int(round(task.vx))
        vy = int(round(task.vy))
        for candidate in self.candidates:
            next_x = candidate[0] + vx
            next_y = candidate[1] + vy
            if self.n > next_x >= 0 and self.n > next_y >= 0:
                delta = task.height - self.map_arr[next_x][next_y]
                # noinspection PyChainedComparisons
                if delta > -self.c and delta < self.c:
                    next_candidates.append([next_x, next_y])
            if not self.has_time:
                logger.warning(f"[candidates: {len(next_candidates)}] Breaking due to time limit...")
                break
        if not next_candidates:
            next_candidates.append(self.prev_cands[0])
        return next_candidates
