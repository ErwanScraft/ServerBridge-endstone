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

    def get_webhook_event(self, event: str) -> dict:
        events = self.get_webhook().get("events", {})
        event_config = events.get(event, {})

        if isinstance(event_config, bool):
            return {
                "enabled": event_config,
                "message": "",
            }

        if not isinstance(event_config, dict):
            return {}

        return event_config
        
    def get_inbound(self) -> dict:
        return self._data.get("inbound", {})
    
    def get_inbound_chat(self) -> dict:
        return self._data.get("inbound", {}).get("chat", {})