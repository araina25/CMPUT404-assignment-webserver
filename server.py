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


#MyWebserver is a class containing methods relating to handling HTTP and handles and implements all the requirements in requirement.org
class MyWebServer(socketserver.BaseRequestHandler):
    
    #This is the abosulte path to the webserver(The servers root directory)
    Initialised_Directory = os.path.abspath('./www')


    #The main function in which all the functions are called into when a new HTTP request is recieved 
    def handle(self):
        #Reading data from the Request 
        self.data = self.request.recv(1024).strip().decode('utf-8')#Limiting to 1024 bytes
        print(f"Got a request of: {self.data}\n")

        #Return a status code of "405 Method Not Allowed" for any method you cannot handle (POST/PUT/DELETE) 
        if not self.GetRequest():
            self.SendResponse(405, "Method Not Allowed")
            return

        
        host_path = self.TranslatePath()
        
        if not self.ValidPath(host_path):
            self.SendResponse(404, "Not Found")
            return

        self.ServerPath(host_path)

    def TranslatePath(self):
        path = self.data.splitlines()[0].split(' ')[1]
        return os.path.abspath(os.path.join(self.Initialised_Directory, path.lstrip('/')))
    
    def GetRequest(self):
        return self.data.splitlines()[0].split(' ')[0] == 'GET'

    
    def ServerPath(self, path):
        if os.path.isdir(path):
            self.ServerDirectory(path)
        else:
            self.ServerFile(path)
    
    def ValidPath(self, path):
        return path.startswith(self.Initialised_Directory)

    def ServerFile(self, path):
        mtype, _ = mimetypes.guess_type(path)

        if os.path.exists(path) and os.path.isfile(path):
            with open(path, 'r') as file:
                content = file.read()
            self.SendResponse(200, "OK", content, mtype)
        else:
            self.SendResponse(404, "Not Found")


    def ServerDirectory(self, path):
        if not self.data.splitlines()[0].split(' ')[1].endswith('/'):
            self.SendResponse(301, "Moved Permanently", location=self.data.splitlines()[0].split(' ')[1] + '/')
            return
        self.ServerFile(os.path.join(path, 'index.html'))

    def SendResponse(self, status_code, status_message, content="", content_type="text/html", location=None):
        response = [
            f"HTTP/1.1 {status_code} {status_message}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}"
        ]
        if location:
            response.append(f"Location: {location}")
        response.append("\r\n")
        response = "\r\n".join(response) + content
        self.request.sendall(response.encode('utf-8'))



        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
