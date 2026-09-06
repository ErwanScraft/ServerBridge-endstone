from secrets import token_urlsafe


class SecretManager:
    def __init__(self, plugin) -> None:
        self.path = plugin.data_folder / "secret.key"
        self.logger = plugin.logger
        self._secret = ""

    def load(self) -> None:
        if self.path.exists():
            secret = self.path.read_text(encoding="utf-8").strip()

            if secret:
                self._secret = secret
                return

        self._generate()

    def get(self) -> str:
        if not self._secret:
            raise RuntimeError("ServerBridge secret is not loaded.")

        return self._secret

    def _generate(self) -> None:
        self._secret = f"sb_{token_urlsafe(48)}"
        self.path.write_text(
            self._secret + "\n",
            encoding="utf-8",
        )

        self.logger.info("ServerBridge secret key generated.")