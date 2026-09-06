from endstone.plugin import Plugin

from .config import ServerBridgeConfig
from .events import PlayerEvents
from .player_data import PlayerData
from .webhook import WebhookDispatcher
from .secret import SecretManager

class ServerBridgePlugin(Plugin):
    api_version = "0.11"
    authors = ["ErwanScraft"]

    def on_enable(self) -> None:
        self.save_resources("config.yml")
    
        self._config = ServerBridgeConfig(self)
        self._config.load()
    
        self._player_data = PlayerData(self)
        self._player_data.load()
        self.player_data = self._player_data
        
        self._secret = SecretManager(self)
        self._secret.load()
        self.secret = self._secret
    
        self._webhook = WebhookDispatcher(
            self,
            self._config,
            self._secret,
        )
        self.webhook = self._webhook
    
        self.register_events(PlayerEvents(self))
    
        self.logger.info("ServerBridge enabled!")