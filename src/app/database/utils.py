from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):  # noqa: N801
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):  # noqa: ANN201, ANN003, ARG001, ANN001
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
