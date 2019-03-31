from math import sqrt
import numpy as np
import sys
sys.path.append("..")
from dno.proto.data import Task
from dno.proto.mock import TaskReader

class PetrFinder:
    def __init__(self, map_raw, c=400):
        self.n = int(sqrt(len(map_raw["map"])))
        self.map_arr = np.array(map_raw["map"]).reshape(self.n, self.n)
        self.candidates = []
        self.prev_cands = []
        self.c = c
        self.prev_speed = 0

    def handle_task(self, task: Task):
        if not self.candidates:
            self.init_candidates(task)
        else:
            self.prev_cands = self.candidates
            self.candidates = self.filter_by_task(task)
        if [task.y, task.x] in self.candidates:
            print("Right point into candidates")


    def init_candidates(self, task: Task):
        for i in range(0, self.n):
            for j in range(0, self.n):
                delta = task.height - self.map_arr[j][i]
                if delta >= -self.c and delta <= self.c:
                    self.candidates.append([j, i])

    def filter_by_task(self, task: Task):
        next_candidates = []
        if task.speed == 0:
            task.speed = self.prev_speed
        else:
            self.prev_speed = task.speed
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



f = open("..\\govnoresult.txt", "w")

def test(task_num):
    tr = TaskReader("..\\data\\besthack19\\task" + str(task_num))
    map_raw, data_raw, _ = tr.read_all()
    print(f"Handeling {task_num} task")
    pf = PetrFinder(map_raw)
    cand_tmp = None
    last_data = None
    iters = 0
    for data in data_raw:
        iters += 1
        d = Task.from_dict(data["data"])
        pf.handle_task(d)
        cand_tmp = pf.candidates
        print(len(pf.candidates))
        if(len(pf.candidates) > 60000):
            pf.candidates = pf.candidates[:59000]
        last_data = data["data"]
        if len(pf.candidates) == 1:
            break
    f.write(str(cand_tmp) + "\n")
    f.write("[" + str(last_data["y"]) + ", " + str(last_data["x"]) + "]\n")
    f.write(f"Iters: {iters}\n")

for i in range(1,32):
    f.write(f"TASK{i}========================\n")
    test(i)