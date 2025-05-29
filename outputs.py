from county import generate_all_pages, initialise, update_all_tables

db_url = "sqlite:///data/LimerickCamogie2025.db"

Session = initialise(db_url)

session = Session()  # Create a session object

# new_results = pd.read_csv("data/new_results.csv", encoding="latin-1", engine="pyarrow")
# add_new_results(new_results=new_results)

# c = {'club_id': [39], 'name': ['Newport (Tipperary)'], 'ainm':['An Port Nua (Tiobraid Árann)']}
# clubs_df = pd.DataFrame(c)
# add_clubs(clubs_df)

# r = {'referee_id': [31], 'name': ['Jim Lees'], 'club_id': [39]}
# referees_df = pd.DataFrame(r)
# add_referees(referees_df)

# update_match_referee(196, 15)

# update_ref_club(8, 18)


# withdraw_team(11)

# update_match_datetime(236, datetime.datetime.strptime('02/06/2025 19:15', "%d/%m/%Y %H:%M"))


# update_match_venue(270, 21)


# add_match_result(425, 2, 7, 7, 7)
# add_match_result(208, walkover=True, winner_id=25)


update_all_tables()

generate_all_pages()

# generate_div_page(9)
# generate_div_page(10)


# update_all_tables()
# for division_id in range(7, 22):
#    instagram_division_results(division_id, datetime.date(2025, 5, 10), days=7)
#    instagram_division_fixtures(division_id, datetime.date(2025, 5, 24), days=7)

# instagram_division_results(9, datetime.date(2025, 5, 10), days=11)

# instagram_division_fixtures(10, datetime.date(2025, 5, 27), days=7)
# instagram_division_results(9, datetime.date(2025, 5, 29))
# instagram_division_results(10, datetime.date(2025, 5, 29))
# instagram_division_fixtures(21, datetime.date(2025, 5, 28))
