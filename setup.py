import pandas as pd

from county import (
    add_clubs,
    add_competitions,
    add_divisions,
    add_groups,
    add_referees,
    add_teams,
    add_venues,
    initialise,
)

db_url = "sqlite:///data/LimerickCamogie2025.db"

clubs_df = pd.read_csv("data/clubs.csv", encoding="latin-1")
competitions_df = pd.read_csv("data/competitions.csv", encoding="latin-1")
divisions_df = pd.read_csv("data/divisions.csv", encoding="latin-1")
groups_df = pd.read_csv("data/groups.csv", encoding="latin-1")
referees_df = pd.read_csv("data/referees.csv", encoding="latin-1")
teams_df = pd.read_csv("data/teams.csv", encoding="latin-1")
venues_df = pd.read_csv("data/venues.csv", encoding="latin-1")

Session = initialise(db_url)

session = Session()  # Create a session object

add_clubs(session=session, clubs_df=clubs_df)
add_referees(session=session, referees_df=referees_df)
add_venues(session=session, venues_df=venues_df)
add_competitions(session=session, competitions_df=competitions_df)
add_divisions(session=session, divisions_df=divisions_df)
add_groups(session=session, groups_df=groups_df)
add_teams(session=session, teams_df=teams_df)
