"""
Google Calendar helpers

The calendar IDs to query are read from config.calendar_ids so they
stay out of source code.  Add this to config.py if it isn't there:
"""

import datetime
from typing import Any

from config import calendar_ids


def fetch_calendar_events(service, max_results: int = 1) -> list[dict[str, Any]]:
    """
    Return the next *max_results* events across all configured calendars,
    sorted by start time.  Calendars that fail (e.g. permission error) are
    skipped with a warning rather than crashing the whole fetch.

    Parameters
    ----------
    service
        An authorised Google Calendar API service object.
    max_results : int
        Maximum number of events to return in total (default 1).

    Returns
    -------
    list[dict]
        Each dict is a raw Google Calendar event resource.
    """
    now = datetime.datetime.utcnow().isoformat() + "Z"
    all_events: list[dict[str, Any]] = []

    for calendar_id in calendar_ids:
        try:
            result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            all_events.extend(result.get("items", []))
        except Exception as exc:
            print(f"[calendar] Could not fetch from {calendar_id}: {exc}")

    # Sort merged results and trim to the requested limit
    all_events.sort(
        key=lambda e: e.get("start", {}).get("dateTime",
                     e.get("start", {}).get("date", ""))
    )
    return all_events[:max_results]


def list_calendars(service) -> list[dict[str, Any]]:
    """
    Return all calendars visible to the authenticated service account.

    Parameters
    ----------
    service
        An authorised Google Calendar API service object.

    Returns
    -------
    list[dict]
        Each dict is a raw Google Calendar calendarList entry.
    """
    result = service.calendarList().list().execute()
    return result.get("items", [])