from create_schema import (  # player_competition_association,; PlayerParticipation,
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
    engine,
    player_team_association,
    team_club_association,
)
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


def add_club(club_id, name, ainm=None, location=None):
    club = Club(id=club_id, name=name, ainm=ainm, location=location)
    with Session() as session:
        session.add(club)
        session.commit()


def add_referee(referee_id, name, club_id):
    referee = Referee(id=referee_id, name=name, club_id=club_id)
    with Session() as session:
        session.add(referee)
        session.commit()


def add_venue(venue_id, name, club_id, location):
    venue = Venue(id=venue_id, name=name, club_id=club_id, location=location)
    with Session() as session:
        session.add(venue)
        session.commit()


def add_player(player_id, name, ainm, club_id):
    player = Player(id=player_id, name=name, ainm=ainm, club_id=club_id)
    with Session() as session:
        session.add(player)
        session.commit()


def add_competition(competition_id, name):
    competition = Competition(id=competition_id, name=name)
    with Session() as session:
        session.add(competition)
        session.commit()


def add_division(division_id, name, competition_id):
    division = Division(id=division_id, name=name, competition_id=competition_id)
    with Session() as session:
        session.add(division)
        session.commit()


def add_group(group_id, name, competition_id, division_id):
    group = Group(
        id=group_id, name=name, competition_id=competition_id, division_id=division_id
    )
    with Session() as session:
        session.add(group)
        session.commit()


def add_team(team_id, name, competition_id, division_id, group_id, club_ids):
    team = Team(
        id=team_id,
        name=name,
        competition_id=competition_id,
        division_id=division_id,
        group_id=group_id,
    )
    with Session() as session:
        session.add(team)
        for club_id in club_ids:
            association = team_club_association.insert().values(
                team_id=team_id, club_id=club_id
            )
            session.execute(association)
        session.commit()


def add_match(
    match_id,
    home_team_id,
    away_team_id,
    venue_id,
    date,
    time,
    competition_id,
    division_id,
    group_id=None,
    stage="group",
    referee_id=None,
):
    match = Match(
        id=match_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        venue_id=venue_id,
        date=date,
        time=time,
        competition_id=competition_id,
        division_id=division_id,
        group_id=group_id,
        stage=stage,
        referee_id=referee_id,
    )
    with Session() as session:
        session.add(match)
        session.commit()


def add_player_participation(match_id, player_id, team_id, started=False):
    participation = PlayerParticipation(
        match_id=match_id,
        player_id=player_id,
        team_id=team_id,
        started=started,
    )
    with Session() as session:
        session.add(participation)
        session.commit()


def add_team_club_association(team_id, club_id):
    with Session() as session:
        association = team_club_association.insert().values(
            team_id=team_id, club_id=club_id
        )
        session.execute(association)
        session.commit()


def add_player_team_association(player_id, team_id):
    with Session() as session:
        association = player_team_association.insert().values(
            player_id=player_id, team_id=team_id
        )
        session.execute(association)
        session.commit()
