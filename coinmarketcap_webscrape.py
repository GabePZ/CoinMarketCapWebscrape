from bs4 import BeautifulSoup
import requests
from pandas import DataFrame, read_html

def is_historical_link(link):
    split_link = link.split('/')
    return "historical" in link and split_link[1] == "historical" and split_link[2] != ""

def get_historical_links(soup):
    links = []
    for link in soup.findAll('a'):
        links.append(link.get("href"))

    return [link for link in filter(None, links) if is_historical_link(link)]

def parse_date(soup):
    date = soup.find_all("div",{'class': "col-xs-12 text-center header header-1x"})[0].text

    #clean up newlines and "Historical Snapshot" Text
    date = date.replace("Historical Snapshot - ", "")
    date = date.replace("\n", "")

    return date

def parse_tables(soup):

    table = soup.find('table', id="currencies-all")

    df = read_html(table.prettify())[0]

    #Drop index and website functions columns
    df = df.drop(["#","Unnamed: 10"], axis=1)

    return df

if __name__ == "__main__":
    CMC_URL = "https://coinmarketcap.com/"
    CSV_PATH = "/CoinMarketCapData.csv"

    response = requests.get(CMC_URL + "historical/")
    soup = BeautifulSoup(response.content, "lxml")

    df = DataFrame()

    for partial_historical_link in get_historical_links(soup):
        historical_link = CMC_URL + partial_historical_link

        try:
            response = requests.get(historical_link)
            soup = BeautifulSoup(response.content, "lxml")

            new_df = parse_tables(soup)
            date = parse_date(soup)

            new_df['date'] = date
            df = df.append(new_df)

            print("Downloaded: " + date)
        except:
            print("ERROR: Unable to parse " + historical_link)

        df.to_csv(CSV_PATH, index = False)
