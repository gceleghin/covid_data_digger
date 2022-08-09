# COVID data digger

A script that prints in a readable manner the number of COVID cases in every italian region in any given day starting from February 24th 2020, ordering them from the most cases to the least.
Data is fetched directly from the Italian Civil Protection department github page, updated every day, unless the user provides a JSON file of his own via the --file argument.

# Installation
Just clone the repo and install the additional modules, no setup required.

## Modules
The script uses XlsxWriter and xlwt to write Xlsx and xls files respectively, so just type:  
`pip install XlsxWriter xlwt`  
to install them.

## Run the script
The default mode of operation has the script downloading the latest JSON from github and return the results from today.
`python3 data_digger.py`

It also accepts some arguments:  
`--date DATE` to show results from the DATE specified. It expects a 'yyyy-mm-dd' format, eg: 2022-01-01  
`--file FILEPATH` reads data from a file instead of downloading the latest data from Github  
`--xlsx` writes a xlsx file named 'Covid_data_DATE.xlsx' containing the list of regions and respective cases  
`--xls` writes a xls file named 'Covid_data_DATE.xls' containing the list of regions and respective cases  

# Webserver
There is also a webserver that when run replies to GET requests with a JSON containing the information required.

## Run the webserver
If you clone the repo, run:  
`python3 webserver/webserver.py`

Once the webserver is up and running it is reachable by connecting to http://coviddatadigger:8080.
A simple GET request will return a JSON containing the data for today, but you can also pass a 'date' parameter to get data for another day, eg:
`http://coviddatadigger:8080/?date=2022-01-01`