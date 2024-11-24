import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup



def load_csv_likabrow(path):
    # Behave like a browser to download file to load species ID and both Latin and German names

    url = path

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        species_data = StringIO(response.text)
        species_df = pd.read_csv(species_data)
        return species_df
    else:
        print(f"Failed to retrieve data: {response.status_code}")

# use BeautifulSoup to get answer from wikipedia URL 
def load_wikidatatodf(path): 
    url = path
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find the bird data table and get rows to lists
    table = soup.find({'class': 'div-col'})
    rows = table.find_all('tr')

    # lists
    english_names = []
    german_names = []
    latin_names = []

    # go through rows for extraction and adding to list
    for row in rows[1:]:  # except first one
        columns = row.find_all('td')
        if len(columns) >= 3:
            english_name = columns[0].text.strip()
            german_name = columns[1].text.strip()
            latin_name = columns[2].text.strip()
            
            english_names.append(english_name)
            german_names.append(german_name)
            latin_names.append(latin_name)

    bird_names_df = pd.DataFrame({
        'English Name': english_names,
        'German Name': german_names,
        'Latin Name': latin_names
    })

# Speichern als CSV
#bird_names_df.to_csv('bird_names.csv', index=False)

# Ausgabe der ersten paar Zeilen zur Überprüfung
#print(bird_names_df.head())
