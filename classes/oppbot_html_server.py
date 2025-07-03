import http.server
import threading

class OppBotHtmlServer(threading.Thread):
    """A simple HTTP server for OppBot that serves HTML content.
    This server responds to GET requests with a welcome message and handles 
    POST requests with a not implemented error."""

    def __init__(self, host='0.0.0.0', port=8888):
        """Initialize the server with the specified host and port."""
        threading.Thread.__init__(self)
        self.server_address = (host, port)
        self.RequestHandler = http.server.SimpleHTTPRequestHandler
        self.httpd = http.server.HTTPServer(self.server_address, self.RequestHandler)

    def run(self):
        """Start the server and listen for requests."""
        print(f"Starting server on {self.server_address[0]}:{self.server_address[1]}")
        self.httpd.serve_forever()

    def stop(self):
        """Stop the server."""
        print("Stopping server...")
        self.httpd.shutdown()
        self.httpd.server_close()
        print("Server stopped.")


if __name__ == "__main__":

    # Create an instance of the OppBotHTMLServer
    server = OppBotHtmlServer()
    print("Starting OppBot HTML server...")
    server.start()
    waiting = input("Press Enter to stop the server...")
    server.stop()
    print("OppBot HTML server has been stopped.")
    print("Server stopped.")
