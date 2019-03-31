from dno.model.model import Model
from dno.proto.mock import TaskReader
from dno.proto.data import Task, Solution
from dno.proto import utils
from dno.proto.backend import BackendInteraction
from loguru import logger

if __name__ == "__main__":
    backend = BackendInteraction(backend_host='besthack19.sytes.net', backed_port=4242, auth="exp3ct0pat5onum")
    land_map = backend.start_task(1)
    task_steps = []
    model = Model(land_map)
    task = backend.send_solution(Solution(ready=False))
    while not backend.session_ended:
        task = backend.send_solution(model.handle_task(task))

    logger.success(f"Final score: {backend.results}")

