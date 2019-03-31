import time
import numpy as np
from typing import Type, Tuple, Optional

from dno.model.model import Model
from dno.proto.backend import BackendInteraction
from dno.proto.mock import TaskReader
from dno.proto.data import Task, Solution, Map
from dno.proto import utils
from loguru import logger
from argparse import ArgumentParser, ArgumentTypeError


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ArgumentTypeError('Boolean value expected.')


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
    return mse


def run(task_num, model_class: Type[Model]=Model, debug: bool=True, prod: bool=True) -> Tuple[Optional[float], Optional[float]]:
    backend = BackendInteraction(backend_host='besthack19.sytes.net', backed_port=4242, auth="exp3ct0pat5onum")
    debug_score = None
    prod_score = None
    if debug:
        logger.warning(f"RUNNING DEBUGGING FOR TASK {task_num}...")
        debug_score = debug_task(model_class, task_num)
        logger.success(f"Final DEBUG score: {debug_score}")
    if debug and prod:
        logger.warning("WAITING SOME TIME FOR YOU TO SEE MUTHAR FACKER")
        time.sleep(10)
    if prod:
        logger.warning(f"RUNNING PRODUCTION FOR TASK {task_num}...")
        land_map = backend.start_task(task_num)
        model = model_class(land_map)
        task = backend.send_solution(Solution(ready=False))
        while not backend.session_ended:
            task = backend.send_solution(model.handle_task(task))
        prod_score = backend.results.score
        logger.success(f"Final PROD score: {prod_score}")
    return debug_score, prod_score


def main():
    default_task_num = 3
    parser = ArgumentParser()
    parser.add_argument("task_nums", type=int, nargs='+', metavar="task_nums",
                        help="task number to test on",
                        default=default_task_num)
    parser.add_argument("--debug", type=str2bool, nargs='?',
                        const=True, default=True,
                        help="enable or disable debug")
    parser.add_argument("--prod", type=str2bool, nargs='?',
                        const=True, default=True,
                        help="enable or disable prod")
    parser.add_argument("--logs", type=str2bool, nargs='?',
                        const=True, default=True,
                        help="enable or disable summary")
    parser.add_argument("--summary", type=str2bool, nargs='?',
                        const=True, default=True,
                        help="enable or disable summary")
    args = parser.parse_args()
    task_results = {}
    if len(args.task_nums) == 1 and args.task_nums[0] == -1:
        args.task_nums = list(range(1, 32))

    logger.warning(f"Starting inference for the following tasks: {args.task_nums}")
    if not args.logs:
        logger.warning("DISABLING LOGS for inferencing!")
        logger.disable('dno.model.model')
        logger.disable('dno.proto.data')
        logger.disable('dno.proto.backend')
    time.sleep(2)
    for task in args.task_nums:
        task_results[task] = run(task, debug=args.debug, prod=args.prod)
    if args.summary:
        logger.success(f"Summary for all {len(task_results)} tasks")
        for task_name, task_data in task_results.items():
            logger.success(f"Task {task_name}: "
                           f"debug={f'{1000*(1-task_data[0]):.2f}' if task_data[0] is not None else 'N/A'}, "
                           f"prod={f'{1000*(1-task_data[1]):.2f}' if task_data[1] is not None else 'N/A'}")


if __name__ == "__main__":
    main()
