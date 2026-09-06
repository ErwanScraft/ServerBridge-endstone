from datetime import datetime, timezone
from threading import Thread

from .client import WebhookClient


class WebhookDispatcher:
    def __init__(self, plugin, config, secret) -> None:
        self.plugin = plugin
        self.config = config
        self.secret = secret
        self.client = WebhookClient(plugin.logger)

    def dispatch(self, event: str, data: dict) -> None:
        webhook = self.config.get_webhook()

        if not webhook.get("enabled", False):
            return

        events = webhook.get("events", {})

        if not events.get(event, False):
            return

        url = str(webhook.get("url", "")).strip()

        if not url:
            return

        payload = {
            "version": 1,
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data,
        }

        secret = str(webhook.get("secret", "")).strip()

        try:
            timeout = float(webhook.get("timeout", 5))
        except (TypeError, ValueError):
            timeout = 5.0

        Thread(
            target=self._send,
            args=(url, payload, timeout),
            daemon=True,
            name="ServerBridge-Webhook",
        ).start()

    def _send(
        self,
        url: str,
        payload: dict,
        timeout: float,
    ) -> None:
        self.client.send(
            url=url,
            payload=payload,
            secret=self.secret.get(),
            timeout=timeout,
        )