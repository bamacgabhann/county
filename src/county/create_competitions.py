from .create_schema import (  # player_competition_association,; PlayerParticipation,
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


def add_club(session, club_id, name, ainm=None):
    club = Club(id=club_id, name=name, ainm=ainm)
    session.add(club)
    session.commit()


def add_referee(session, referee_id, name, club_id):
    referee = Referee(id=referee_id, name=name, club_id=club_id)
    session.add(referee)
    session.commit()


def add_venue(session, venue_id, name, club_id, address=None):
    venue = Venue(id=venue_id, name=name, club_id=club_id, address=address)
    session.add(venue)
    session.commit()


def add_player(session, player_id, name, ainm, club_id):
    player = Player(id=player_id, name=name, ainm=ainm, club_id=club_id)
    session.add(player)
    session.commit()


def add_competition(session, competition_id, name):
    competition = Competition(id=competition_id, name=name)
    session.add(competition)
    session.commit()


def add_division(session, division_id, name, competition_id):
    division = Division(id=division_id, name=name, competition_id=competition_id)
    session.add(division)
    session.commit()


def add_group(session, group_id, name, competition_id, division_id):
    group = Group(
        id=group_id, name=name, competition_id=competition_id, division_id=division_id
    )
    session.add(group)
    session.commit()


def add_team(
    session,
    team_id,
    name,
    competition_id,
    division_id,
    group_id,
    club_id1,
    club_id2=None,
):
    team = Team(
        id=team_id,
        name=name,
        competition_id=competition_id,
        division_id=division_id,
        group_id=group_id,
    )
    session.add(team)
    association = team_club_association.insert().values(
        team_id=team_id, club_id=club_id1
    )
    session.execute(association)
    if club_id2:
        association = team_club_association.insert().values(
            team_id=team_id, club_id=club_id2
        )
        session.execute(association)

    session.commit()


def add_match(
    session,
    match_id,
    home_team_id,
    away_team_id,
    venue_id,
    competition_id,
    division_id,
    stage,
    group_round,
    match_no,
    group_id=None,
    date=None,
    time=None,
    referee_id=None,
):
    match = Match(
        id=match_id,
        home_team_id=home_team_id,
        away_team_id=away_team_id,
        venue_id=venue_id,
        competition_id=competition_id,
        division_id=division_id,
        stage=stage,
        round=group_round,
        match_no=match_no,
        group_id=group_id,
        date=date,
        time=time,
        referee_id=referee_id,
    )
    session.add(match)
    session.commit()


def add_player_participation(session, match_id, player_id, team_id, started=False):
    participation = PlayerParticipation(
        match_id=match_id,
        player_id=player_id,
        team_id=team_id,
        started=started,
    )
    session.add(participation)
    session.commit()


def add_team_club_association(session, team_id, club_id):
    association = team_club_association.insert().values(
        team_id=team_id, club_id=club_id
    )
    session.execute(association)
    session.commit()


def add_player_team_association(session, player_id, team_id):
    association = player_team_association.insert().values(
        player_id=player_id, team_id=team_id
    )
    session.execute(association)
    session.commit()
