import pandas as pd

from county import add_new_results, initialise

db_url = "sqlite:///data/LimerickCamogie2025.db"

new_results = pd.read_csv("data/new_results.csv", encoding="latin-1", engine="pyarrow")

Session = initialise(db_url)

session = Session()  # Create a session object

add_new_results(new_results=new_results)
