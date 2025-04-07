import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker

from .create_competitions import (  # noqa F401
    add_club,
    add_competition,
    add_division,
    add_group,
    add_match,
    add_player,
    add_player_participation,
    add_player_team_association,
    add_referee,
    add_team,
    add_team_club_association,
    add_venue,
)
from .create_schema import (  # noqa F401
    Base,
    Club,
    Competition,
    Division,
    Group,
    Match,
    Player,
    PlayerParticipation,
    Referee,
    Team,
    Venue,
    player_team_association,
    team_club_association,
)
from .update_matches import (  # noqa F401
    update_player_participation,
    update_score,
)

# Global variable to store the engine
engine = None


def get_engine(db_url=None):
    """Creates a database engine with the provided URL or from environment variables."""
    if db_url is None:
        db_url = os.environ.get("DATABASE_URL")
    if db_url is None:
        raise ValueError("DATABASE_URL environment variable not set.")
    return create_engine(db_url)


def get_session(db_url=None):
    """Returns a session object."""

    global engine  # Use global engine

    if engine is None:  # Create engine if it doesn't exist
        engine = get_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    return Session()


def initialise(db_url=None):
    """Creates the database schema."""
    global engine  # Use global engine
    # Create the database engine
    Session = get_session(db_url)
    # Create the database tables if they do not exist
    inspector = inspect(engine)
    if not inspector.has_table("clubs"):  # Check for one of the tables
        Base.metadata.create_all(engine)
    return Session


name = "County Competitions"
__version__ = "0.1.0"
__author__ = "Breandán Anraoi MacGabhann"
