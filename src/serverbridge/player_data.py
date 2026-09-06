import yaml


class PlayerData:
    def __init__(self, plugin) -> None:
        self.path = plugin.data_folder / "players.yml"
        self.players: set[str] = set()

    def load(self) -> None:
        if not self.path.exists():
            self.players = set()
            return

        with self.path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or []

        if not isinstance(data, list):
            raise ValueError("players.yml must contain a YAML list.")

        self.players = {str(player_id) for player_id in data}

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            yaml.safe_dump(
                sorted(self.players),
                file,
                allow_unicode=True,
                default_flow_style=False,
            )

    def is_first_join(self, player) -> bool:
        player_id = str(player.unique_id)

        if player_id in self.players:
            return False

        self.players.add(player_id)
        self.save()

        return True