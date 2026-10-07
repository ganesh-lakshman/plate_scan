"""Mock eligibility service — stands in for the external partner network."""

import httpx

from app.config import settings


async def check_eligibility(vin: str) -> bool:
    """Call the mock partner-network eligibility endpoint.

    Falls back to a local stub if the HTTP call fails so the app
    stays functional even without the mock server running separately.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                settings.ELIGIBILITY_SERVICE_URL,
                json={"vin": vin},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("still_eligible_for_repo", False)
    except Exception:
        # Fallback local stub: eligible if VIN does not end with "00000"
        return not vin.endswith("00000")
