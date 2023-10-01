#  coding: utf-8 
import socketserver
import os 
import http.server
import mimetypes 
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
    
    BASE_DIR = os.path.abspath('./www')

    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print(f"Got a request of: {self.data}\n")

        if not self.is_get_request():
            self.send_response(405, "Method Not Allowed")
            return

        local_path = self.translate_path()
        
        if not self.valid_path(local_path):
            self.send_response(404, "Not Found")
            return

        self.serve_path(local_path)

    def is_get_request(self):
        return self.data.splitlines()[0].split(' ')[0] == 'GET'

    def translate_path(self):
        path = self.data.splitlines()[0].split(' ')[1]
        return os.path.abspath(os.path.join(self.BASE_DIR, path.lstrip('/')))

    def valid_path(self, path):
        return path.startswith(self.BASE_DIR)

    def serve_path(self, path):
        if os.path.isdir(path):
            self.serve_directory(path)
        else:
            self.serve_file(path)

    def serve_directory(self, path):
        if not self.data.splitlines()[0].split(' ')[1].endswith('/'):
            self.send_response(301, "Moved Permanently", location=self.data.splitlines()[0].split(' ')[1] + '/')
            return
        self.serve_file(os.path.join(path, 'index.html'))

    def serve_file(self, path):
        mime_type, _ = mimetypes.guess_type(path)
        try:
            with open(path, 'r') as file:
                content = file.read()
            self.send_response(200, "OK", content, mime_type)
        except FileNotFoundError:
            self.send_response(404, "Not Found")

    def send_response(self, status_code, status_message, content="", content_type="text/html", location=None):
        headers = [
            f"HTTP/1.1 {status_code} {status_message}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}"
        ]
        if location:
            headers.append(f"Location: {location}")
        headers.append("\r\n")
        response = "\r\n".join(headers) + content
        self.request.sendall(response.encode('utf-8'))



        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
