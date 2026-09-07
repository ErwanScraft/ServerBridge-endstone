import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread


class InboundRequestHandler(BaseHTTPRequestHandler):
    server_version = "ServerBridge/0.2"

    def do_POST(self) -> None:
        bridge = self.server.bridge

        if self.path != "/api/v1":
            self._send_json(
                404,
                {
                    "success": False,
                    "error": "Endpoint not found",
                },
            )
            return

        if not self._authenticate(bridge):
            self._send_json(
                401,
                {
                    "success": False,
                    "error": "Unauthorized",
                },
            )
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            content_length = 0

        if content_length <= 0:
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Request body is required",
                },
            )
            return

        try:
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Invalid JSON",
                },
            )
            return

        if not isinstance(data, dict):
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Request body must be an object",
                },
            )
            return

        action = str(data.get("action", "")).strip().lower()

        if action == "chat":
            result = bridge.handle_chat(data)
        elif action == "command":
            result = bridge.handle_command(data)
        else:
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Unknown action",
                },
            )
            return

        status = 200 if result.get("success", False) else 400
        self._send_json(status, result)

    def _authenticate(self, bridge) -> bool:
        authorization = self.headers.get("Authorization", "").strip()

        if not authorization.startswith("Bearer "):
            return False

        token = authorization[7:].strip()

        if not token:
            return False

        try:
            return token == bridge.plugin.secret.get()
        except RuntimeError:
            return False

    def _send_json(self, status: int, data: dict) -> None:
        payload = json.dumps(
            data,
            ensure_ascii=False,
        ).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args) -> None:
        return


class InboundServer:
    def __init__(self, plugin, config) -> None:
        self.plugin = plugin
        self.config = config
        self.server = None
        self.thread = None

    def start(self) -> None:
        inbound = self.config.get_inbound()

        if not inbound.get("enabled", False):
            return

        host = str(inbound.get("host", "127.0.0.1"))
        port = self._get_port(inbound.get("port", 8765))

        self.server = ThreadingHTTPServer(
            (host, port),
            InboundRequestHandler,
        )

        self.server.bridge = self

        self.thread = Thread(
            target=self.server.serve_forever,
            daemon=True,
            name="ServerBridge-Inbound",
        )
        self.thread.start()

        self.plugin.logger.info(
            f"ServerBridge inbound API listening on {host}:{port}"
        )

    def stop(self) -> None:
        if self.server is None:
            return

        self.server.shutdown()
        self.server.server_close()

        if self.thread is not None:
            self.thread.join(timeout=2)

        self.server = None
        self.thread = None

    def handle_chat(self, data: dict) -> dict:
        inbound = self.config.get_inbound()
        actions = inbound.get("actions", {})

        if not actions.get("chat", True):
            return {
                "success": False,
                "action": "chat",
                "error": "Chat action is disabled",
            }

        message = str(data.get("message", "")).strip()

        if not message:
            return {
                "success": False,
                "action": "chat",
                "error": "Message is required",
            }

        self.plugin.server.scheduler.run_task(
            lambda: self.plugin.server.broadcast_message(
                message
            )
        )

        return {
            "success": True,
            "action": "chat",
        }

    def handle_command(self, data: dict) -> dict:
        inbound = self.config.get_inbound()
        actions = inbound.get("actions", {})

        if not actions.get("command", True):
            return {
                "success": False,
                "action": "command",
                "error": "Command action is disabled",
            }

        command = str(data.get("command", "")).strip()

        if command.startswith("/"):
            command = command[1:].strip()

        if not command:
            return {
                "success": False,
                "action": "command",
                "error": "Command is required",
            }

        if not self._is_command_allowed(command):
            return {
                "success": False,
                "action": "command",
                "error": "Command is not allowed",
            }

        self.plugin.server.scheduler.run_task(
            lambda: self.plugin.server.dispatch_command(
                command
            )
        )

        return {
            "success": True,
            "action": "command",
        }

    def _is_command_allowed(self, command: str) -> bool:
        inbound = self.config.get_inbound()
        command_config = inbound.get("command", {})

        allowed = command_config.get("allowed", [])

        if not isinstance(allowed, list):
            return False

        command_name = command.split(maxsplit=1)[0].lower()

        return command_name in {
            str(value).strip().lower()
            for value in allowed
            if str(value).strip()
        }

    @staticmethod
    def _get_port(value) -> int:
        try:
            port = int(value)
        except (TypeError, ValueError):
            return 8765

        if not 1 <= port <= 65535:
            return 8765

        return port