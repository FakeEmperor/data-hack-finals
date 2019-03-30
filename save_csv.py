from typing import List, Union
from pathlib import Path
from dno.proto.mock import MockInterop, BaseInteropBackend
from dno.proto.utils import get_project_root
from loguru import logger


def get_csvs(tasks: List[str]=None, output_dir: Union[Path, str]="data/csvs"):
    """
    Get csv data
    """
    root: Path = get_project_root() / "data" / "besthack19"
    output_dir = get_project_root() / 'data'/ 'csvs'
    if tasks is None:
        tasks = root.glob('*')
        tasks = [path.name for path in tasks if path.is_file()]
    if not output_dir.exists():
        logger.debug("Creating directory structure for the output directory...")
        output_dir.mkdir(parents=True, exist_ok=True)

    for task in tasks:
        logger.info(f"Saving info for {task}...")
        backend = MockInterop(root, task)
        _, df, _ = backend.get_csv()
        df.to_csv(str(output_dir / f'{task}.csv'))


if __name__ == "__main__":
    get_csvs()
