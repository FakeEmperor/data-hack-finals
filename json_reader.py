"""
Govno dlya chteniya govna
"""

import json
from le_convert import to_int
from pathlib import Path

class TaskReader:
    def __init__(self, task_path):
        if not Path(task_path).exists():
            raise FileNotFoundError(f"Error: can't find file \"{task_path}\"")
        self.io_wrapper = open(task_path)

    def read_next(self):
        try:
            size = to_int(self.io_wrapper.read(4))
        except IOError:
            return ""
        return self.io_wrapper.read(size)

    def read_map(self):
        self.io_wrapper.seek(0)
        size = to_int(self.io_wrapper.read(4))
        return self.io_wrapper.read(size)

    def read_next_j(self):
        return json.loads(self.read_next())

    def read_map_j(self):
        return json.loads(self.read_map())


#test = TaskReader((Path(__name__).parent / "bh" / "task1").absolute())
#map_str = test.read_map()
#map_str_json = test.read_map_j()
#print("")