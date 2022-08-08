import argparse
import json
import xlsxwriter
import xlwt
from datetime import date
from datetime import datetime
from urllib.request import urlopen
from urllib.error import URLError

URL_LATEST_DATA = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-json/dpc-covid19-ita-province-latest.json"
URL_ALL_DATA = "https://github.com/pcm-dpc/COVID-19/raw/master/dati-json/dpc-covid19-ita-province.json"
DATE_BEGINNING_DATA = "2020-02-24"
DATE_FORMAT = "%Y-%m-%d"

regions = {}

def dateChecker(day):
    """
    Checks a string to see if the date format is correct,
    if the day is valid and returns it if it's correct,
    returns 'today' if not
    """
    try:
        date_to_check = str(datetime.strptime(day, DATE_FORMAT))[:10]
        if (date_to_check < DATE_BEGINNING_DATA):
            print("There is no data available before February 24th 2020, defaulting to today")
            return(str(date.today()))
        else:
            return(date_to_check)
    except ValueError:
        print("Date format not valid, defaulting to today.")
        return(str(date.today()))

def getData(url = URL_ALL_DATA):
    """
    Gets the data from a specified url defaulting
    to the json containing all the data available on github
    """
    try:
        response = urlopen(url)
        dataset = json.loads(response.read())
    except URLError:
        print("Error: data on github seems to be unreachable at the moment.")
        dataset = {}
    return dataset


def processDataIntoRegions(dataset = getData(), day = str(date.today())):
    """
    Returns a dictionary containing 'region': 'cases' pairs
    Accepts a dataset, downloads it if not available
    Accepts a date to check, defaults to today
    """
    print("Processing statistics for %s" % day)
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
    then alphabetically if there's regions with the same values
    """

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

def writeToXlsx(dataset, day):
    """
    Creates an xlsx file for the selected day
    """
    workbook = xlsxwriter.Workbook("Covid_data_" + day + ".xlsx")
    worksheet = workbook.add_worksheet(day)

    row = 0
    col = 0

    worksheet.write(row, col, "Region")
    worksheet.write(row, col + 1, "Cases")
    row += 1

    for region, cases in dataset.items():
        worksheet.write(row, col, region)
        worksheet.write(row, col + 1, cases)
        row += 1

    workbook.close()

def writeToXls(dataset, day):
    """
    Creates an xls file for the selected day
    """
    workbook = xlwt.Workbook(encoding = "utf-8")
    worksheet = workbook.add_sheet(day)

    row = 0
    col = 0

    worksheet.write(row, col, "Region")
    worksheet.write(row, col + 1, "Cases")
    row += 1

    for region, cases in dataset.items():
        worksheet.write(row, col, region)
        worksheet.write(row, col + 1, cases)
        row += 1

    workbook.save("Covid_data_" + day + ".xls")

def main(args = None, day = str(date.today()), return_json = False):
    
    if (args):
        if (args.date):
            day = dateChecker(args.date)
    else:
        day = dateChecker(day)

    regions = processDataIntoRegions(day = day)
    
    if (len(regions.items())) > 0:
        regions = sortRegions(regions)
        if not (return_json):
            printValues(regions)
        if (args):
            if (args.xlsx):
                writeToXlsx(regions, day)
            if (args.xls):
                writeToXls(regions, day)
        if (return_json):
            jsonfile = json.dumps(regions)
            return jsonfile
    else:
        print("No data available for the day selected.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Covid data digger')
    parser.add_argument(
        '--date',
        type = str,
        help = "Date you want to get the number of cases from, formatted AAAA-MM-DD"
    )
    parser.add_argument(
        '--xlsx',
        action='store_true',
        help = "Write the results in an .xlsx file"
    )
    parser.add_argument(
        '--xls',
        action='store_true',
        help = "Write the results in an .xls file"
    )
    args = parser.parse_args()

    main(args)