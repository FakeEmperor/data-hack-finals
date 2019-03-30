from pathlib import Path
from typing import Optional

def get_project_root()-> Optional[Path]:
    current_dir = Path.cwd()
    while True:
        if (current_dir / '.git').exists():
            return current_dir
        if current_dir.parent != current_dir:
            current_dir = current_dir.parent
        else:
            return None

