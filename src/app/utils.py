from datetime import UTC, datetime


def timezone_validator(value: datetime) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = value.replace(tzinfo=UTC)
    return value
