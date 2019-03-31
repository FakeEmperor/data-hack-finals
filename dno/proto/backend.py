import json
import socket
from typing import Union, Optional, Tuple
from loguru import logger

from dno.proto.base import BaseInteropBackend
from dno.proto.data import Map, Solution, Task, Results, TaskReader


class BackendInteractionException(Exception):
    """
    Raises during interaction with the backend in case:
    - error received from the backend
    - state is invalid
    """


class BackendInteraction(BaseInteropBackend):

    def __init__(self, backend_host: str, backed_port: int, auth: str):
        # Set backend url
        self.backend_host = backend_host
        self.backend_port = backed_port
        self._auth_data = auth

        # Set connection params
        self._current_iteration: int = 0
        self._finite_response: dict = None
        self._task_name = None
        self._stored_connection = None

        # Set result
        self._actual_score: Results = None

    @property
    def results(self) -> Optional[Results]:
        if not self.session_ended:
            return None
        if "scores" in self._finite_response:
            return Results.from_dict(self._finite_response)
        elif "error" in self._finite_response:
            raise BackendInteractionException(f"Backend interaction failed: {self._finite_response['error']}")
        else:
            raise BackendInteractionException(f"Unknown fucking huina: {self._finite_response}")

    @property
    def current_iteration(self) -> int:
        return self._current_iteration

    def make_session(self, use_cache=True) -> socket.SocketType:
        if self._stored_connection is None or not use_cache:
            tmp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.info(f"Connectig to {self.backend_host}:{self.backend_port}...")
            tmp_socket.connect((self.backend_host, self.backend_port))
            self._stored_connection = tmp_socket
            return tmp_socket
        else:
            # connection already exists, return it
            return self._stored_connection

    @property
    def session_ended(self) -> bool:
        return self._finite_response is not None

    def send_solution(self, solution: Solution) -> Union[Task, Results]:
        logger.info(f"Sending solution: {solution} for iteration: {self.current_iteration}")
        self._current_iteration += 1
        data = self.send_receive(solution.to_dict())
        self.assert_data(data)
        if "data" in data:
            return Task.from_dict(data["data"])
        else:
            self._finite_response = data
            return self.results

    def _reset(self) -> None:
        self._current_iteration = 0
        self._finite_response = None
        self._task_name = None
        self._stored_connection = None

    def build_start_task_message(self, task_index: int):
        return {
            "team": self._auth_data,
            "task": task_index
        }

    @staticmethod
    def prepare_data(data: dict) -> bytes:
        msg_bytes = json.dumps(data).encode()
        msg_size = len(msg_bytes).to_bytes(4, byteorder="little")
        return msg_size + msg_bytes

    @property
    def session(self) -> Optional[socket.SocketType]:
        return self._stored_connection

    def send_receive(self, data: dict) -> dict:
        """
        Sends and receives data from the backend
        :param data: Data to send
        :return: Received data
        """
        logger.debug(f"Sending data: {data}")
        self.session.send(self.prepare_data(data))
        received = TaskReader.read_next_response(socket.SocketIO(self.session, mode='rb'))
        logger.debug(f"Received data: {received}")
        return received

    @staticmethod
    def assert_data(data: dict) -> dict:
        if "error" in data:
            raise BackendInteractionException(f"Assertion error on response from server: {data}")
        return data

    def start_task(self, task_index: int) -> Map:
        # 1. Open session if it is None
        self._reset()
        self._task_name = task_index
        self.make_session(use_cache=False)
        # 2. Form msg in required format (bytes)
        # 3. Send msg to backend
        map_data = self.send_receive(self.build_start_task_message(task_index))
        self.assert_data(map_data)
        return Map.from_dict(map_data)

    @property
    def current_task(self) -> str:
        return self._task_name


def main():
    backend = BackendInteraction(backend_host='besthack19.sytes.net', backed_port=4242, auth="exp3ct0pat5onum")
    backend.start_task(2)
    task_steps = []
    while not backend.session_ended:
        data = backend.send_solution(Solution(ready=False))
        if not backend.session_ended:
            task_steps.append(data)
    logger.success(f"Final score: {backend.results}")


if __name__ == "__main__":
    main()

