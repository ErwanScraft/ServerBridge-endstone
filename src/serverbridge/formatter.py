class MessageFormatter:
    @staticmethod
    def format(template: str, data: dict) -> str:
        player = data.get("player", {})

        replacements = {
            "{player}": str(player.get("name", "")),
            "{uuid}": str(player.get("uuid", "")),
        }

        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)

        return template