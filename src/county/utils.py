from functools import wraps

from . import Session  # Assuming Session factory is available in __init__.py


def with_session(func):
    """Decorator to manage SQLAlchemy sessions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            result = func(session, *args, **kwargs)
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.remove()

    return wrapper
