import logging

from create_schema import LeagueTable, Match, PlayerParticipation, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


def update_score(
    match_id,
    home_goals=None,
    home_points=None,
    away_goals=None,
    away_points=None,
    walkover=False,
    walkover_winner_id=None,
):
    with Session() as session:
        if match := session.query(Match).filter_by(id=match_id).first():

            if walkover:
                match.walkover = True
                match.walkover_winner_id = walkover_winner_id
            else:
                match.home_goals = home_goals
                match.home_points = home_points
                match.away_goals = away_goals
                match.away_points = away_points

            if match.stage == "group":
                home_team_stats = (
                    session.query(LeagueTable)
                    .filter_by(team_id=match.home_team_id, group_id=match.group_id)
                    .first()
                )
                away_team_stats = (
                    session.query(LeagueTable)
                    .filter_by(team_id=match.away_team_id, group_id=match.group_id)
                    .first()
                )

                if not home_team_stats:
                    home_team_stats = LeagueTable(
                        team_id=match.home_team_id, group_id=match.group_id
                    )
                    session.add(home_team_stats)
                if not away_team_stats:
                    away_team_stats = LeagueTable(
                        team_id=match.away_team_id, group_id=match.group_id
                    )
                    session.add(away_team_stats)

                home_team_stats.played += 1
                away_team_stats.played += 1

                if match.walkover:

                    if match.walkover_winner_id == match.home_team_id:
                        home_team_stats.won += 1
                        away_team_stats.lost += 1
                    else:
                        home_team_stats.lost += 1
                        away_team_stats.won += 1
                else:
                    home_score = (match.home_goals * 3) + match.home_points
                    away_score = (match.away_goals * 3) + match.away_points

                    if home_score > away_score:
                        home_team_stats.won += 1
                        away_team_stats.lost += 1
                    elif home_score < away_score:
                        home_team_stats.lost += 1
                        away_team_stats.won += 1
                    else:
                        home_team_stats.drawn += 1
                        away_team_stats.drawn += 1

                    home_team_stats.goals_for += match.home_goals
                    home_team_stats.points_for += match.home_points
                    home_team_stats.scores_for += home_score
                    home_team_stats.goals_against += match.away_goals
                    home_team_stats.points_against += match.away_points
                    home_team_stats.scores_against += away_score

                    away_team_stats.goals_for += match.away_goals
                    away_team_stats.points_for += match.away_points
                    away_team_stats.scores_for += away_score
                    away_team_stats.goals_against += match.home_goals
                    away_team_stats.points_against += match.home_points
                    away_team_stats.scores_against += home_score

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


# Example usage
# with Session() as session:
#    match = session.get(Match, 1)  # Replace 1 with the actual match ID
#    if match:
#        for participation in match.home_players_started:
#            print(f"Home Player Started: {participation.player.name}")
#
#        for participation in match.away_players_substitute:
#            print(f"Away Player Substitute: {participation.player.name}")
#    else:
#        print("Match not found.")

# with Session() as session:
#    group_id = 1  # Replace with the actual group ID
#    standings = (
#        session.query(LeagueTable)
#        .filter_by(group_id=group_id)
#        .order_by(LeagueTable.league_position)
#        .all()
#    )
#    for entry in standings:
#        print(
#            f"{entry.team.name}: Played={entry.played}, Points={entry.league_points}, Position={entry.league_position}"
#        )
