"""
solar and lunar data helpers

Public API
----------
fetch_astral_data(city, region, timezone, lat, lon) -> AstralData
"""

import datetime
import math
from dataclasses import dataclass

from astral import LocationInfo
from astral.sun import sun
from astral.moon import phase as moon_phase   # returns float 0–28 (age in days)


# Mean synodic month length in days
_SYNODIC_MONTH = 29.53058770576

# Quarter-phase targets within one cycle, paired with their display names.
# The sentinel at the end handles wrap-around when age is near 29.5.
_NAMED_PHASES: list[tuple[float, str]] = [
    (_SYNODIC_MONTH * 0 / 4, "New Moon"),        # 0.0 d
    (_SYNODIC_MONTH * 1 / 4, "First Quarter"),   # ~7.4 d
    (_SYNODIC_MONTH * 2 / 4, "Full Moon"),        # ~14.8 d
    (_SYNODIC_MONTH * 3 / 4, "Last Quarter"),     # ~22.1 d
    (_SYNODIC_MONTH,         "New Moon"),          # 29.5 d – wrap sentinel
]

# Within this many days of a named phase, show "tonight" instead of "in N days"
_PHASE_THRESHOLD = 0.75


@dataclass(frozen=True)
class AstralData:
    """All solar/lunar values needed by the display widgets."""
    sunrise:         datetime.datetime   # timezone-aware, local time
    sunset:          datetime.datetime   # timezone-aware, local time
    illumination:    float               # 0.0 (new) → 1.0 (full) → 0.0
    phase_angle:     float               # 0–360 (0/360=new, 180=full)
    days_to_next:    int                 # whole days until next named phase
    next_phase_name: str                 # e.g. "Full Moon", "Last Quarter"


def _moon_illumination(phase_angle_deg: float) -> float:
    """Fraction of the lunar disc that is illuminated (0.0–1.0)."""
    return (1.0 - math.cos(math.radians(phase_angle_deg))) / 2.0


def _next_phase(age: float) -> tuple[int, str]:
    """
    Given the moon's age in days, return (days_to_next, phase_name).

    Uses math.ceil so that 0.4 days away shows as "in 1 day" rather than
    the misleading "tonight".  Only returns days_to_next=0 when we are
    within _PHASE_THRESHOLD days of the phase.
    """
    for phase_age, phase_label in _NAMED_PHASES:
        days_away = phase_age - age
        if days_away >= 0:
            if days_away < _PHASE_THRESHOLD:
                return 0, phase_label
            return math.ceil(days_away), phase_label

    # Unreachable given the sentinel, but be defensive
    return 0, "New Moon"


def fetch_astral_data(city: str, region: str, timezone: str,
                      lat: float, lon: float) -> AstralData:
    """
    Return solar and lunar data for today at the given location.

    Parameters
    ----------
    city, region, timezone : str
        Passed directly to astral.LocationInfo.
    lat, lon : float
        Decimal-degree coordinates (positive = N/E).

    Returns
    -------
    AstralData
        Frozen dataclass; access fields by name, e.g. data.sunrise.
    """
    location = LocationInfo(city, region, timezone, lat, lon)
    today    = datetime.date.today()

    s       = sun(location.observer, date=today, tzinfo=location.timezone)
    sunrise = s["sunrise"]
    sunset  = s["sunset"]

    age          = moon_phase(today)                   # 0–28 days
    phase_angle  = (age / _SYNODIC_MONTH) * 360.0     # 0–360°
    illumination = _moon_illumination(phase_angle)

    days_to_next, next_phase_name = _next_phase(age)

    return AstralData(
        sunrise         = sunrise,
        sunset          = sunset,
        illumination    = illumination,
        phase_angle     = phase_angle,
        days_to_next    = days_to_next,
        next_phase_name = next_phase_name,
    )