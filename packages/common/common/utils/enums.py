from sqlalchemy import Enum as SAEnum

def pg_enum(enum_class, **kwargs):
    """
    SQLAlchemy Enum that always uses .value (lowercase) when talking to PostgreSQL.
    Use this instead of Enum() for all enum columns.
    """
    return SAEnum(
        enum_class,
        values_callable=lambda obj: [e.value for e in obj],
        **kwargs,
    )