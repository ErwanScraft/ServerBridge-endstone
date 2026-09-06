from endstone.event import PlayerJoinEvent, PlayerQuitEvent
from endstone.plugin import EventPriority, event_handler


class PlayerEvents:
    def __init__(self, plugin) -> None:
        self.plugin = plugin

    @event_handler(PlayerJoinEvent, EventPriority.NORMAL)
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        player = event.player

        self.plugin.webhook.dispatch(
            "player.join",
            {
                "player": {
                    "name": player.name,
                    "uuid": str(player.unique_id),
                }
            },
        )

    @event_handler(PlayerQuitEvent, EventPriority.NORMAL)
    def on_player_leave(self, event: PlayerQuitEvent) -> None:
        player = event.player

        self.plugin.webhook.dispatch(
            "player.leave",
            {
                "player": {
                    "name": player.name,
                    "uuid": str(player.unique_id),
                }
            },
        )