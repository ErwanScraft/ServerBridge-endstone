import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class WebhookClient:
    USER_AGENT = "ServerBridge/0.1"

    def __init__(self, logger) -> None:
        self.logger = logger

    def send(
        self,
        url: str,
        payload: dict,
        secret: str = "",
        timeout: float = 5.0,
    ) -> bool:
        data = json.dumps(payload).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }

        if secret:
            headers["Authorization"] = f"Bearer {secret}"

        request = Request(
            url,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=timeout) as response:
                status = response.status

                if 200 <= status < 300:
                    return True

                self.logger.warning(
                    f"Webhook returned HTTP {status}: {url}"
                )

        except HTTPError as error:
            self.logger.warning(
                f"Webhook HTTP error {error.code}: {url}"
            )

        except URLError as error:
            self.logger.warning(
                f"Webhook connection failed: {error.reason}"
            )

        except Exception as error:
            self.logger.warning(
                f"Webhook request failed: {error}"
            )

        return False