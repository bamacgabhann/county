import os
from datetime import date, time
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
    add_result,
    update_player_participation,
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
            Session.remove()

    return wrapper


# add_club = with_session(add_club)
# add_competition = with_session(add_competition)
# add_division = with_session(add_division)
# add_group = with_session(add_group)
# add_match = with_session(add_match)
# add_player_participation = with_session(add_player_participation)
# add_player_team_association = with_session(add_player_team_association)
# add_referee = with_session(add_referee)
# add_team = with_session(add_team)
# add_team_club_association = with_session(add_team_club_association)
# add_venue = with_session(add_venue)


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
        club_name: str = row["name"]
        ainm: str | None = row["ainm"] if pd.notna(row["ainm"]) else None
        add_club(session=session, club_id=club_id, name=club_name, ainm=ainm)


@with_session
def add_referees(session, referees_df):
    for idx, row in referees_df.iterrows():
        referee_id: int = row["referee_id"]
        ref_name: str = row["name"]
        club_id: int = row["club_id"]
        add_referee(
            session=session, referee_id=referee_id, name=ref_name, club_id=club_id
        )


@with_session
def add_venues(session, venues_df):
    for idx, row in venues_df.iterrows():
        venue_id: int = row["venue_id"]
        venue_name: str = row["name"]
        club_id: int = row["club_id"]
        address: str | None = row["address"] if pd.notna(row["address"]) else None
        add_venue(
            session=session,
            venue_id=venue_id,
            name=venue_name,
            club_id=club_id,
            address=address,
        )


@with_session
def add_competitions(session, competitions_df):
    for idx, row in competitions_df.iterrows():
        competition_id: int = row["competition_id"]
        competition_name: str = row["name"]
        add_competition(
            session=session, competition_id=competition_id, name=competition_name
        )


@with_session
def add_divisions(session, divisions_df):
    for idx, row in divisions_df.iterrows():
        division_id: int = row["division_id"]
        division_name: str = row["name"]
        competition_id: int = row["competition_id"]
        add_division(
            session=session,
            division_id=division_id,
            name=division_name,
            competition_id=competition_id,
        )


@with_session
def add_groups(session, groups_df):
    for idx, row in groups_df.iterrows():
        group_id: int = row["group_id"]
        group_name: str = row["name"]
        competition_id: int = row["competition_id"]
        division_id: int = row["division_id"]
        add_group(
            session=session,
            group_id=group_id,
            name=group_name,
            competition_id=competition_id,
            division_id=division_id,
        )


@with_session
def add_teams(session, teams_df):
    for idx, row in teams_df.iterrows():
        team_id: int = row["team_id"]
        team_name: str = row["name"]
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
            name=team_name,
            competition_id=competition_id,
            division_id=division_id,
            group_id=group_id,
            club_id1=club_id1,
            club_id2=club_id2,
        )


@with_session
def add_matches(session, matches_df):
    for idx, row in matches_df.iterrows():
        match_id: int = row["match_id"]
        home_team_id: int = (
            row["home_team_id"] if pd.notna(row["home_team_id"]) else None
        )
        away_team_id: int = (
            row["away_team_id"] if pd.notna(row["away_team_id"]) else None
        )
        venue_id: int = row["venue_id"] if pd.notna(row["venue_id"]) else None
        competition_id: int = row["competition_id"]
        division_id: int = row["division_id"]
        stage: str = row["stage"]
        group_round: str = row["group_round"]
        match_no: int = row["match_no"]
        group_id: int | None = row["group_id"] if pd.notna(row["group_id"]) else None
        match_date: date | None = (
            row["match_date"] if pd.notna(row["match_date"]) else None
        )
        match_time: time | None = (
            row["match_time"] if pd.notna(row["match_time"]) else None
        )
        referee_id: int = row["referee_id"] if pd.notna(row["referee_id"]) else None

        add_match(
            session=session,
            match_id=match_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            venue_id=venue_id,
            competition_id=competition_id,
            division_id=division_id,
            stage=stage,
            group_round=group_round,
            match_no=match_no,
            group_id=group_id,
            match_date=match_date,
            match_time=match_time,
            referee_id=referee_id,
        )


@with_session
def add_new_results(session, new_results):
    for idx, row in new_results.iterrows():
        match_id: int = row["match_id"]
        home_goals: int = row["home_goals"] if pd.notna(row["home_goals"]) else None
        home_points: int = row["home_points"] if pd.notna(row["home_points"]) else None
        away_goals: int = row["away_goals"] if pd.notna(row["away_goals"]) else None
        away_points: int = row["away_points"] if pd.notna(row["away_points"]) else None
        walkover: bool = row["walkover"] if pd.notna(row["walkover"]) else False
        winner_id: int = row["winner_id"] if pd.notna(row["winner_id"]) else None

        add_result(
            session=session,
            match_id=match_id,
            home_goals=home_goals,
            home_points=home_points,
            away_goals=away_goals,
            away_points=away_points,
            walkover=walkover,
            winner_id=winner_id,
        )


