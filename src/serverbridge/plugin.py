from endstone.plugin import Plugin

from .config import ServerBridgeConfig


class ServerBridgePlugin(Plugin):
    api_version = "0.11"
    authors = ["ErwanScraft"]

    def on_enable(self) -> None:
        self.save_resources("config.yml")

        self._config = ServerBridgeConfig(self)
        self._config.load()

        self.logger.info("ServerBridge enabled!")