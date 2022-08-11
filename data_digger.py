import sys
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


def date_checker(day):
    """
    Checks a string to see if the date format is correct and the day is valid
    returns it if it's correct, returns 'today' if not
    """
    try:
        date_to_check = str(datetime.strptime(day, DATE_FORMAT))[:10]
        if date_to_check < DATE_BEGINNING_DATA:
            print("There is no data available before February 24th 2020, defaulting to today.")
            return str(date.today())        elif date_to_check > str(date.today()):
            print("Date specified has yet to come! Defaulting to today.")
            return str(date.today())
        else:
            return date_to_check
    except ValueError:
        print("Error: Date format not valid, defaulting to today. Format expected: yyyy-mm-dd.")
        return str(date.today())
    except TypeError:
        print("Error: there has been a problem during the date check. Defaulting to today.")
        return str(date.today())


def get_data(url=URL_ALL_DATA):
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
    except json.decoder.JSONDecodeError:
        print("Error: Data cannot be decoded as JSON. Exiting.")
        exit()
    return dataset


def process_data_into_regions(dataset=None, day=str(date.today())):
    """
    Returns a dictionary containing 'region': 'cases' pairs
    Accepts a dataset, downloads it if not available
    Accepts a date to check, defaults to today
    """
    # If the data requested is for today we can download just the latest data
    if not dataset:
        if day == str(date.today()):
            dataset = get_data(URL_LATEST_DATA)
        else:
            dataset = get_data()

    print("Processing statistics for %s" % day)
    regions = {}
    for values in dataset:
        if values['data'][:10] == day:
            if values['denominazione_regione'] in ['P.A. Bolzano', 'P.A. Trento']:
                values['denominazione_regione'] = "Trentino - Alto Adige"

            if values['denominazione_regione'] not in regions.keys():
                regions[values['denominazione_regione']] = values['totale_casi']
            else:
                regions[values['denominazione_regione']] += values['totale_casi']

    return regions


def sort_regions(regions):
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


def print_values(dataset):
    """
    Prints the values in a readable format
    """
    for region, cases in dataset.items():
        print(region + ": " + str(cases))

def write_to_xls_xlsx(dataset, day, filetype):
    filename = "Covid_data_" + day

    if filetype == "xls":
        workbook = xlwt.Workbook(encoding = "utf-8")
        worksheet = workbook.add_sheet(day)
    else:
        workbook = xlsxwriter.Workbook(filename + ".xlsx")
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

    if filetype == "xls":
        workbook.save(filename + ".xls")
    else:
        workbook.close()


def parse_arguments(args):
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
    parser.add_argument(
        '--file',
        type = str,
        help = "Read data from file instead of downloading it"
    )
    args = parser.parse_args(args)
    return args


def file_parser(fileToRead):
    try:
        fileToOpen = open(fileToRead)
        data = json.load(fileToOpen)
        fileToOpen.close()
    except FileNotFoundError:
        print("File not found, downloading data from Github")
        data = {}
    except json.decoder.JSONDecodeError:
        print("Error: Data cannot be decoded as JSON, downloading data from Github")
        data = {}

    return data


def main(args=None, return_json=False):
    args = parse_arguments(args)

    if args.date:
        day = date_checker(args.date)
    else:
        day = str(date.today())

    if args.file:
        data_from_file = file_parser(args.file)
        regions = process_data_into_regions(dataset = data_from_file, day = day)
    else:
        regions = process_data_into_regions(day = day)

    if regions.items():
        regions = sort_regions(regions)
        if not return_json:
            print_values(regions)
        if args.xlsx:
            write_to_xls_xlsx(regions, day, "xlsx")
        if args.xls:
            write_to_xls_xlsx(regions, day, "xls")
    else:
        print("No data available for the day selected.")
        if day == str(date.today()):
            print("Data for today may not be available yet, try again later.")

    if return_json:
        jsonfile = json.dumps(regions)
        return jsonfile

if __name__ == '__main__':
    main(sys.argv[1:])