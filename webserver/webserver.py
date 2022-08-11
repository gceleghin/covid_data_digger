from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from socket import gaierror
from datetime import date
import argparse
import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_path)
import data_digger


class handler (BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()

        date_passed = parse_qs(urlparse(self.path).query).get("date")

        if date_passed:
            json_file = data_digger.main(['--date', date_passed[0]], return_json = True)
        else:
            json_file = data_digger.main(['--date', str(date.today())], return_json = True)

        self.wfile.write(json_file.encode())


def parse_web_arguments(arguments):
    argument_parser = argparse.ArgumentParser(description="webserver that returns a JSON")
    argument_parser.add_argument(
        '--hostname',
        type = str,
        help = "hostname for the webserver"
    )
    argument_parser.add_argument(
        '--port',
        type = int,
        help = "port number for the webserver"
    )
    arguments = argument_parser.parse_args(arguments)
    return arguments


def main(arguments=None):
    arguments = parse_web_arguments(arguments)
    if arguments.hostname:
        hostname = arguments.hostname
    else:
        hostname = "coviddatadigger"
    if arguments.port:
        server_port = arguments.port
    else:
        server_port = 8080

    try:
        webserver = HTTPServer((hostname, server_port), handler)
    except gaierror as e:
        print("Error: cannot establish a connection")
        print(e)
        exit()

    print("Server up, reachable to http://%s:%s" % (hostname, server_port))
    webserver.serve_forever()


if __name__ == '__main__':
    main(sys.argv[1:])