from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from typing import Any

from rsnapshot_docker_compose_backup.docker import docker


class ApiRequestHandler(BaseHTTPRequestHandler):

    next_response: bytes = b'{"Message": "No Response set"}'
    next_status = 400

    def do_GET(self):
        self.send_response(ApiRequestHandler.next_status)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(ApiRequestHandler.next_response)))
        self.end_headers()
        self.wfile.write(ApiRequestHandler.next_response)


def run_server(responses: list[tuple[int, dict[str, Any] | list[Any]]]):
    server_address = ("localhost", 8000)
    httpd = HTTPServer(server_address, ApiRequestHandler)
    i = 0
    while i < len(responses):
        print(f"serve response {i+1} / {len(responses)}")
        ApiRequestHandler.next_response = json.dumps(responses[i][1]).encode("utf-8")
        ApiRequestHandler.next_status = int(responses[i][0])
        httpd.handle_request()
        i += 1


def mock_responses(responses: list[tuple[int, dict[str, Any] | list[Any]]]):
    def server():
        run_server(responses=responses)

    threading.Thread(None, server).start()
    time.sleep(0.1)


def test_ps() -> None:
    mock_responses(
        [
            (
                200,
                [
                    {
                        "Id": "8dfafdbc3a40",
                        "Names": ["/boring_feynman"],
                        "Image": "ubuntu:latest",
                        "ImageID": "d74508fb6632491cea586a1fd7d748dfc5274cd6fdfedee309ecdcbc2bf5cb82",
                        "Command": "echo 1",
                        "Created": 1367854155,
                        "State": "Exited",
                        "Status": "Exit 0",
                        "Ports": [
                            {"PrivatePort": 2222, "PublicPort": 3333, "Type": "tcp"}
                        ],
                        "Labels": {
                            "com.example.vendor": "Acme",
                            "com.example.license": "GPL",
                            "com.example.version": "1.0",
                        },
                        "SizeRw": 12288,
                        "SizeRootFs": 0,
                        "HostConfig": {
                            "NetworkMode": "default",
                            "Annotations": {"io.kubernetes.docker.type": "container"},
                        },
                        "NetworkSettings": {
                            "Networks": {
                                "bridge": {
                                    "NetworkID": "7ea29fc1412292a2d7bba362f9253545fecdfa8ce9a6e37dd10ba8bee7129812",
                                    "EndpointID": "2cdc4edb1ded3631c81f57966563e5c8525b81121bb3706a9a9a3ae102711f3f",
                                    "Gateway": "172.17.0.1",
                                    "IPAddress": "172.17.0.2",
                                    "IPPrefixLen": 16,
                                    "IPv6Gateway": "",
                                    "GlobalIPv6Address": "",
                                    "GlobalIPv6PrefixLen": 0,
                                    "MacAddress": "02:42:ac:11:00:02",
                                }
                            }
                        },
                        "Mounts": [
                            {
                                "Name": "fac362...80535",
                                "Source": "/data",
                                "Destination": "/data",
                                "Driver": "local",
                                "Mode": "ro,Z",
                                "RW": False,
                                "Propagation": "",
                            }
                        ],
                    },
                    {
                        "Id": "9cd87474be90",
                        "Names": ["/coolName"],
                        "Image": "ubuntu:latest",
                        "ImageID": "d74508fb6632491cea586a1fd7d748dfc5274cd6fdfedee309ecdcbc2bf5cb82",
                        "Command": "echo 222222",
                        "Created": 1367854155,
                        "State": "Exited",
                        "Status": "Exit 0",
                        "Ports": [],
                        "Labels": {},
                        "SizeRw": 12288,
                        "SizeRootFs": 0,
                        "HostConfig": {
                            "NetworkMode": "default",
                            "Annotations": {
                                "io.kubernetes.docker.type": "container",
                                "io.kubernetes.sandbox.id": "3befe639bed0fd6afdd65fd1fa84506756f59360ec4adc270b0fdac9be22b4d3",
                            },
                        },
                        "NetworkSettings": {
                            "Networks": {
                                "bridge": {
                                    "NetworkID": "7ea29fc1412292a2d7bba362f9253545fecdfa8ce9a6e37dd10ba8bee7129812",
                                    "EndpointID": "88eaed7b37b38c2a3f0c4bc796494fdf51b270c2d22656412a2ca5d559a64d7a",
                                    "Gateway": "172.17.0.1",
                                    "IPAddress": "172.17.0.8",
                                    "IPPrefixLen": 16,
                                    "IPv6Gateway": "",
                                    "GlobalIPv6Address": "",
                                    "GlobalIPv6PrefixLen": 0,
                                    "MacAddress": "02:42:ac:11:00:08",
                                }
                            }
                        },
                        "Mounts": [],
                    },
                ],
            )
        ]
    )
    response = docker.ps(socket_connection="http://localhost:8000")
    assert response[0].id == "8dfafdbc3a40"
    assert response[1].image == "ubuntu:latest"


def test_version() -> None:
    mock_responses([(200, {"Version": "27.0.3"})])
    assert docker.get_version(socket_connection="http://localhost:8000") == "27.0.3"
