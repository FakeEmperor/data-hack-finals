from pathlib import Path
from typing import Optional

TASK_PATH_TEMPLATE = 'data/besthack19/task{}'

def get_project_root()-> Optional[Path]:
    current_dir = Path.cwd()
    while True:
        if (current_dir / '.git').exists():
            return current_dir
        if current_dir.parent != current_dir:
            current_dir = current_dir.parent
        else:
            return None

def get_task_path(task_number: int) -> Path:
    result = get_project_root() / TASK_PATH_TEMPLATE.format(task_number)
    if not result.exists():
        raise FileNotFoundError()
    return result