import argparse
import json
from datetime import date
from datetime import datetime
from urllib.request import urlopen

URL_LATEST_DATA = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-json/dpc-covid19-ita-province-latest.json"
URL_ALL_DATA = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-json/dpc-covid19-ita-province.json"
DATE_BEGINNING_DATA = "2020-02-24"

date_to_check = str(date.today())
date_format = "%Y-%m-%d"

parser = argparse.ArgumentParser(description='Covid data digger')
parser.add_argument(
    '--date',
    type = str,
    help = "Date you want to get the number of cases from, formatted AAAA-MM-DD"
)

args = parser.parse_args()

if (args.date):
    try:
        date_to_check = str(datetime.strptime(args.date, date_format))[:10]
        if (date_to_check < DATE_BEGINNING_DATA):
            date_to_check = str(date.today())    
            print("There is no data available before February 24th 2020, defaulting to today")
    except ValueError:
        date_to_check = str(date.today())
        print("Date format not valid, defaulting to today")
else:
    print("No date specified, defaulting to today")

print("Checking statistics for " + date_to_check)
regions = {}

def getData(url = URL_ALL_DATA):
    """
    Gets the data from a specified url
    defaulting to all the data available
    """
    response = urlopen(url)
    dataset = json.loads(response.read())
    return dataset


def processDataIntoRegions(dataset = getData(), day = str(date.today())):
    """
    Returns a dictionary containing 'region': 'cases' pairs
    Accepts a dataset, downloads it if not available
    Accepts a date to check, defaults to today
    """
    for values in dataset:
        if values['data'][:10] == day:
            if values['denominazione_regione'] == "P.A. Bolzano":
                values['denominazione_regione'] = "Trentino - Alto Adige"
            if values['denominazione_regione'] == "P.A. Trento":
                values['denominazione_regione'] = "Trentino - Alto Adige"
            if values['denominazione_regione'] not in regions.keys():
                regions[values['denominazione_regione']] = values['totale_casi']
            else:
                regions[values['denominazione_regione']] += values['totale_casi']
    return regions

def sortRegions(regions):
    """
    Sorts the regions by number of cases first,
    alphabetically if there's regions with the same values
    """
    # We can use "reverse = True" using 'totale_casi' as key
    # because we want them in descending order,
    # but we wouldn't be able to alphabetically sort the regions
    # as it would apply the reversed order to them as well
    #
    # By using the negative value of 'totale_casi' we can use
    # the regions' names as a secondary key
    if regions:
        regions = dict(
            sorted(
                regions.items(),
                key = lambda item: (-item[1], item[0]),
            )
        )
    return regions

def printValues(dataset):
    """
    Prints the values in a readable format
    """
    for region, cases in dataset.items():
        print(region + ": " + str(cases))


# Before getting to the negative value solution above,
# I was sorting by name first, then I was doing a second pass
# using the values as a key

# if regions:
#   regions = dict(
#       sorted(
#           regions.items(),
#           key=lambda item: (item[0]),
#       )   
#   )
# if regions:
#   regions = dict(
#       sorted(
#           regions.items(),
#           key=lambda item: (item[1]),
#           reverse = True
#       )   
#   )
    

regions = processDataIntoRegions(getData(), date_to_check)
if (len(regions.items())) > 0:
    regions = sortRegions(regions)
    printValues(regions)
else:
    print("No data available.")