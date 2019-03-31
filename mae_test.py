import json
from typing import List
from loguru import logger

from dno.proto.utils import get_project_root


def mse(answers: List[dict], correct: List[dict], map_size: int):
    mse = 0
    for answer, correct in zip(answers, correct):
        if not answer['ready']:
            mse += 0.5
        else:
            err = (answer['x'] - correct['x']) ** 2 + (answer['y'] - correct['y']) ** 2
            err /= map_size**2
            mse += err
    mse /= len(answers)
    return mse


if __name__ == "__main__":
    root = get_project_root()
    task_name = 'task105'
    answer_data = json.loads((root / 'data' / 'finals' / f'{task_name}_answer.txt').read_text())
    correct_data = json.loads((root / 'data' / 'finals' / f'{task_name}.txt').read_text())
    image_size = 1081
    error = mse(answer_data, correct_data, map_size=1081)
    logger.success(f"MSE: {error}")
    logger.success(f"SCORE: {1000*(1-error):.0f}")
