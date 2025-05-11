import logging
from collections import Counter

from sqlalchemy import text

from .create_schema import Match, PlayerParticipation, Team


def update_date(session, match_id, date):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.date = date
    else:
        logging.warning("update_date: No match found for id %s", match_id)


def update_time(
    session,
    match_id,
    time,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.time = time
    else:
        logging.warning("update_time: No match found for id %s", match_id)


def update_date_time(
    session,
    match_id,
    date,
    time,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.date = date
        match.time = time
    else:
        logging.warning("update_date_time: No match found for id %s", match_id)


def update_venue(
    session,
    match_id,
    venue_id,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.venue_id = venue_id
    else:
        logging.warning("update_venue: No match found for id %s", match_id)


def update_referee(
    session,
    match_id,
    referee_id,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.referee_id = referee_id
    else:
        logging.warning("update_referee: No match found for id %s", match_id)


def update_knockout_teams(session, division_id):
    """Updates home and away teams for knockout matches in a division."""

    matches = (
        session.query(Match).filter_by(division_id=division_id, stage="knockout").all()
    )

    for match in matches:
        if match.home_team_criteria:
            try:
                # Execute the criteria from the Criteria table
                criteria = match.home_team_criteria[0].sql_query  # Access criteria
                result = session.execute(
                    text(criteria),
                    {"division_id": division_id, "match_id": match.id},
                ).scalar()
                match.home_team_id = result
            except Exception as e:
                logging.error(f"Error updating home team for match {match.id}: {e}")

        if match.away_team_criteria:
            try:
                criteria = match.away_team_criteria[0].sql_query
                result = session.execute(
                    text(criteria),
                    {"division_id": division_id, "match_id": match.id},
                ).scalar()
                match.away_team_id = result
            except Exception as e:
                logging.error(f"Error updating away team for match {match.id}: {e}")


def update_walkover(
    session,
    match_id,
    winner_id,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.walkover = True
        match.winner_id = winner_id
    else:
        logging.warning("update_walkover: No match found for id %s", match_id)


def get_team_stats(
    session,
    match_id,
    team_id,
):
    if not (match := session.query(Match).filter_by(id=match_id).first()):
        logging.warning("get_team_stats: No match found for id %s", match_id)
    else:
        if match.stage == "group":
            return (
                session.query(Team)
                .filter_by(id=team_id, group_id=match.group_id)
                .first()
            )
        logging.warning("get_team_stats: Match is not in group stage")
    return None


def determine_winner(
    home_goals,
    home_points,
    away_goals,
    away_points,
):
    home_score = (home_goals * 3) + home_points
    away_score = (away_goals * 3) + away_points

    if home_score > away_score:
        return "home"
    elif home_score < away_score:
        return "away"
    else:
        return "draw"


def update_group_table_stats(
    session,
    match_id,
    home_goals=None,
    home_points=None,
    away_goals=None,
    away_points=None,
):
    if not (match := session.query(Match).filter_by(id=match_id).first()):
        return
    if match.stage == "group":
        home_team_stats = get_team_stats(session, match_id, match.home_team_id)
        away_team_stats = get_team_stats(session, match_id, match.away_team_id)

        home_team_stats.played += 1
        away_team_stats.played += 1

        if match.walkover:
            if match.winner_id == match.home_team_id:
                home_team_stats.won += 1
                away_team_stats.lost += 1
                away_team_stats.fielded_all = False
            else:
                home_team_stats.lost += 1
                away_team_stats.won += 1
                home_team_stats.fielded_all = False
        else:
            home_team_stats.goals_for += home_goals
            home_team_stats.points_for += home_points
            home_team_stats.goals_against += away_goals
            home_team_stats.points_against += away_points

            away_team_stats.goals_for += away_goals
            away_team_stats.points_for += away_points
            away_team_stats.goals_against += home_goals
            away_team_stats.points_against += home_points

            match_winner = determine_winner(
                home_goals,
                home_points,
                away_goals,
                away_points,
            )
            match match_winner:
                case "home":
                    home_team_stats.won += 1
                    away_team_stats.lost += 1
                    match.winner_id = match.home_team_id
                case "away":
                    home_team_stats.lost += 1
                    away_team_stats.won += 1
                    match.winner_id = match.away_team_id
                case "draw":
                    home_team_stats.drawn += 1
                    away_team_stats.drawn += 1


def update_score(
    session,
    match_id,
    home_goals=None,
    home_points=None,
    away_goals=None,
    away_points=None,
):
    if match := session.query(Match).filter_by(id=match_id).first():
        match.home_goals = home_goals
        match.home_points = home_points
        match.away_goals = away_goals
        match.away_points = away_points


def update_scores_x_wo(
    session,
    group_id,
):

    teams_in_group = session.query(Team).filter_by(group_id=group_id).all()
    teams_x_wo = (
        session.query(Team).filter_by(group_id=group_id, fielded_all=True).all()
    )
    for team in teams_in_group:
        team_and_x_wo_ids = [team.id] + [t.id for t in teams_x_wo]  # Combine IDs
        matches_x_wo = (
            session.query(Match)
            .filter_by(group_id=group_id, stage="group")
            .filter(
                (Match.home_team_id.in_(team_and_x_wo_ids))  # Use combined IDs
                | (Match.away_team_id.in_(team_and_x_wo_ids))  # Use combined IDs
            )
            .all()
        )
        team.goals_for_x_wo = 0
        team.points_for_x_wo = 0
        team.goals_against_x_wo = 0
        team.points_against_x_wo = 0

        for m in matches_x_wo:
            if m.home_team_id == team.id:
                team.goals_for_x_wo += m.home_goals or 0
                team.points_for_x_wo += m.home_points or 0
                team.goals_against_x_wo += m.away_goals or 0
                team.points_against_x_wo += m.away_points or 0
            elif m.away_team_id == team.id:
                team.goals_for_x_wo += m.away_goals or 0
                team.points_for_x_wo += m.away_points or 0
                team.goals_against_x_wo += m.home_goals or 0
                team.points_against_x_wo += m.home_points or 0


def update_league_ranks(
    session,
    group_id,
):
    # first try to rank on league points
    # if there are teams level on points, rank by fielded_all
    # if 2 teams are level and both fielded_all, winner of match between those teams ranks ahead
    # if they are still level, or 3+ teams level, rank by scoring_difference excluding matches involving walkover teams

    # Calculate the scoring difference excluding matches against teams with fielded_all=False

    teams = session.query(Team).filter_by(group_id=group_id).all()
    update_scores_x_wo(session, group_id)

    # Sort teams by league points in descending order
    sorted_teams = sorted(
        teams,
        key=lambda team: (
            team.league_points,
            team.fielded_all,
            team.scoring_difference_x_wo,
        ),
        reverse=True,
    )

    # Assign initial ranks
    for i, team in enumerate(sorted_teams):
        team.league_rank = i + 1

    # Count the occurrences of each points total
    points_counts = Counter(team.league_points for team in sorted_teams)

    # Check for ties and handle them
    for points, count in points_counts.items():
        if count == 2:
            tied_teams = [team for team in sorted_teams if team.league_points == points]
            tied_ranks = [team.league_rank for team in tied_teams]

            h2h = (
                session.query(Match)
                .filter_by(group_id=group_id, stage="group")
                .filter(
                    Match.home_team_id.in_(t.id for t in tied_teams)
                )  # Use combined IDs
                .filter(Match.away_team_id.in_(t.id for t in tied_teams))
                .first()  # Use combined IDs
            )
            if h2h is not None and h2h.winner_id:
                if h2h.winner_id == tied_teams[0].id:
                    # Team 1 wins the tie
                    tied_teams[0].league_rank = min(tied_ranks)
                    tied_teams[1].league_rank = max(tied_ranks)
                else:
                    # Team 2 wins the tie
                    tied_teams[0].league_rank = max(tied_ranks)
                    tied_teams[1].league_rank = min(tied_ranks)


def add_result(
    session,
    match_id,
    home_goals=None,
    home_points=None,
    away_goals=None,
    away_points=None,
    walkover=False,
    winner_id=None,
):
    if match := session.query(Match).filter_by(id=match_id).first():

        if walkover:
            update_walkover(session, match_id, winner_id)
        else:
            update_score(
                session,
                match_id,
                home_goals,
                home_points,
                away_goals,
                away_points,
            )

        update_group_table_stats(
            session,
            match_id,
            home_goals,
            home_points,
            away_goals,
            away_points,
        )
        update_league_ranks(session, match.group_id)
        update_knockout_teams(session, match.division_id)
        session.commit()
    else:
        logging.warning("update_score: No match found for id %s", match_id)


def update_player_participation(session, match_id, player_id, team_id, started):
    if (
        player_participation := session.query(PlayerParticipation)
        .filter_by(match_id=match_id, player_id=player_id, team_id=team_id)
        .first()
    ):
        player_participation.started = started
    else:
        logging.warning(
            "update_player_participation: No player participation found for match_id %s, player_id %s, team_id %s",
            match_id,
            player_id,
            team_id,
        )
