import requests
from bs4 import BeautifulSoup
from sys import maxsize as MAX_INT

import database as db
import sqlalchemy
from schemas import pokemon
from databasesync import pkTypes


def TextToInt(text):
    if text == '—':
        return 0
    if text == '∞':
        return 101
    else:
        return int(text)
    
def MoveCategoryHandling(cell):
    if cell.attrs.get('data-filter-value', 0) != 0:
        return cell.attrs.get('data-filter-value').capitalize()
    else:
        return "—"

# Replace 'your_url_here' with the URL of the webpage you want to scrape
url = 'https://pokemondb.net/pokedex/all'
pokedex = []

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the <table> element by its tag name
    table = soup.find('table')

    # Check if the table was found
    if table:
        # Find all the rows within the table
        rows = table.find_all('tr')

        # Loop through each row and perform specific scraping
        for row in rows:
            # Find all the <td> elements in the current row
            cells = row.find_all('td')

            # Check if the row contains data in the form of cells
            if cells:

                # Multi-type handling
                types = cells[2].text.split(" ")
                type1 = pkTypes[types[0]]
                type2 = pkTypes[types[1]]

                # Pokemon db isnstance
                pokedex.append(
                    {
                        "pokedex_number": int(cells[0].text),
                        "name": cells[1].text,
                        "type1": type1,
                        "type2": type2,
                        "hp": int(cells[4].text),
                        "attack": int(cells[5].text),
                        "defense": int(cells[6].text),
                        "special_attack": int(cells[7].text),
                        "special_defense": int(cells[8].text),
                        "speed": int(cells[9].text)
                    }
                )
                
                print(f"{cells[1].text} added to list.")

                print("------------")  # Separator between rows
    else:
        print("Table not found on the page.")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)

#------------------------------------------------------------#

# Insert the scraped data into the database
with db.engine.begin() as conn:
    conn.execute(
        sqlalchemy
        .insert(pokemon)
        .values(pokedex)
    )
