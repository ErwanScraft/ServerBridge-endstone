from endstone.event import (
    PlayerChatEvent,
    PlayerDeathEvent,
    PlayerJoinEvent,
    PlayerQuitEvent,
    event_handler,
)

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
    
    @event_handler
    def on_player_death(self, event: PlayerDeathEvent) -> None:
        player = event.player
        damage_source = event.damage_source

        self.plugin.webhook.dispatch(
            "player.die",
            {
                "player": {
                    "name": player.name,
                    "uuid": str(player.unique_id),
                },
                "death": {
                    "cause": damage_source.type,
                },
            },
        )
    
    @event_handler
    def on_player_chat(self, event: PlayerChatEvent) -> None:
        if event.message.startswith("/"):
            return
    
        player = event.player
    
        self.plugin.webhook.dispatch(
            "player.chat",
            {
                "player": {
                    "name": player.name,
                    "uuid": str(player.unique_id),
                },
                "chat": {
                    "message": event.message,
                },
            },
        )