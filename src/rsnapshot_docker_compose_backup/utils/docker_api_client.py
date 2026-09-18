import json
import socket
import urllib.parse
from abc import ABC, abstractmethod
from dataclasses import dataclass
from http import HTTPStatus, client
from typing import Any


@dataclass
class HttpResponse:
    status_code: int
    status_text: str
    headers: dict[str, str]
    json_body: Any


class Api:

    _docker_socket: socket.socket | None = None

    def __init__(
        self, socket_connection: str = "unix:///run/docker.sock", version: str = "v1.46"
    ) -> None:
        self._current_connection: Api.Connection = self._open_socket(socket_connection)
        self.version = version

    def _open_socket(self, socket_connection: str) -> "Api.Connection":
        if socket_connection.startswith("unix://"):
            return Api.SocketConnection(socket_connection)
        if socket_connection.startswith("http://"):
            return Api.HttpConnection(socket_connection)
        msg = "Only Unix and http Sockets are supported"
        raise ValueError(msg)

    def get(
        self,
        endpoint: str,
        *,
        query_parameter: dict[str, str] | None = None,
        header: dict[str, str] | None = None,
    ) -> HttpResponse:
        path = f"/{self.version}{endpoint}"
        if query_parameter is not None:
            parameter: list[str] = []
            for name, value in query_parameter.items():
                parameter.append(f"{name}={urllib.parse.quote_plus(value)}")
            path = path + "?" + "&".join(parameter)
        return self._current_connection.get(path=path, header=header)

    class Connection(ABC):

        @abstractmethod
        def get(
            self,
            path: str,
            *,
            header: dict[str, str] | None = None,
        ) -> HttpResponse:
            pass

    class SocketConnection(Connection):

        def __init__(self, socket_connection: str) -> None:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(socket_connection[7:])  # Remove 'unix://'

        def get(
            self,
            path: str,
            *,
            header: dict[str, str] | None = None,
        ) -> HttpResponse:

            request = [
                f"GET {path} HTTP/1.1",
                "Host:docker.sock",
            ]
            if header is not None:
                for name, value in header.items():
                    request.append(f"{name}:{value}")
            request.append("\r\n")
            self.sock.send("\r\n".join(request).encode("utf-8"))
            return self._parse_response()

        def _parse_response(self) -> HttpResponse:
            # Read statusline and headers. I read byte by byte to be sure that not too much is read wich could lead to blocking
            message_start = b""
            while not message_start.endswith(b"\r\n\r\n"):
                message_start = message_start + self.sock.recv(1)
            lines: list[str] = message_start.decode("utf-8").splitlines()
            # Parse statusline
            status_line = lines[0]
            status_code = int(status_line.split(" ")[1])
            status_text = " ".join(status_line.split(" ")[2:])
            if status_code >= HTTPStatus.BAD_REQUEST:
                raise ValueError(status_text)
            # Read headers
            headers: dict[str, str] = {}
            for line in lines[1:]:
                split = line.split(":")
                if len(split) == 2:  # noqa: PLR2004
                    headers[split[0]] = split[1].strip()
            # read body
            if "Content-Length" in headers:
                body_length = int(headers["Content-Length"])
                body = self.sock.recv(body_length).decode("utf-8")
            elif (
                "Transfer-Encoding" in headers
                and headers["Transfer-Encoding"] == "chunked"
            ):
                body = ""
                while True:
                    chunk = b""
                    while not chunk.endswith(b"\r\n"):
                        chunk += self.sock.recv(1)
                    length = int(chunk.decode("utf-8"), 16)
                    if length == 0:
                        break
                    body = body + self.sock.recv(length).decode("utf-8")
                    self.sock.recv(2)  # Skip ending \r\n
            else:
                raise ValueError(headers)
            return HttpResponse(
                status_code=status_code,
                status_text=status_text,
                headers=headers,
                json_body=json.loads(body),
            )

    class HttpConnection(Connection):

        def __init__(self, socket_connection: str) -> None:
            self.httpConnection = client.HTTPConnection(
                socket_connection[7:]
            )  # Remove 'http://'

        def get(
            self,
            path: str,
            *,
            header: dict[str, str] | None = None,  # noqa: ARG002
        ) -> HttpResponse:

            self.httpConnection.request("GET", path)
            response = self.httpConnection.getresponse()
            headers: dict[str, str] = {}
            for curr_header in response.getheaders():
                headers[curr_header[0]] = curr_header[1]
            return HttpResponse(
                status_code=response.status,
                status_text="",
                headers=headers,
                json_body=json.loads(response.read()),
            )
