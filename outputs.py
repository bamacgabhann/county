from county import Division, generate_league_table_html, initialise

db_url = "sqlite:///data/LimerickCamogie2025.db"

Session = initialise(db_url)

session = Session()  # Create a session object

divisions = session.query(Division).all()

for division in divisions:
    generate_league_table_html(session, division.id)
