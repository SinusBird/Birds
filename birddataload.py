import pandas as pd
import requests
from io import StringIO
from bs4 import BeautifulSoup
import traceback


# Behave like a browser to download file to load species ID and both Latin and German names
def load_csv_likabrow(url):
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
            elif debug:
                print(row)
        columns = ["Deutscher Name", "Englischer Name", "Lateinischer Name"] 
        d = pd.DataFrame(data, columns=columns)
        print(d.head())
        return pd.DataFrame(data, columns=columns)


    # handle load issues
    except Exception as e:
        traceback.print_exc() 
        #print(f'Issue with data load from {url}: {e}')
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
        print(df)
        return df

    except Exception as e:
        traceback.print_exc() 
        #print(f'Issue with data load from {url}: {e}')
        return None    

bla = laod_ger_birds('https://www.club300.de/ranking/birdlist_de.php')

