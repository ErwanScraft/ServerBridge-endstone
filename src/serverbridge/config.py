import yaml


class ServerBridgeConfig:
    def __init__(self, plugin) -> None:
        self.plugin = plugin
        self._data = {}

    def load(self) -> None:
        path = self.plugin.data_folder / "config.yml"

        with open(path, "r", encoding="utf-8") as file:
            self._data = yaml.safe_load(file) or {}

    def get_webhook(self) -> dict:
        return self._data.get("webhook", {})