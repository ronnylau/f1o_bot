import json
from datetime import datetime
from sys import exit, stderr
from typing import Any, Dict, Optional
import os

import logging
from updatechecker.utils import Utility

logger = logging.getLogger(__name__)

class Renovate:
    """
    Renovate is a Battle.net, PlayStation, and Steam title watcher that
    reports updates via Discord.

    https://github.com/EthanC/Renovate
    """

    def Initialize(self: Any) -> None:
        """Initialize Renovate and begin primary functionality."""
        logger.info("Renovate")
        logger.info("https://github.com/EthanC/Renovate")

        self.config: Dict[str, Any] = Renovate.LoadConfig(self)

        self.history: Dict[str, Any] = Renovate.LoadHistory(self)
        self.changed: bool = False

        # PlayStation 4
        for title in self.config["titles"]["orbis"]:
            Renovate.ProcessOrbisTitle(self, title)

        if self.changed:
            Renovate.SaveHistory(self)

        logger.warning("Finished processing titles")

    def LoadConfig(self: Any) -> Dict[str, Any]:
        """Load the configuration values specified in config.json"""
        dir = os.path.dirname(__file__)
        file = "config.json"
        path = os.path.join(dir, file)
        try:
            with open(path, "r") as file:
                config: Dict[str, Any] = json.loads(file.read())
        except Exception as e:
            logger.warning(f"Failed to load configuration, {e}")

            exit(1)

        logger.warning("Loaded configuration")

        return config

    def LoadHistory(self: Any) -> Dict[str, Any]:
        """Load the last seen title versions specified in history.json"""

        try:
            with open("history.json", "r") as file:
                history: Dict[str, Any] = json.loads(file.read())
        except FileNotFoundError:
            history: Dict[str, Any] = {
                "battle": {},
                "prospero": {},
                "orbis": {},
                "steam": {},
            }

            with open("history.json", "w+") as file:
                file.write(json.dumps(history, indent=4))

            logger.warning("Title history not found, created empty file")
        except Exception as e:
            logger.warning(f"Failed to load title history, {e}")

            exit(1)

        if history.get("battle") is None:
            history["battle"] = {}

        if history.get("prospero") is None:
            history["prospero"] = {}

        if history.get("orbis") is None:
            history["orbis"] = {}

        if history.get("steam") is None:
            history["steam"] = {}

        logger.warning("Loaded title history")

        return history

    def ProcessOrbisTitle(self: Any, titleId: str) -> None:
        """
        Get the current version of the specified PlayStation 4 title and
        determine whether or not it has updated.
        """

        past: Optional[str] = self.history["orbis"].get(titleId)

        data: Optional[Dict[str, Any]] = Utility.GET(
            self, f"https://orbispatches.com/api/lookup?titleid={titleId}"
        )

        if (data is None) or (not data.get("success")):
            return

        name: str = data["metadata"]["name"]
        current: str = data["metadata"]["currentVersion"]

        if past is None:
            self.history["orbis"][titleId] = current
            self.changed = True

            logger.warning(
                f"Orbis title {name} previously untracked, saved version {current} to title history"
            )

            return
        elif past == current:
            logger.warning(f"Orbis title {name} not updated ({current})")

            return

        logger.warning(f"Orbis title {name} updated, {past} -> {current}")

        success: bool = Renovate.Notify(

            self,
            {
                "name": name,
                "url": f"https://orbispatches.com/{titleId}",
                "platformColor": "00439C",
                "region": data["metadata"]["region"],
                "titleId": titleId,
                "platformLogo": "https://i.imgur.com/ccNqLcb.png",
                "thumbnail": data["metadata"]["icon"],
                "image": None,
                "pastVersion": f"`{past}`",
                "currentVersion": f"`{current}`",
            },
        )

        # Ensure no changes go without notification
        if success:
            self.history["orbis"][titleId] = current
            self.changed = True

    def Notify(self: Any, data: Dict[str, str]) -> bool:
        """Report title version change to the configured Discord webhook."""

        settings: Dict[str, Any] = self.config["discord"]

        region: Optional[str] = data.get("region")
        titleId: str = data["titleId"]

        payload: Dict[str, Any] = {
            "username": settings["username"],
            "embeds": [
                {
                    "title": data["name"],
                    "description": "Es gibt ein Update zu F1 22!",
                    "url": data.get("url"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "color": int(data["platformColor"], base=16),
                    "footer": {
                        "text": titleId if region is None else f"({region}) {titleId}",
                        "icon_url": data["platformLogo"],
                    },
                    "thumbnail": {"url": data.get("thumbnail")},
                    "image": {"url": data.get("image")},
                    "author": {
                        "name": "F1O PS Bot"
                    },
                    "fields": [
                        {
                            "name": "Letzte Version",
                            "value": data["pastVersion"],
                            "inline": True,
                        },
                        {
                            "name": "Neue Version",
                            "value": data["currentVersion"],
                            "inline": True,
                        },
                    ],
                }
            ],
        }

        return Utility.POST(self, settings["webhookUrl"], payload)

    def SaveHistory(self: Any) -> None:
        """Save the latest title versions to history.json"""

        if self.config.get("debug"):
            logger.warning("Debug is active, not saving title history")

            return

        try:
            with open("history.json", "w+") as file:
                file.write(json.dumps(self.history, indent=4))
        except Exception as e:
            logger.warning(f"Failed to save title history, {e}")

            exit(1)

        logger.warning("Saved title history")


if __name__ == "__main__":
    try:
        Renovate.Initialize(Renovate)
    except KeyboardInterrupt:
        exit()
