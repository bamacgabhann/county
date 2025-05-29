import os
from datetime import date, time, timedelta
from functools import wraps

import pandas as pd
from PIL import Image, ImageDraw, ImageFont  # Import necessary libraries
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
    update_date,
    update_date_time,
    update_league_ranks,
    update_player_participation,
    update_referee,
    update_time,
    update_venue,
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
        print("Adding result for match_id:", match_id)
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


def generate_league_page_html(session, division_id):
    """Generates HTML for a league table."""

    # Start of HTML
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>League Table, Results, and Fixtures</title>
    <style>
        /* CSS styles */
        body {
            font-family: sans-serif;
        }
        .h2 {
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: rgba(0, 102, 0, 1);
        letter-spacing: 0;
        line-height: 2rem;
        margin-top: 20px;
    }
    .container {
        grid-template-columns: 1fr; /* Single column for all screen sizes */
        grid-gap: 20px; /* Gap between rows */
    }

    .table-row {
        grid-column: 1;
        grid-row: 1;
    }

    .fixtures-results-container { /* Styles for smaller screens */
        display: grid;
        grid-template-columns: 1fr; /* Single column */
        grid-template-rows: auto auto; /* Two rows for Results and Fixtures */
        grid-gap: 20px; /* Gap between rows */
        grid-column: 1;
        grid-row: 2;
    }

    .results-column {
        grid-column: 1;
        grid-row: 1;
    }

    .fixtures-column {
        grid-column: 1;
        grid-row: 2;
    }

    @media (min-width: 768px) { /* Example breakpoint - adjust as needed */
        .fixtures-results-container {
            grid-template-columns: 1fr 1fr; /* Two columns for Results and Fixtures */
            grid-template-rows: auto; /* Single row */
        }

        .results-column {
            grid-column: 1;
            grid-row: 1;
        }

        .fixtures-column {
            grid-column: 2;
            grid-row: 1;
        }
    }
    .results-container, .fixtures-container, .group-table-container {
        display: grid; /* Ensure grid layout within containers */
    }

    .group-table { /* Apply grid display to the container */
        display: grid;
    }


    .group-table .grid-row div {
        padding-top: 7px;
        padding-bottom: 9px;
    }
    .group-table .grid-row div.team {
        padding-left: 20px;
    }
    .group-table .D, .group-table .GA, .group-table .GF, .group-table .L, .group-table .P, .group-table .PA, .group-table .PF, .group-table .W, .group-table .diff, .group-table .points, .group-table .rank {
        text-align: center;
        font-weight: 600;
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
    .group-table .grid-row.head {
        display: grid;
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
        /* Hide GF, PF, GA, PA on smaller screens */
    @media (max-width: 600px) { /* Adjust breakpoint as needed */
        .group-table .GF,
        .group-table .PF,
        .group-table .GA,
        .group-table .PA {
            display: none;
        }

        /* Adjust grid template columns for smaller screens */
        .group-table .grid-row {
            grid-template-columns: 1fr 6fr 1fr 1fr 1fr 1fr 1fr 1fr; /* Reduced number of columns */
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

        .group-table .diff {
          grid-column: 7;
          grid-row: 1;
        }
        .group-table .points {
          grid-column: 8;
          grid-row: 1;
        }
    }

    .fixtures-container {
        background-color: #EEECEC;
        margin-top: 20px; /* top padding */
    }

    .fixtures-container .grid-row {
        display: grid;
        grid-template-columns: 5fr 1fr 5fr;
        grid-template-areas: "home_fix vs away_fix";
        color: #000000;
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        letter-spacing: 0;
        line-height: 1rem;
        padding-top: 7px; /* top padding */
    }

    .fixtures-container .grid-row.head {
        color: white;
        background-color: rgba(0, 102, 0, 1);
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0;
        line-height: 1.25rem;
        /* Vertically center and add left padding */
        display: flex;
        align-items: center; /* Vertical centering */
        padding-left: 20px; /* Left padding */
        height: 36px;
        padding-top: 0; /* top padding */
        border-spacing: 0;
        text-transform: capitalize;
    }

    .fixtures-container h3.date { /* Target the date heading specifically */
        margin: 0; /* Remove default margins */
    }

    .fixtures-container .H {
        grid-area: home_fix;
        padding-left: 20px;
        text-align: left;
        font-weight: 500;
    }
    .fixtures-container .A {
        grid-area: away_fix;
        padding-right: 20px;
        text-align: right;
        font-weight: 500;
    }
    .fixtures-container .vs {
        grid-area: vs;
        text-align: center;
        font-weight: 400;
    }

        /* Style the footer row */
    .fixtures-container .grid-row.footer {
        display: grid;
        grid-template-columns: 1fr;
        padding-bottom: 7px;
    }

    .fixtures-container .footer-text {
        grid-column: 1;
        margin: 0; /* Remove default margins */
        font-family: "IBM Plex Sans", sans-serif;
        letter-spacing: 0;
        line-height: 0.8rem;
        text-align: center; /* Center the content */
        font-size: 0.8rem; /* Smaller font size */
        color: #444444; /* Lighter text color */
        padding-bottom: 5px;
    }
    .fixtures-container > .grid-row > div { /* Select direct div children of grid-row */
        margin: 0; /* Remove any default margins */
    }

    .fixtures-container > .grid-row > div > p { /* Select the <p> within the divs */
        margin: 0; /* Remove default margins from the <p> */
    }

    .results-container {
        background-color: #EEECEC;
        margin-top: 20px; /* top padding */
    }

    .results-container h3.date { /* Target the date heading specifically */
        margin: 0; /* Remove default margins */
    }

    .results-container .grid-row {
        display: grid;
        grid-template-columns: 6fr 2fr 2fr 6fr;
        grid-template-areas: "r-home hs as r-away";
        color: #000000;
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        letter-spacing: 0;
        padding-top: 7px; /* top padding */
        line-height: 1rem;
    }

    .results-container .grid-row.head {
        color: white;
        background-color: rgba(0, 102, 0, 1);
        font-family: "IBM Plex Sans", sans-serif;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0;
        line-height: 1.25rem;
        /* Vertically center and add left padding */
        display: flex;
        align-items: center; /* Vertical centering */
        padding-left: 20px; /* Left padding */
        height: 36px;
        padding-top: 0; /* top padding */
        border-spacing: 0;
        text-transform: capitalize;
    }

    .results-container .H {
        grid-area: r-home;
        padding-left: 20px;
        text-align: left;
        font-weight: 500;
    }
    .results-container .HS {
        grid-area: hs;
        padding-right: 20px;
        text-align: center;
        font-weight: 400;
    }
    .results-container .AS {
        grid-area: as;
        padding-left: 20px;
        text-align: center;
        font-weight: 400;
    }

    .results-container .A {
        grid-area: r-away;
        padding-right: 20px;
        text-align: right;
        font-weight: 500;
    }


        /* Style the footer row */
    .results-container .grid-row.footer {
        display: grid;
        grid-template-columns: 1fr;
        padding-bottom: 7px;
    }

    .results-container .footer-text {
        grid-column: 1;
        margin: 0; /* Remove default margins */
        font-family: "IBM Plex Sans", sans-serif;
        letter-spacing: 0;
        line-height: 0.8rem;
        text-align: center; /* Center the content */
        font-size: 0.8rem; /* Smaller font size */
        color: #444444; /* Lighter text color */
        padding-bottom: 5px;
    }
    .results-container > .grid-row > div { /* Select direct div children of grid-row */
        margin: 0; /* Remove any default margins */
    }

    .results-container > .grid-row > div > p { /* Select the <p> within the divs */
        margin: 0; /* Remove default margins from the <p> */
    }

</style>
</head>
<body>
  <div class="container">
    <div class="group-table-container">
    """

    groups = session.query(Group).filter_by(division_id=division_id).all()

    for group in groups:

        if group.name == "(single group)":
            table_title = f"{group.division.name}"
        else:
            table_title = f"{group.name}"

        html += f"""

      <div class="group-table">
        <div class="grid-row head">
          <div class="rank  "></div>
          <div class="team  ">{table_title}</div>
          <div class="P  ">P</div>
          <div class="W  ">W</div>
          <div class="D  ">D</div>
          <div class="L  ">L</div>
          <div class="GF  ">GF</div>
          <div class="PF  ">PF</div>
          <div class="GA  ">GA</div>
          <div class="PA  ">PA</div>
          <div class="diff  ">+/-</div>
          <div class="points  ">Pts</div>
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

        # close group-table
        html += """
      </div>
        """

    # close group-table-container
    html += """
    </div>
    """

    # add fixtures-results-container
    html += """
    <div class="fixtures-results-container">
    """

    # add results container
    html += """
      <div class="results-column">
        <div class="h2">Results</div>
    """

    results = (
        session.query(Match)
        .filter(Match.division_id == division_id, Match.date <= date.today())
        .all()
    )
    unique_dates = sorted(list({result.date for result in results}), reverse=True)

    for match_date in unique_dates:  # Iterate through unique dates and add date heading
        html += f"""
        <div class="results-container">
          <div class="grid-row head">
            <h3 class="date">{match_date.strftime('%A %d %B %Y')}</h3>
          </div>
    """
        matches_on_date = [
            result for result in results if result.date == match_date
        ]  # Filter matches for current date
        for match in matches_on_date:
            if (
                match.winner_id is None
                and match.home_goals is None
                and match.away_goals is None
                and match.home_points is None
                and match.away_points is None
            ):
                continue
            home_team_name = (
                f"<strong>{match.home_team.name}</strong>"
                if (match.winner_id == match.home_team_id)
                else match.home_team.name
            )
            away_team_name = (
                f"<strong>{match.away_team.name}</strong>"
                if (match.winner_id == match.away_team_id)
                else match.away_team.name
            )
            if match.walkover:
                home_score = "W/O" if (match.winner_id == match.home_team_id) else "X"
                away_score = "W/O" if (match.winner_id == match.away_team_id) else "X"
            else:
                home_score = f"{match.home_goals}-{match.home_points:02}"
                away_score = f"{match.away_goals}-{match.away_points:02}"

            html += f"""
          <div class="grid-row">
            <div class="H">
              <p class="team-name team-home ">{home_team_name}</p>
            </div>
            <div class="HS">
              <p class="match-main-info">{home_score}</p>
            </div>
            <div class="AS">
              <p class="match-main-info">{away_score}</p>
            </div>
            <div class="A">
              <p class="team-name team-away">{away_team_name}</p>
            </div>
          </div>
                """
            # Add footer row for each match
            if match.referee:  # Check if referee is available
                html += f"""
          <div class="grid-row footer">
            <p class="footer-text">Referee: {match.referee.name} ({match.referee.club.name})</p>
          </div>
                """

        # Close results-container
        html += """
        </div>

        """

    # Close results-column
    html += """
      </div>
      """

    # add fixtures container
    html += """
      <div class="fixtures-column">
        <div class="h2">Fixtures</div>
        """

    fixtures = (
        session.query(Match)
        .filter(
            Match.division_id == division_id,
            Match.stage == "group",
            Match.date > date.today(),
        )
        .all()
    )
    fixture_dates = sorted(list({fixture.date for fixture in fixtures}))

    for match_date in fixture_dates:  # Iterate through unique dates
        html += f"""
        <div class="fixtures-container">
          <div class="grid-row head">
            <h3 class="date">{match_date.strftime('%A %d %B %Y')}</h3>
          </div>
    """  # Add date heading
        matches_on_date = [
            fixture for fixture in fixtures if fixture.date == match_date
        ]  # Filter matches for current date
        for match in matches_on_date:
            html += f"""
          <div class="grid-row">
            <div class="H">
              <p class="team-name team-home ">{match.home_team.name}</p>
            </div>
            <div class="vs"><p>v</p></div>
            <div class="A">
              <p class="team-name team-away">{match.away_team.name}</p>
            </div>
          </div>
          <div class="grid-row footer">
            <p class="footer-text">Throw-in: {match.time.strftime('%H:%M')}, {match.venue.name}
                """
            # Add footer row for each match
            if match.referee:  # Check if referee is available
                html += f"""(Referee: {match.referee.name})
                """
            html += """
            </p>
          </div>
        """

        # Close fixtures-container
        html += """
        </div>
                """

    # Close fixtures-container, fixtures-results-container, container, body, html
    html += """
      </div>
    </div>
  </div>
</body>
</html>
            """

    if not os.path.exists("outputs"):
        os.makedirs("outputs")
    current_div = session.query(Division).filter_by(id=division_id).first()
    fname = f"outputs/league_page_{current_div.name}.html"
    with open(fname, "w") as file:
        file.write(html)


@with_session
def generate_div_page(session, division_id):
    """Generates HTML for a league table."""
    generate_league_page_html(session, division_id)


@with_session
def generate_all_pages(session):
    """Generates HTML for all league tables."""
    divisions = session.query(Division).all()
    for division in divisions:
        generate_league_page_html(session, division.id)


@with_session
def update_match_referee(session, match_id, referee_id):
    """Updates the referee for a match."""
    update_referee(session, match_id, referee_id)


@with_session
def update_match_date(session, match_id, match_date):
    """Updates the date for a match."""
    update_date(session, match_id, match_date.date())


@with_session
def update_match_time(session, match_id, match_time):
    """Updates the date for a match."""
    update_time(session, match_id, match_time.time())


@with_session
def update_match_datetime(session, match_id, match_datetime):
    """Updates the date for a match."""
    update_date(session, match_id, match_datetime.date())
    update_time(session, match_id, match_datetime.time())


@with_session
def update_match_venue(session, match_id, venue_id):
    """Updates the venue for a match."""
    update_venue(session, match_id, venue_id)


def add_fixtures_to_image(draw, font, fixtures, y_position):
    """Helper function to add fixtures to the image."""

    for match in fixtures:
        time_str = match.time.strftime("%H:%M")
        home_team = match.home_team.name
        away_team = match.away_team.name
        venue_referee = f"{match.venue.name}. Referee: {match.referee.name}"

        # Add fixture details to image, with formatting and background colors
        draw.text((50, y_position), time_str, font=font, fill="black")
        draw.text(
            (200, y_position),
            home_team,
            font=font,
            fill="black",
            background="rgba(0, 102, 0, 0.5)",
        )  # Semi-transparent green
        draw.text(
            (540, y_position),
            "v",
            font=font,
            fill="black",
            background="rgba(255, 255, 255, 0.5)",
        )  # Semi-transparent white
        draw.text(
            (800, y_position),
            away_team,
            font=font,
            fill="black",
            background="rgba(0, 102, 0, 0.5)",
        )  # Semi-transparent green
        y_position += 40  # Increment y-position for next row
        draw.text((50, y_position), venue_referee, font=font, fill="black")
        y_position += 60  # Increment y-position for next fixture

    return y_position


def add_results_to_image(draw, font, results, y_position):
    """Helper function to add results to the image."""

    for match in results:
        time_str = match.time.strftime("%H:%M")
        home_team = match.home_team.name
        away_team = match.away_team.name
        home_score = f"{match.home_goals}-{match.home_points:02}"
        away_score = f"{match.away_goals}-{match.away_points:02}"
        venue_referee = f"{match.venue.name}. Referee: {match.referee.name}"

        # Add result details to image, with formatting and background colors
        draw.text((50, y_position), time_str, font=font, fill="black")
        draw.text(
            (200, y_position),
            home_team,
            font=font,
            fill="black",
            background="rgba(0, 102, 0, 0.5)",
        )  # Semi-transparent green
        draw.text(
            (540, y_position),
            home_score,
            font=font,
            fill="black",
            background="rgba(255, 255, 255, 0.5)",
        )  # Semi-transparent white
        draw.text(
            (800, y_position),
            away_score,
            font=font,
            fill="black",
            background="rgba(0, 102, 0, 0.5)",
        )  # Semi-transparent green
        draw.text(
            (900, y_position),
            away_team,
            font=font,
            fill="black",
            background="rgba(255, 255, 255, 0.5)",
        )  # Semi-transparent white
        y_position += 40  # Increment y-position for next row
        draw.text((50, y_position), venue_referee, font=font, fill="black")
        y_position += 60  # Increment y-position for next result

    return y_position


@with_session
def instagram_division_results(session, division_id, start_date, days=0):
    """Generates Instagram image with results and tables for a division on a particular date."""

    division = session.query(Division).filter_by(id=division_id).first()
    groups = session.query(Group).filter_by(division_id=division_id).all()

    # Create a new image with the specified dimensions and background
    image = Image.new("RGB", (1080, 1350), color="white")
    bg_image = Image.open("data/fix_bg.png")  # Open background image
    image.paste(bg_image, (0, 0))  # Paste background image

    draw = ImageDraw.Draw(image, "RGBA")
    font_title = ImageFont.truetype("data/klima-bold-web.ttf", 60)  # Load fonts
    font_subtitle = ImageFont.truetype("data/klima-medium-italic-web.ttf", 40)
    font_section = ImageFont.truetype("data/klima-medium-web.ttf", 30)
    font_name = ImageFont.truetype("data/klima-regular-web.ttf", 30)
    font_stats = ImageFont.truetype("data/klima-light-web.ttf", 30)

    # initial coordinates
    x1 = 50
    x2 = 1030
    y1 = 100  # 180
    x_rank = 70
    x_name = 140
    x_logo = 95
    x_g = 60
    x_p = 600
    x_w = 640
    x_d = 680
    x_l = 720
    x_f = 785
    x_a = 875
    x_diff = 950
    x_pts = 1005
    x_home_l = 440
    x_home_m = 485
    x_home_r = 530
    x_away_l = 550
    x_away_m = 595
    x_away_r = 640
    x_home_name = 100
    x_away_name = 980
    x_home_logo = 60
    x_away_logo = 990

    # define background colours
    table_head_bg = "#ffffffbf"  # "rgba(255, 255, 255, 0.75)"
    row_bg_odd = "#2d8c3380"  # rgba(45, 140, 51, 0.5)"
    row_bg_even = "#ffffff33"  # "rgba(255, 255, 255, 0.2)"
    result_bg = "#ffffff80"  # "rgba(255, 255, 255, 0.5)"

    # Add uppercase division name as title

    if division.competition_id < 3:
        title = f"{division.competition.name.upper()} {division.name.upper()}"
    else:
        title = division.name.upper()
    draw.text((540, y1), title, font=font_title, fill="white", anchor="ms")
    y1 += 20

    # Add league tables

    for group in groups:
        y2 = y1 + 40

        # Header row
        y3 = y1 + 31

        draw.rectangle([x1, y1, x2, y2], fill=table_head_bg)
        draw.text(
            (x_g, y3),
            group.name if len(groups) > 1 else division.name,
            font=font_section,
            fill="black",
            anchor="ls",
        )
        draw.text((x_p, y3), "P", font=font_stats, fill="black", anchor="ms")
        draw.text((x_w, y3), "W", font=font_stats, fill="black", anchor="ms")
        draw.text((x_d, y3), "D", font=font_stats, fill="black", anchor="ms")
        draw.text((x_l, y3), "L", font=font_stats, fill="black", anchor="ms")
        draw.text((x_f, y3), "F", font=font_stats, fill="black", anchor="ms")
        draw.text((x_a, y3), "A", font=font_stats, fill="black", anchor="ms")
        draw.text((x_diff, y3), "+/-", font=font_stats, fill="black", anchor="ms")
        draw.text((x_pts, y3), "Pts", font=font_stats, fill="black", anchor="ms")

        y1 = y2

        teams = session.query(Team).filter_by(group_id=group.id).all()
        sorted_teams = sorted(teams, key=lambda team: team.league_rank)

        for team in sorted_teams:
            y2 = y1 + 40
            y3 = y1 + 31
            draw.rectangle(
                [x1, y1, x2, y2],
                fill=(row_bg_even if team.league_rank % 2 == 0 else row_bg_odd),
            )
            draw.text(
                (x_rank, y3),
                str(team.league_rank),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            # Draw team logo
            try:
                logo = Image.open(f"data/logos/logo30_{team.clubs[0].name}.png")
                image.paste(logo, (x_logo, y1 + 5))
            finally:
                pass
            draw.text(
                (x_name, y3), team.name, font=font_name, fill="white", anchor="ls"
            )
            draw.text(
                (x_p, y3), str(team.played), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_w, y3), str(team.won), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_d, y3), str(team.drawn), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_l, y3), str(team.lost), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_f, y3),
                f"{team.goals_for}-{team.points_for}",
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_a, y3),
                f"{team.goals_against}-{team.points_against}",
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_diff, y3),
                str(team.scoring_difference_x_wo),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_pts, y3),
                str(team.league_points),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            y1 = y2

        y1 += 20

    # Define date range
    date_range = [start_date]
    if days > 0:
        date_range.extend(start_date + timedelta(days=i) for i in range(1, days + 1))
    for results_date in date_range:
        if (
            results := session.query(Match)
            .filter_by(division_id=division_id, date=results_date)
            .filter(
                (
                    (Match.home_goals >= 0)
                    & (Match.away_goals >= 0)
                    & (Match.home_points >= 0)
                    & (Match.away_points >= 0)
                )
                | Match.walkover
            )
            .all()
        ):
            # Add date as subtitle - format day-name dd month yyyy
            date_str = results_date.strftime("%A %d %B %Y")
            draw.text(
                (540, y1 + 35),
                date_str,
                font=font_subtitle,
                fill="lightgray",
                anchor="ms",
            )
            y1 += 50

            # Add results

            for result in results:
                y2 = y1 + 50
                y3 = y1 + 36

                match result.home_team.name:
                    case "Templeglantine/Knockaderry":
                        home_name = "Templegl / Knockaderry"
                    case "Croagh-Kilfinny / Crecora":
                        home_name = "Croagh-Kilf / Crecora"
                    case _:
                        home_name = result.home_team.name

                match result.away_team.name:
                    case "Templeglantine/Knockaderry":
                        away_name = "Templegl / Knockaderry"
                    case "Croagh-Kilfinny / Crecora":
                        away_name = "Croagh-Kilf / Crecora"
                    case _:
                        away_name = result.away_team.name

                draw.rectangle([x1, y1, x2, y2], fill=result_bg)
                draw.rectangle([x_home_l, y1, x_home_r, y2], fill="white")
                draw.rectangle([x_away_l, y1, x_away_r, y2], fill="white")
                # home logo here
                try:
                    logo = Image.open(
                        f"data/logos/logo30_{result.home_team.clubs[0].name}.png"
                    )
                    image.paste(logo, (x_home_logo, y1 + 10))
                finally:
                    pass

                if result.walkover:
                    if result.winner_id == result.home_team_id:
                        home_score = "W/O"
                        away_score = "X"
                    elif result.winner_id == result.away_team_id:
                        home_score = "X"
                        away_score = "W/O"
                else:
                    home_score = f"{result.home_goals}-{result.home_points:02}"
                    away_score = f"{result.away_goals}-{result.away_points:02}"

                draw.text(
                    (x_home_name, y3),
                    home_name,
                    font=font_name,
                    fill="black",
                    anchor="ls",
                )
                draw.text(
                    (x_home_m, y3),
                    home_score,
                    font=font_name,
                    fill="black",
                    anchor="ms",
                )
                draw.text(
                    (x_away_m, y3),
                    away_score,
                    font=font_name,
                    fill="black",
                    anchor="ms",
                )
                draw.text(
                    (x_away_name, y3),
                    away_name,
                    fill="black",
                    anchor="rs",
                    font=font_name,
                )
                # away logo here
                try:
                    logo = Image.open(
                        f"data/logos/logo30_{result.away_team.clubs[0].name}.png"
                    )
                    image.paste(logo, (x_away_logo, y1 + 10))
                finally:
                    pass

                y1 = y2 + 20

    image.save(f"outputs/results_{division.name}_{results_date.strftime('%Y%m%d')}.png")
    image.save(f"outputs/results_{division.name}_{results_date.strftime('%Y%m%d')}.png")


