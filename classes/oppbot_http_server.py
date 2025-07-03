import http.server
import itertools
import threading
import logging

class OppBotHttpServer(threading.Thread):
    """A simple HTTP server for OppBot that serves HTML content.
    This server responds to GET requests with a welcome message and handles 
    POST requests with a not implemented error."""

    def __init__(self, host='0.0.0.0', port=8888):
        """Initialize the server with the specified host and port."""
        threading.Thread.__init__(self)
        self.server_address = (host, port)
        self.RequestHandler = QuietRequestHandler
        self.httpd = http.server.HTTPServer(self.server_address, self.RequestHandler)

    def run(self):
        """Start the server and listen for requests."""
        logging.info(f"Starting server on {self.server_address[0]}:{self.server_address[1]}")
        self.httpd.serve_forever()

    def stop(self):
        """Stop the server."""
        logging.info("Stopping server...")
        self.httpd.shutdown()
        self.httpd.server_close()
        logging.info("Server stopped.")


class QuietRequestHandler(http.server.SimpleHTTPRequestHandler):
    """A custom request handler that suppresses logging for GET requests."""
    
    def log_message(self, format, *args):
        """Override to suppress logging of GET requests to console."""
        message = format % args
        logging.info("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          message.translate(self._control_char_table)))
    # https://en.wikipedia.org/wiki/List_of_Unicode_characters#Control_codes
    _control_char_table = str.maketrans(
            {c: fr'\x{c:02x}' for c in itertools.chain(range(0x20), range(0x7f,0xa0))})

    # def do_GET(self):
    #     """Handle GET requests."""
    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/html')
    #     self.end_headers()
    #     self.wfile.write(b"Welcome to the OppBot HTML Server!")

    def do_POST(self):
        """Handle POST requests."""
        self.send_response(501)  # Not Implemented
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"POST method not implemented.")

if __name__ == "__main__":

    # Create an instance of the OppBotHTMLServer
    server = OppBotHttpServer()
    logging.info("Starting OppBot HTML server...")
    server.start()
    waiting = input("Press Enter to stop the server...")
    server.stop()
    logging.info("OppBot HTML server has been stopped.")
    logging.info("Server stopped.")
