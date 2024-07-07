from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from typing import Any, Dict, List, Tuple, Union


class ApiRequestHandler(BaseHTTPRequestHandler):

    next_response: bytes = b'{"Message": "No Response set"}'
    next_status = 400

    def do_GET(self) -> None:
        self.send_response(ApiRequestHandler.next_status)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(ApiRequestHandler.next_response)))
        self.end_headers()
        self.wfile.write(ApiRequestHandler.next_response)


def run_server(responses: List[Tuple[int, Union[Dict[str, Any], List[Any]]]]) -> None:
    server_address = ("localhost", 8000)
    httpd = HTTPServer(server_address, ApiRequestHandler)
    i = 0
    while i < len(responses):
        print(f"serve response {i+1} / {len(responses)}")
        ApiRequestHandler.next_response = json.dumps(responses[i][1]).encode("utf-8")
        ApiRequestHandler.next_status = int(responses[i][0])
        httpd.handle_request()
        i += 1


def mock_responses(
    responses: List[Tuple[int, Union[Dict[str, Any], List[Any]]]]
) -> None:
    def server() -> None:
        run_server(responses=responses)

    threading.Thread(None, server).start()
    time.sleep(0.1)