@with_session
def generate_league_table_html(session, division_id):
    """Generates HTML for a league table."""

    # Start of HTML
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>League Table</title>
        <style>
            /* CSS styles */
            body {{
                font-family: sans-serif;
            }}
    .group-table .grid-row.head {
        color: white;
        background-color: rgba(0, 102, 0, 1);
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0;
        line-height: 1.25rem;
        text-align: left;
        height: 36px;
        border-spacing: 0;
        text-transform: capitalize;
    }
    .group-table .grid-row div {
        padding-top: 7px;
        padding-bottom: 9px;
    }
    .group-table .grid-row div.team {
        padding-left: 20px;
    }
    .group-table .D, .group-table .GA, .group-table .GF, .group-table .L, .group-table .P, .group-table .PA, .group-table .PF, .group-table .W, .group-table .diff, .group-table .Pts, .group-table .rank {
        text-align: center;
        font-weight: 600;
    }
    .group-table .team {
        grid-column: 1;
        grid-row: 1;
    }
    .group-table .grid-row {
        display: grid;
        grid-template-columns: 1fr 6fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;
        color: #000000;
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        letter-spacing: 0;
        line-height: 1.25rem;
    }
    .group-table .grid-row.odd {
        background-color: white;
    }
    .group-table .grid-row.even {
        background-color: rgba(0, 102, 0, 0.1);
    }

    .group-table .rank {
      grid-column: 1;
      grid-row: 1;
    }
    .group-table .team {
      grid-column: 2;
      grid-row: 1;
    }
    .group-table .P {
      grid-column: 3;
      grid-row: 1;
    }
    .group-table .W {
      grid-column: 4;
      grid-row: 1;
    }
    .group-table .D {
      grid-column: 5;
      grid-row: 1;
    }
    .group-table .L {
      grid-column: 6;
      grid-row: 1;
    }
    .group-table .GF {
      grid-column: 7;
      grid-row: 1;
    }
    .group-table .PF {
      grid-column: 8;
      grid-row: 1;
    }
    .group-table .GA {
      grid-column: 9;
      grid-row: 1;
    }
    .group-table .PA {
      grid-column: 10;
      grid-row: 1;
    }

    .group-table .diff {
      grid-column: 11;
      grid-row: 1;
    }
    .group-table .points {
      grid-column: 12;
      grid-row: 1;
    }

    td p {
      text-align: center;
    }

    td h3 {
      text-align: center;
    }

    </style>
    </head>
    <body>
    """

    groups = session.query(Group).filter_by(division_id=division_id).all()
    for group in groups:
        html += """
        <div class="group-table">
        <div class="grid-row head">
        <div class="rank  "></div>
        <div class="team  "></div>
        <div class="P  ">P</div>
        <div class="W  ">W</div>
        <div class="D  ">D</div>
        <div class="L  ">L</div>
        <div class="GF  ">GF</div>
        <div class="PF  ">PF</div>
        <div class="GA  ">GA</div>
        <div class="PA  ">PA</div>
        <div class="diff  ">+/-</div>
        <div class="Pts  ">Pts</div>
        </div>
        """

        teams = session.query(Team).filter_by(group_id=group.id).all()
        sorted_teams = sorted(teams, key=lambda team: team.league_rank)
        for team in sorted_teams:
            html += f"""
            <div class="grid-row {'even' if team.league_rank % 2 == 0 else 'odd'}">
                <div class="rank">{team.league_rank}</div>
                <div class="team">{team.name}</div>
                <div class="P">{team.played}</div>
                <div class="W">{team.won}</div>
                <div class="D">{team.drawn}</div>
                <div class="L">{team.lost}</div>
                <div class="GF">{team.goals_for}</div>
                <div class="PF">{team.points_for}</div>
                <div class="GA">{team.goals_against}</div>
                <div class="PA">{team.points_against}</div>
                <div class="diff">{team.scoring_difference_x_wo}</div>
                <div class="points">{team.league_points}</div>
            </div>
            """
    html += """
            </body>
            </html>
            """
    fname = f"outputs/league_table_{division_id}.html"
    with open(fname, "w") as file:
        file.write(html)


name = "County Competitions"
__version__ = "0.1.0"
__author__ = "Breandán Anraoi MacGabhann"
