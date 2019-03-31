from math import sqrt
from dno.proto.data import Task, Solution, Map
from dno.proto.mock import TaskReader
import numpy as np
from typing import List


class Model:
    def __init__(self, map_raw: Map, c=400):
        self.n: int = map_raw.data.shape[0]
        self.map_arr: np.ndarray = map_raw.data
        self.candidates: List[(int, int)] = []
        self.prev_cands: List[(int, int)] = []
        self.c: int = c
        self.ready: bool = False
        self.coords: (int, int) = None

    def handle_task(self, task: Task) -> Solution:
        if not self.ready:
            self._find_candidates(task)
            if len(self.candidates) == 1:
                self.ready = True
                y, x = self.candidates[0]
                self.coords = x, y
        else:
            x, y = self.coords
            new_x, new_y = x + int(round(task.vx)), y + int(round(task.vy))
            self.coords = new_x, new_y

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

    def _init_candidates(self, task: Task):
        for i in range(0, self.n):
            for j in range(0, self.n):
                delta = task.height - self.map_arr[j][i]
                if delta >= -self.c and delta <= self.c:
                    self.candidates.append([j, i])

    def _filter_by_task(self, task: Task):
        next_candidates = []
        for candidate in self.candidates:
            next_x = candidate[0] + int(round(task.vy))
            next_y = candidate[1] + int(round(task.vx))
            if next_x < self.n and next_x >= 0 and next_y < self.n and next_y >= 0:
                delta = task.height - self.map_arr[next_x][next_y]
                if delta > -self.c and delta < self.c:
                    next_candidates.append([next_x, next_y])
        if not next_candidates:
            next_candidates.append(self.prev_cands[0])
        return next_candidates
