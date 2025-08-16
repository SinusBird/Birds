import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup
import traceback
import requests
import re
from fdpdataload import get_ftp_data

def get_first_value(df):
    columns = list(df.columns)
    first_row = df.iloc[0].tolist()
    for col, val in zip(columns, first_row):
        print(f"{col}: {val}")

# Behave like a browser to download file to load species ID and both Latin and German names
def load_csv_likabrow(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response. raise_for_status()
    except requests.exceptions.HTTPError as err: #is not working
        print("Issue with euring website: ", err)

    # Check if the request was successful
    if response.status_code == 200:
        species_data = StringIO(response.text)
        species_df = pd.read_csv(species_data)
        return species_df
    else:
        print(f'Failed to retrieve data: {response.status_code}')

# use BeautifulSoup to bird name data from website (german, english, latin names)
def load_birddatatodf(url, debug=False):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
       # if debug:
      #      'Websites html structure:'
       #     print(soup.prettify())

        # find the bird data columns and get rows to lists then to data frame
        rows = soup.find_all('tr')

        data = []
        for row in rows[3:]:
            if len(row) >= 5:
                fields = row.find_all("td")
                ger = fields[2].get_text()
                eng = fields[3].get_text()
                lat = fields[4].get_text()
                data.append([ger, eng, lat])
        columns = ["Deutscher Name", "Englischer Name", "Lateinischer Name"]
        d = pd.DataFrame(data, columns=columns)
        if debug:
            print('Website data',d.head())
        return pd.DataFrame(data, columns=columns)


    # handle load issues
    except Exception as e:
        traceback.print_exc()
        print(f'Issue with data load from {url}: {e}')
        return None

def laod_ger_birds(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        ol_elements = soup.find_all("ol", {"start": "0"})
        li_elements = ol_elements[0].find_all("li")
        data = []
        for ol in li_elements:
            text = ol.get_text().split(",")
            ger = text[0]
            eng = text[1]
            lat = text[2]
            data.append([ger, eng, lat])
        columns = ["Deutscher Name", "Englischer Name", "Lateinischer Name"]
        df = pd.DataFrame(data, columns=columns)
        debug: (
            print(df))
        return df

    except Exception as e:
        traceback.print_exc()
        print(f'Issue with data load from {url}: {e}')
        return None

bla = laod_ger_birds('https://www.club300.de/ranking/birdlist_de.php')


def get_latest_euring_species_code_url():
    url = 'https://euring.org/data-and-codes/euring-codes'  # Anpassen, falls nötig
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # Begrenze die Suche auf den "Current Codes"-Block
    current_codes_block = soup.select_one('#block-views-current-codes-block')
    if not current_codes_block:
        return None

    # Titel-Suchmuster für Species Codes
    pattern = re.compile(r'^EURING Species Codes.*', re.IGNORECASE)

    for row in current_codes_block.select('.views-row'):
        title = row.select_one('.views-field-title .field-content')
        if title and pattern.match(title.text.strip()):
            link_tag = row.select_one('a[href$=".csv"]')
            if link_tag:
                href = link_tag['href']
                return f'https://euring.org{href}' if href.startswith('/') else href

    return None  # Falls kein Treffer gefunden wurde

def get_bird_code ():
    euring_species_url = get_latest_euring_species_code_url()
    df_birdid = load_csv_likabrow(euring_species_url)

    df_birdid.name = "birdid df"
    print(df_birdid.name)
    get_first_value(df_birdid)

    return df_birdid

def get_ringing_data ():
    fact_dfs, dim_dfs = get_ftp_data()
    df_ringing = fact_dfs["df_ringing"]

    df_ringing.name = "ringing df"
    print(df_ringing.name)
    get_first_value(df_ringing)

    return df_ringing

def get_bird_translations():
    df_birdnames = load_birddatatodf('https://www.club300.de/publications/wp-bird-list.php', debug=False)

    if df_birdnames is not None:
        print("Bird names loaded")
        #print(df_birdnames.head())  # Zeige die ersten Zeilen des DataFrames
    else:
        print("No bird names available")#

    return df_birdnames

def prep_birddata():

    # Load further bird data to display names
    df_birdid = get_bird_code()

    # Load data to analyze
    df = get_ringing_data()
    # Merge species ID with the original dataframe to add species names
    # TBD

    # Ensure DateTimeID is in the correct datetime format, and remove rows with invalid dates
    df['Fangtag'] = pd.to_datetime(df['Fangtag'], errors='coerce')

    # Drop rows where DateTimeID could not be parsed
    df = df.dropna(subset=['Fangtag'])

    df_merg = pd.merge(df, df_birdid, how='left', left_on=['strSpecies'], right_on=['EURING_Code'])
    df_merg.name = "merged df"
    print(df_merg.name)
    get_first_value(df_merg)

    # Load name translations --- from club500 URL, ask about usage before data publication!!!!
    df_birdnames = get_bird_translations()
    df_birdnames.name = "bridname df"
    print(df_birdnames.name)
    get_first_value(df_birdnames)

    #trim join columns
    df_merg['Current_Name'] = df_merg['Current_Name'].str.strip()
    df_birdnames['Lateinischer Name'] = df_birdnames['Lateinischer Name'].str.strip()

    df_with_names = pd.merge(df_merg, df_birdnames, how='left', left_on=['Current_Name'], right_on=['Lateinischer Name'])
    df_with_names = df_with_names.rename(columns={"Deutscher Name": "NameGER", "Lateinischer Name": "NameLAT", "Englischer Name": "NameENG"})
    df_with_names['Name'] = (
        df_with_names['NameGER'].combine_first(df_with_names['NameENG'])
        .combine_first(df_with_names['NameLAT']).combine_first(df_with_names['strSpecies']))

    values = {"NameLAT": "Latin Name missing"}
    df_with_names = df_with_names.fillna(value=values)

    df_with_names.name = "merged with names df"
    print(df_with_names.name)
    get_first_value(df_with_names)
    df = df_with_names

    return df

