from endstone.event import PlayerJoinEvent, PlayerQuitEvent, event_handler


class PlayerEvents:
    def __init__(self, plugin) -> None:
        self.plugin = plugin

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        player = event.player

        player_data = {
            "name": player.name,
            "uuid": str(player.unique_id),
        }

        self.plugin.webhook.dispatch(
            "player.join",
            {"player": player_data},
        )

        if self.plugin.player_data.is_first_join(player):
            self.plugin.webhook.dispatch(
                "player.first_join",
                {"player": player_data},
            )

    @event_handler
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
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