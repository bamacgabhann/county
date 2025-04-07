import os
from functools import wraps

import pandas as pd
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
Session = None


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
    global Session  # Use global Session
    if engine is None:  # Create engine if it doesn't exist
        engine = get_engine(db_url)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    return Session


def initialise(db_url=None):
    """Creates the database schema."""
    global engine  # Use global engine
    global Session  # Use global Session
    # Create the database engine
    Session = get_session(db_url)
    # Create the database tables if they do not exist
    inspector = inspect(engine)
    if not inspector.has_table("clubs"):  # Check for one of the tables
        Base.metadata.create_all(engine)
    return Session


@with_session
def add_clubs(session, clubs_df):
    for idx, row in clubs_df.iterrows():
        club_id: int = row["club_id"]
        name: str = row["name"]
        ainm: str | None = row["ainm"] if pd.notna(row["ainm"]) else None
        add_club(session=session, club_id=club_id, name=name, ainm=ainm)


@with_session
def add_referees(session, referees_df):
    for idx, row in referees_df.iterrows():
        referee_id: int = row["referee_id"]
        name: str = row["name"]
        club_id: int = row["club_id"]
        add_referee(session=session, referee_id=referee_id, name=name, club_id=club_id)


@with_session
def add_venues(session, venues_df):
    for idx, row in venues_df.iterrows():
        venue_id: int = row["venue_id"]
        name: str = row["name"]
        club_id: int = row["club_id"]
        address: str | None = row["address"] if pd.notna(row["address"]) else None
        add_venue(
            session=session,
            venue_id=venue_id,
            name=name,
            club_id=club_id,
            address=address,
        )


@with_session
def add_competitions(session, competitions_df):
    for idx, row in competitions_df.iterrows():
        competition_id: int = row["competition_id"]
        name: str = row["name"]
        add_competition(session=session, competition_id=competition_id, name=name)


@with_session
def add_divisions(session, divisions_df):
    for idx, row in divisions_df.iterrows():
        division_id: int = row["division_id"]
        name: str = row["name"]
        competition_id: int = row["competition_id"]
        add_division(
            session=session,
            division_id=division_id,
            name=name,
            competition_id=competition_id,
        )


@with_session
def add_groups(session, groups_df):
    for idx, row in groups_df.iterrows():
        group_id: int = row["group_id"]
        name: str = row["name"]
        competition_id: int = row["competition_id"]
        division_id: int = row["division_id"]
        add_group(
            session=session,
            group_id=group_id,
            name=name,
            competition_id=competition_id,
            division_id=division_id,
        )


@with_session
def add_teams(session, teams_df):
    for idx, row in teams_df.iterrows():
        team_id: int = row["team_id"]
        name: str = row["name"]
        competition_id: int = row["competition_id"]
        division_id: int = row["division_id"]
        group_id: int = row["group_id"]
        club_id1: int = row["club_id1"]
        club_id2: int | None = (
            int(row["club_id2"]) if pd.notna(row["club_id2"]) else None
        )
        add_team(
            session=session,
            team_id=team_id,
            name=name,
            competition_id=competition_id,
            division_id=division_id,
            group_id=group_id,
            club_id1=club_id1,
            club_id2=club_id2,
        )


name = "County Competitions"
__version__ = "0.1.0"
__author__ = "Breandán Anraoi MacGabhann"
