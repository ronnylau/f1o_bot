import json
from time import sleep
from typing import Any, Dict, Optional

import httpx
from httpx import HTTPError, Response, TimeoutException
import logging

logger = logging.getLogger(__name__)

class Utility:
    """Utilitarian functions designed for Renovate."""

    def GET(
        self: Any, url: str, raw: bool = False, isRetry: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Perform an HTTP GET request and return its response."""

        logger = logging.getLogger(__name__)
        logger.debug(f"GET {url}")

        status: int = 0

        try:
            res: Response = httpx.get(url, timeout=30.0, follow_redirects=True)
            status = res.status_code
            data: Dict[str, Any] = res.text

            res.raise_for_status()
        except TimeoutException as e:
            if not isRetry:
                logger.debug(f"GET {url} failed, {e}... Retry in 10s")

                sleep(10)

                return Utility.GET(self, url, raw, True)

            # TimeoutException is common, no need to log as error
            logger.debug(f"GET {url} failed, {e}")

            return
        except HTTPError as e:
            if not isRetry:
                logger.debug(f"(HTTP {status}) GET {url} failed, {e}... Retry in 10s")

                sleep(10)

                return Utility.GET(self, url, raw, True)

            logger.error(f"(HTTP {status}) GET {url} failed, {e}")

            return
        except Exception as e:
            if not isRetry:
                logger.debug(f"GET {url} failed, {e}... Retry in 10s")

                sleep(10)

                return Utility.GET(self, url, raw, True)

            logger.error(f"GET {url} failed, {e}")

            return

        if raw is True:
            return data

        return res.json()

    def POST(self: Any, url: str, payload: Dict[str, Any]) -> bool:
        logger = logging.getLogger(__name__)
        """Perform an HTTP POST request and return its status."""

        try:
            res: Response = httpx.post(
                url,
                data=json.dumps(payload),
                headers={"content-type": "application/json"},
            )
            data: str = res.text

            res.raise_for_status()
        except Exception as e:
            logger.warning(f"POST {url} failed, {e}")

            return False
        return True
