import math
from datetime import UTC, datetime

from app.utils import timezone_validator


def test_timezone_validator() -> None:
    t1 = datetime.now()  # noqa: DTZ005

    t1_validated = timezone_validator(t1)

    assert math.isclose(t1_validated.timestamp(), t1.replace(tzinfo=UTC).timestamp()) is True
    assert t1_validated.tzinfo is not None
    assert t1_validated.tzinfo.utcoffset(t1_validated) is not None
    assert t1_validated.tzinfo.tzname == UTC.tzname
