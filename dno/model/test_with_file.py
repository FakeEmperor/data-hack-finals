from dno.model.model import Model
from dno.proto.mock import TaskReader
from dno.proto.data import Task, Map
from dno.proto import utils

if __name__ == "__main__":
    task_num = 2
    task_reader = TaskReader(utils.get_task_path(task_num))
    land_map, tasks, _ = task_reader.read_all()
    land_map = Map.from_dict(land_map)
    tasks = list(map(lambda t: Task.from_dict(t['data']), tasks))
    model = Model(map_raw=land_map)
    mse = 0
    for task in tasks:
        sol = model.handle_task(task)
        if not sol.ready:
            mse += 0.5
        else:
            err =  (sol.x - task.x) ** 2 + (sol.y - task.y) ** 2
            err /= land_map.data.size
            mse += err
    mse /= len(tasks)
    print(f'Task: {task_num} MSE: {mse}')


