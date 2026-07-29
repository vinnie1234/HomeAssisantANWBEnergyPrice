from datetime import timedelta, datetime, timezone
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_URL, API_INTERVAL

_LOGGER = logging.getLogger(__name__)

HEADERS = {
    "accept": "application/json",
    "accept-language": "nl,en;q=0.9",
    "origin": "https://www.anwb.nl",
    "referer": "https://www.anwb.nl/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0"
    ),
}


class ANWBEnergyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> dict:
        now = datetime.now(timezone.utc)
        # Fetch yesterday 23:00 UTC → today 23:00 UTC (covers full local day NL)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=1)
        end = start + timedelta(hours=25)

        params = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "interval": API_INTERVAL,
        }

        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(API_URL, params=params) as response:
                    response.raise_for_status()
                    raw = await response.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Fout bij ophalen ANWB energieprijzen: {err}") from err

        return self._parse(raw, now)

    def _parse(self, raw: dict, now: datetime) -> dict:
        entries = raw.get("data", [])

        hourly = {}
        for entry in entries:
            dt = datetime.fromisoformat(entry["date"])
            values = entry.get("values", {})
            hourly[dt] = {
                "marktprijs": values.get("marktprijs"),
                "allinPrijs": values.get("allInPrijs"),
            }

        # Current hour price: find the entry whose hour matches now (UTC)
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        current = hourly.get(current_hour) or self._closest(hourly, current_hour)

        marktprijzen = [v["marktprijs"] for v in hourly.values() if v["marktprijs"] is not None]
        allinprijzen = [v["allinPrijs"] for v in hourly.values() if v["allinPrijs"] is not None]

        # Build sorted list for attributes (ISO string keys for serialisation)
        hourly_attr = {
            dt.isoformat(): vals for dt, vals in sorted(hourly.items())
        }

        marktprijs_goedkoopste = min(hourly.items(), key=lambda x: x[1]["marktprijs"] if x[1]["marktprijs"] is not None else float("inf"), default=None)
        allinprijs_goedkoopste = min(hourly.items(), key=lambda x: x[1]["allinPrijs"] if x[1]["allinPrijs"] is not None else float("inf"), default=None)

        return {
            "current": current,
            "hourly": hourly_attr,
            "marktprijs_min": min(marktprijzen) if marktprijzen else None,
            "marktprijs_max": max(marktprijzen) if marktprijzen else None,
            "marktprijs_avg": round(sum(marktprijzen) / len(marktprijzen), 5) if marktprijzen else None,
            "allinprijs_min": min(allinprijzen) if allinprijzen else None,
            "allinprijs_max": max(allinprijzen) if allinprijzen else None,
            "allinprijs_avg": round(sum(allinprijzen) / len(allinprijzen), 5) if allinprijzen else None,
            "marktprijs_goedkoopste_uur": {
                "prijs": marktprijs_goedkoopste[1]["marktprijs"],
                "tijdstip": marktprijs_goedkoopste[0].isoformat(),
            } if marktprijs_goedkoopste else None,
            "allinprijs_goedkoopste_uur": {
                "prijs": allinprijs_goedkoopste[1]["allinPrijs"],
                "tijdstip": allinprijs_goedkoopste[0].isoformat(),
            } if allinprijs_goedkoopste else None,
        }

    @staticmethod
    def _closest(hourly: dict, target: datetime):
        if not hourly:
            return None
        closest_dt = min(hourly.keys(), key=lambda dt: abs((dt - target).total_seconds()))
        return hourly[closest_dt]
