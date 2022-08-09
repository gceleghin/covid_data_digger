from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from socket import gaierror
import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(root_path)
import data_digger

HOSTNAME = "coviddatadigger"
SERVER_PORT = 8080

class handler (BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.end_headers()

        date = parse_qs(urlparse(self.path).query).get("date")
        if (date):
            json_file = data_digger.main(['--date',date[0]], return_json = True)
        else:
            json_file = data_digger.main(return_json = True)

        self.wfile.write(json_file.encode())


def main():
    try:
        webserver = HTTPServer((HOSTNAME, SERVER_PORT), handler)
    except gaierror:
        print("Error: cannot establish a connection")
        exit()
    print("Server up, reachable to http://%s:%s" % (HOSTNAME, SERVER_PORT))
    webserver.serve_forever()


if __name__ == '__main__':
    main()