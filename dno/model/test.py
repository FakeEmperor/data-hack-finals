import time
from typing import Type

from dno.model.model import Model
from dno.proto.backend import BackendInteraction
from dno.proto.mock import TaskReader
from dno.proto.data import Task, Solution, Map
from dno.proto import utils
from loguru import logger
from argparse import ArgumentParser


def debug_task(model_class: Type[Model], task_num: int):
    task_reader = TaskReader(utils.get_task_path(task_num))
    land_map, tasks, _ = task_reader.read_all()
    land_map = Map.from_dict(land_map)
    model = model_class(land_map)
    tasks = list(map(lambda t: Task.from_dict(t['data']), tasks))
    mse = 0
    for task in tasks:
        sol = model.handle_task(task)
        if not sol.ready:
            mse += 0.5
        else:
            err = (sol.x - task.x) ** 2 + (sol.y - task.y) ** 2
            err /= (land_map.data.shape[0] * land_map.data.shape[1])
            mse += err
    mse /= len(tasks)
    logger.success(f'Task: {task_num} MSE: {mse}')


def run(task_num, model_class: Type[Model]=Model, debug: bool=True):
    backend = BackendInteraction(backend_host='besthack19.sytes.net', backed_port=4242, auth="exp3ct0pat5onum")
    if debug:
        logger.warning(f"RUNNING DEBUGGING FOR TASK {task_num}...")
        debug_task(model_class, task_num)
        logger.warning("WAITING SOME TIME FOR YOU TO SEE MUTHAR FACKER")
        time.sleep(10)
    logger.warning(f"Starting remote production tests...")
    land_map = backend.start_task(task_num)
    model = model_class(land_map)
    task = backend.send_solution(Solution(ready=False))
    while not backend.session_ended:
        task = backend.send_solution(model.handle_task(task))
    logger.success(f"Final score: {backend.results}")


if __name__ == "__main__":
    default_task_num = 23
    parser = ArgumentParser()
    parser.add_argument("task_num", type=int, metavar="task_num",
                        help="task number to test on",
                        default=default_task_num)
    args = parser.parse_args()
    run(args.task_num)
