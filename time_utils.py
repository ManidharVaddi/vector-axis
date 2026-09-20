from datetime import datetime, timedelta, date

IST_OFFSET = timedelta(hours=5, minutes=30)

CHECKIN_START_HOUR = 21  # 9:00 PM
CHECKIN_END_HOUR = 23   # 11:00 PM


def get_ist_now() -> datetime:
    """
    Returns current time in IST, calculated from UTC - does not depend on
    the device's local timezone setting.
    """
    utc_now = datetime.utcnow()
    return utc_now + IST_OFFSET


def get_ist_today() -> date:
    return get_ist_now().date()


def is_checkin_window_open() -> bool:
    """True only between 9:00 PM and 11:00 PM IST."""
    now = get_ist_now()
    return CHECKIN_START_HOUR <= now.hour < CHECKIN_END_HOUR