@with_session
def instagram_division_fixtures(session, division_id, start_date, days=0):
    """Generates Instagram image with fixtures for a division on a particular date range."""

    division = session.query(Division).filter_by(id=division_id).first()
    groups = session.query(Group).filter_by(division_id=division_id).all()

    # Create a new image with the specified dimensions and background
    image = Image.new("RGB", (1080, 1350), color="white")
    bg_image = Image.open("data/fix_bg.png")  # Open background image
    image.paste(bg_image, (0, 0))  # Paste background image

    draw = ImageDraw.Draw(image, "RGBA")
    font_title = ImageFont.truetype("data/klima-bold-web.ttf", 60)  # Load fonts
    font_subtitle = ImageFont.truetype("data/klima-medium-italic-web.ttf", 40)
    font_section = ImageFont.truetype("data/klima-medium-web.ttf", 30)
    font_name = ImageFont.truetype("data/klima-regular-web.ttf", 30)
    font_stats = ImageFont.truetype("data/klima-light-web.ttf", 30)
    font_info = ImageFont.truetype("data/klima-light-italic-web.ttf", 20)

    # initial coordinates
    x1 = 50
    x2 = 1030
    y1 = 100
    x_rank = 70
    x_name = 140
    x_logo = 95
    x_g = 60
    x_p = 600
    x_w = 640
    x_d = 680
    x_l = 720
    x_f = 785
    x_a = 875
    x_diff = 950
    x_pts = 1005
    x_fix_time = 60
    x_home_logo = 150
    x_home_name = 190
    x_v = 585
    x_away_name = 980
    x_away_logo = 990

    # define background colours
    table_head_bg = "#ffffffbf"  # "rgba(255, 255, 255, 0.75)"
    row_bg_odd = "#2d8c3380"  # rgba(45, 140, 51, 0.5)"
    row_bg_even = "#ffffff33"  # "rgba(255, 255, 255, 0.2)"
    result_bg = "#ffffff80"  # "rgba(255, 255, 255, 0.5)"

    # Add uppercase division name as title
    if division.competition_id < 3:
        title = f"{division.competition.name.upper()} {division.name.upper()}"
    else:
        title = division.name.upper()
    draw.text((540, y1), title, font=font_title, fill="white", anchor="ms")
    y1 += 30

    # Add league tables

    for group in groups:
        y2 = y1 + 40

        # Header row
        y3 = y1 + 31

        draw.rectangle([x1, y1, x2, y2], fill=table_head_bg)
        draw.text(
            (x_g, y3),
            group.name if len(groups) > 1 else division.name,
            font=font_section,
            fill="black",
            anchor="ls",
        )
        draw.text((x_p, y3), "P", font=font_stats, fill="black", anchor="ms")
        draw.text((x_w, y3), "W", font=font_stats, fill="black", anchor="ms")
        draw.text((x_d, y3), "D", font=font_stats, fill="black", anchor="ms")
        draw.text((x_l, y3), "L", font=font_stats, fill="black", anchor="ms")
        draw.text((x_f, y3), "F", font=font_stats, fill="black", anchor="ms")
        draw.text((x_a, y3), "A", font=font_stats, fill="black", anchor="ms")
        draw.text((x_diff, y3), "+/-", font=font_stats, fill="black", anchor="ms")
        draw.text((x_pts, y3), "Pts", font=font_stats, fill="black", anchor="ms")

        y1 = y2

        teams = session.query(Team).filter_by(group_id=group.id).all()
        sorted_teams = sorted(teams, key=lambda team: team.league_rank)

        for team in sorted_teams:
            y2 = y1 + 40
            y3 = y1 + 31
            draw.rectangle(
                [x1, y1, x2, y2],
                fill=(row_bg_even if team.league_rank % 2 == 0 else row_bg_odd),
            )
            draw.text(
                (x_rank, y3),
                str(team.league_rank),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            # Draw team logo
            try:
                logo = Image.open(f"data/logos/logo30_{team.clubs[0].name}.png")
                image.paste(logo, (x_logo, y1 + 5))
            finally:
                pass
            draw.text(
                (x_name, y3), team.name, font=font_name, fill="white", anchor="ls"
            )
            draw.text(
                (x_p, y3), str(team.played), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_w, y3), str(team.won), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_d, y3), str(team.drawn), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_l, y3), str(team.lost), font=font_stats, fill="white", anchor="ms"
            )
            draw.text(
                (x_f, y3),
                f"{team.goals_for}-{team.points_for}",
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_a, y3),
                f"{team.goals_against}-{team.points_against}",
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_diff, y3),
                str(team.scoring_difference_x_wo),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            draw.text(
                (x_pts, y3),
                str(team.league_points),
                font=font_stats,
                fill="white",
                anchor="ms",
            )
            y1 = y2

        y1 += 20

    # Define date range
    date_range = [start_date]
    if days > 0:
        date_range.extend(start_date + timedelta(days=i) for i in range(1, days + 1))

    for fixtures_date in date_range:
        if (
            fixtures := session.query(Match)
            .filter_by(division_id=division_id, date=fixtures_date)
            .all()
        ):
            # Add date as subtitle - format day-name dd month yyyy
            date_str = fixtures_date.strftime("%A %d %B %Y")
            draw.text(
                (540, y1 + 35),
                date_str,
                font=font_subtitle,
                fill="lightgray",
                anchor="ms",
            )
            y1 += 50

            # Add fixtures

            for fixture in fixtures:
                y2 = y1 + 60
                y3 = y1 + 31

                match fixture.home_team.name:
                    case "Templeglantine/Knockaderry":
                        home_name = "Templeglan / Knockaderry"
                    case _:
                        home_name = fixture.home_team.name

                match fixture.away_team.name:
                    case "Templeglantine/Knockaderry":
                        away_name = "Templeglan / Knockaderry"
                    case _:
                        away_name = fixture.away_team.name

                draw.rectangle([x1, y1, x2, y2], fill=result_bg)

                # home logo here
                try:
                    logo = Image.open(
                        f"data/logos/logo30_{fixture.home_team.clubs[0].name}.png"
                    )
                    image.paste(logo, (x_home_logo, y1 + 5))
                finally:
                    pass

                match_time = fixture.time.strftime("%H:%M")

                draw.text(
                    (x_fix_time, y3),
                    match_time,
                    font=font_name,
                    fill="black",
                    anchor="ls",
                )
                draw.text(
                    (x_home_name, y3),
                    home_name,
                    font=font_name,
                    fill="black",
                    anchor="ls",
                )
                draw.text((x_v, y3), "v", font=font_name, fill="black", anchor="ms")
                draw.text(
                    (x_away_name, y3),
                    away_name,
                    fill="black",
                    anchor="rs",
                    font=font_name,
                )
                # away logo here
                try:
                    logo = Image.open(
                        f"data/logos/logo30_{fixture.away_team.clubs[0].name}.png"
                    )
                    image.paste(logo, (x_away_logo, y1 + 5))
                finally:
                    pass

                if fixture.referee:
                    match_info = f"Venue: {fixture.venue.name} - Referee: {fixture.referee.name} ({fixture.referee.club.name})"
                else:
                    match_info = f"{fixture.venue.name}"
                draw.text(
                    (x_v, y3 + 22),
                    match_info,
                    font=font_info,
                    fill="black",
                    anchor="ms",
                )

                y1 = y2 + 10

    image.save(
        f"outputs/fixtures_{division.name}_{start_date.strftime('%A %d %B %Y')}.png"
    )


