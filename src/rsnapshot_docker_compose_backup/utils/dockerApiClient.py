from dataclasses import dataclass
import json
import socket
from typing import Any, Optional
import urllib.parse


@dataclass
class HttpResponse:
    protocol_version: str
    status_code: int
    status_text: str
    headers: dict[str, str]
    json_body: Any


class Api:

    _docker_socket: Optional[socket.socket] = None

    def __init__(
        self, socket_connection: str = "unix:///run/docker.sock", version: str = "v1.46"
    ) -> None:
        self.docker_socket = self._open_socket(socket_connection)
        self.version = version

    def _open_socket(self, socket_connection: str) -> socket.socket:
        if socket_connection.startswith("unix://"):
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(socket_connection.removeprefix("unix://"))
            return sock
        if socket_connection.startswith("http://"):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            parts = socket_connection.removeprefix("http://").split(":")
            host = parts[0]
            port = 80
            if len(parts) == 2:
                port = int(parts[1])
            print(f"connect to {host}, {port}")
            sock.connect((host, port))
            return sock
        raise ValueError("Only Unix and http Sockets are supported")

    def get(
        self,
        endpoint: str,
        *,
        query_parameter: Optional[dict[str, str]] = None,
        header: Optional[dict[str, str]] = None,
    ) -> HttpResponse:
        path = f"/{self.version}{endpoint}"
        if query_parameter is not None:
            parameter: list[str] = []
            for name, value in query_parameter.items():
                parameter.append(f"{name}={urllib.parse.quote_plus(value)}")
            path = path + "?" + "&".join(parameter)
        request = [
            f"GET {path} HTTP/1.1",
            "Host:docker.sock",
        ]
        if header is not None:
            for name, value in header.items():
                request.append(f"{name}:{value}")
        request.append("\r\n")
        self.docker_socket.send("\r\n".join(request).encode("utf-8"))
        return self._parse_response(self.docker_socket)

    @staticmethod
    def _parse_response(sock: socket.socket) -> HttpResponse:
        #Read statusline and headers. I read byte by byte to be sure that not too much is read wich could lead to blocking
        message_start = b""
        while not message_start.endswith(b"\r\n\r\n"):
            message_start = message_start + sock.recv(1)
        lines: list[str] = message_start.decode("utf-8").splitlines()
        #Parse statusline
        status_line = lines[0]
        protocol_version = status_line.split(" ")[0]
        status_code = int(status_line.split(" ")[1])
        status_text = " ".join(status_line.split(" ")[2:])
        if status_code >= 400:
            raise ValueError(status_text)
        #Read headers
        headers: dict[str, str] = {}
        for line in lines[1:]:
            split = line.split(":")
            if len(split) == 2:
                headers[split[0]] = split[1].strip()
        #read body
        if "Content-Length" in headers:
            body_length = int(headers["Content-Length"])
            body = sock.recv(body_length).decode("utf-8")
        elif (
            "Transfer-Encoding" in headers and headers["Transfer-Encoding"] == "chunked"
        ):
            body = ""
            while True:
                chunk = b""
                while not chunk.endswith(b"\r\n"):
                    chunk += sock.recv(1)
                length = int(chunk.decode("utf-8"), 16)
                if length == 0:
                    break
                body = body + sock.recv(length).decode("utf-8")
                sock.recv(2)  # Skip ending \r\n
        else:
            raise ValueError(headers)
        return HttpResponse(
            protocol_version=protocol_version,
            status_code=status_code,
            status_text=status_text,
            headers=headers,
            json_body=json.loads(body),
        )
