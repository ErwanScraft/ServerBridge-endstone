class MessageFormatter:
    @staticmethod
    def format(template: str, data: dict) -> str:
        player = data.get("player", {})

        replacements = {
            "{player}": str(player.get("name", "")),
            "{uuid}": str(player.get("uuid", "")),
            "{death_cause}": str(data.get("death", {}).get("cause", "")),
            "{message}": str(data.get("chat", {}).get("message", "")),
        }

        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)

        return template