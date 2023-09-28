#  coding: utf-8 
import socketserver
import os 
import http.server

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.request.sendall(bytearray("OK",'utf-8'))
        
        http_method, requested_path = self.parseHttp()

        if http_method and requested_path:
            # Step 2: Serve Static Files
            self.serveStatic(requested_path)

            # Step 3: Handle Redirects
            self.handleRedirect(requested_path)

            # Step 4: Handle Unsupported HTTP Methods
            self.handleUnsupportedMethod(http_method)

            # Close the connection when you're done
            self.closeConnection()
        else:
            # Handle malformed or incomplete requests
            self.send_error_response(400)  # Bad Request

    # ... (other class members and methods)

    #Parse the HTTP  request, from Client and extract the relavent information 
    """# Split the raw HTTP request into lines
    request_lines = self.data.decode('utf-8').split('\r\n')

    # The first line of the request contains the HTTP method and path
    first_line = request_lines[0].split()

    if len(first_line) == 3:
        # Extract the HTTP method, requested path, and HTTP version
        http_method, requested_path, http_version = first_line
        return http_method, requested_path

    # If the first line doesn't contain three elements, return None to indicate a malformed request
    return None, None"""
    def parseHttp(self):
        #Conerting the recived data from byte to UTF8 and spliting using the delimiter(\r\n)
        request_lines = self.data.decode('utf-8').split('\r\n')

        first_line = request_lines[0].split()#First line contains the HTTP path,method and version.

        if len(first_line) == 3:
        # Extract the HTTP method, requested path, and HTTP version
            http_method, requested_path, http_version = first_line
            return http_method, requested_path
        #Indicating a malformed request(First line dosent contain the required info)
        return None,None 
        
        #connection = http.client.HTTPConnection('www.python.org', 80, timeout=10)
        #pass

    '''import os

def serve_static_file(self, file_path):
    # Define the base directory where static files are stored (./www)
    base_directory = "./www"

    # Construct the full path to the requested file
    full_path = os.path.join(base_directory, file_path.lstrip("/"))

    # Check if the file exists
    if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
            # Read the content of the file
            with open(full_path, 'rb') as file:
                file_content = file.read()

            # Determine the MIME type based on the file extension
            file_extension = os.path.splitext(full_path)[1].lower()
            mime_type = "text/html" if file_extension == ".html" else "text/css" if file_extension == ".css" else "application/octet-stream"

            # Construct the HTTP response with a 200 OK status code
            response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(file_content)}\r\n\r\n".encode('utf-8') + file_content

            # Send the response to the client
            self.send_http_response(response)

        except Exception as e:
            # Handle any errors that may occur during file reading
            print(f"Error serving file: {e}")
            self.send_error_response(500)  # Internal Server Error
    else:
        # If the file does not exist, construct a 404 Not Found response
        self.send_error_response(404)  # Not Found
'''

    #Function checks for existing files (./WWW directory)
    def serveStatic(self,filePath):

        base_directory = "./www"#Creating a directory for static files stored with (./www)
        full_path = os.path.join(base_directory,filePath.lstrip("/"))
        # Check if the file exists

        #content = get_file('jenkins_analytics.html')
                #return Response(content, mimetype="text/html")


            #@app.route('/', defaults={'path': ''})
            #@app.route('/<path:path>')
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                # Read the content of the file
                with open(full_path, 'rb') as file:
                    file_content = file.read()

                # Determine the MIME type based on the file extension
                file_extension = os.path.splitext(full_path)[1].lower()
                mime_type = "text/html" if file_extension == ".html" else "text/css" if file_extension == ".css" else "application/octet-stream"

                # Construct the HTTP response with a 200 OK status code
                response = f"HTTP/1.1 200 OK\r\nContent-Type: {mime_type}\r\nContent-Length: {len(file_content)}\r\n\r\n".encode('utf-8') + file_content

                # Send the response to the client
                self.send_http_response(response)

            except Exception as e:
                # Handle any errors that may occur during file reading
                print(f"Error serving file: {e}")
                self.send_error_response(500)  # Internal Server Error
        else:
            # If the file does not exist, construct a 404 Not Found response
            self.send_error_response(404)  # Not Found

                                                    
        #pass

    #Construct a 301 -- Permanently Moved (Handles redirects)
    def handleRedirect(self, path):
         # Check if the requested path ends with a trailing slash
        if path.endswith("/"):
            # Construct the new path with the trailing slash removed
            new_path = path.rstrip("/")
            
            # Construct the HTTP response with a 301 Moved Permanently status code
            response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {new_path}/\r\n\r\n".encode('utf-8')

            # Send the response to the client
            self.send_http_response(response)
        #pass

    #To Handle unsupported HTTP methods -- 405 method not allowed
    def handleUnsupportedMethod(self, method):
        # Define a list of supported HTTP methods
        supported_methods = ["GET"]

        # Check if the provided method is in the list of supported methods
        if method not in supported_methods:
            # Construct the HTTP response with a 405 Method Not Allowed status code
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode('utf-8')

            # Send the response to the client
            self.send_http_response(response)
        #pass

    #Sends the constructed HTTP response to Client 
    def sendHttpResponse(self, response):
        try:
            # Send the HTTP response to the client
            self.request.sendall(response)
        except Exception as e:
            # Handle any errors that may occur during response sending
            print(f"Error sending HTTP response: {e}")
        #pass

    #Closes the connection to Client
    def closeConnection(self):
        try:
            # Close the connection to the client
            self.request.close()
        except Exception as e:
            # Handle any errors that may occur during the connection closing
            print(f"Error closing connection: {e}")
        #pass
    


        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
