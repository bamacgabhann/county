import logging

from create_schema import Match, PlayerParticipation, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


def update_score(match_id, home_goals, home_points, away_goals, away_points):
    with Session() as session:
        if match := session.query(Match).filter_by(id=match_id).first():
            match.home_goals = home_goals
            match.home_points = home_points
            match.away_goals = away_goals
            match.away_points = away_points
            session.commit()
        else:
            logging.warning("update_score: No match found for id %s", match_id)


def update_player_participation(match_id, player_id, team_id, started):
    with Session() as session:
        if (
            player_participation := session.query(PlayerParticipation)
            .filter_by(match_id=match_id, player_id=player_id, team_id=team_id)
            .first()
        ):
            player_participation.started = started
            session.commit()
        else:
            logging.warning(
                "update_player_participation: No player participation found for match_id %s, player_id %s, team_id %s",
                match_id,
                player_id,
                team_id,
            )
