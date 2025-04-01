from create_schema import (  # player_competition_association,; PlayerParticipation,
    Club,
    Competition,
    Division,
    Match,
    Player,
    Team,
    engine,
)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def add_club(name, location):
    club = Club(name=name, location=location)
    session.add(club)
    session.commit()


def add_player(name, ainm, age, grade, club_name):
    player = Player(name=name, ainm=ainm, age=age, grade=grade, club_name=club_name)
    session.add(player)
    session.commit()


def add_competition(name, grade):
    competition = Competition(name=name, grade=grade)
    session.add(competition)
    session.commit()


def add_division(name, competition_id):
    division = Division(name=name, competition_id=competition_id)
    session.add(division)
    session.commit()


def add_team(name, club_name, division_id):
    team = Team(name=name, club_name=club_name, division_id=division_id)
    session.add(team)
    session.commit()


def add_match(
    home_team_id, away_team_id, location, date, grade, competition_id, division_id
):
    match = Match(
        date=date,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        home_goals=None,
        home_points=None,
        away_goals=None,
        away_points=None,
        location=location,
        grade=grade,
        competition_id=competition_id,
        division_id=division_id,
    )
    session.add(match)
    session.commit()


# Example usage
# add_club("Club A", "POINT(12.9715987 77.594566)")
# add_competition("Competition A", "Under 16")
# add_division("Division A", 1)
# add_team("Team A", 1, 1)
# add_match(1, 2, "POINT(12.9715987 77.594566)", date(2025, 3, 14), "Under 16", 1, 1)
