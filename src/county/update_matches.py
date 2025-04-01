from create_schema import Match, Player, PlayerParticipation, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()


def update_score(match_id, home_goals, home_points, away_goals, away_points):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.home_goals = home_goals
        match.home_points = home_points
        match.away_goals = away_goals
        match.away_points = away_points
        session.commit()


def add_player_participation(match_id, player_id, team_id, is_substitute):
    participation = PlayerParticipation(
        match_id=match_id,
        player_id=player_id,
        team_id=team_id,
        is_substitute=is_substitute,
    )
    session.add(participation)
    session.commit()


def add_player(name, age, grade, club_id):
    player = Player(name=name, age=age, grade=grade, club_id=club_id)
    session.add(player)
    session.commit()


# Example usage
update_score(1, 3, 18, 2, 15)
add_player_participation(1, 1, 1, False)
add_player("Player A", 16, "Under 16", 1)