@with_session
def update_ref_club(
    session,
    referee_id,
    club_id,
):
    if ref := session.query(Referee).filter_by(id=referee_id).first():
        ref.club_id = club_id


@with_session
def add_match_result(
    session,
    match_id,
    home_goals=None,
    home_points=None,
    away_goals=None,
    away_points=None,
    walkover=False,
    winner_id=None,
):
    add_result(
        session,
        match_id,
        home_goals=home_goals,
        home_points=home_points,
        away_goals=away_goals,
        away_points=away_points,
        walkover=walkover,
        winner_id=winner_id,
    )


@with_session
def update_all_tables(session):
    """Updates all league tables."""
    groups = session.query(Group).all()
    for group in groups:
        update_league_ranks(session, group.id)


@with_session
def update_division_tables(
    session,
    division_id,
):
    groups = session.query(Group).filter_by(division_id=division_id).all()
    for group in groups:
        update_league_ranks(session, group.id)


@with_session
def update_stats(
    session,
    team_id,
    P,
    W,
    D,
    L,
):
    if team := session.query(Team).filter_by(id=team_id).first():
        team.played = P
        team.won = W
        team.drawn = D
        team.lost = L
        update_league_ranks(session, team.group_id)


@with_session
def withdraw_team(session, team_id):
    team = session.query(Team).filter_by(id=team_id).first()
    for match in team.home_matches:
        session.delete(match)
    for match in team.away_matches:
        session.delete(match)
    team.fielded_all = False
    team.played = 0
    team.won = 0
    team.drawn = 0
    team.lost = 0
    team.goals_for = 0
    team.points_for = 0
    team.goals_against = 0
    team.points_against = 0
    team.goals_for_x_wo = 0
    team.points_for_x_wo = 0
    team.goals_against_x_wo = 0
    team.points_against_x_wo = 0
    update_league_ranks(session, team.group_id)


name = "County Competitions"
__version__ = "0.1.0"
__author__ = "Breandán Anraoi MacGabhann"
