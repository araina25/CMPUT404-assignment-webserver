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

        #Translating the local URL to a -- local file/directory path
        host_path = self.TranslatePath()
        

        if not self.ValidPath(host_path):#Verifying if the path is under the servers root directory 
            self.SendResponse(404, "Not Found")
            return
        
        self.ServerPath(host_path)

    #Translate Path is a function that will extract the path from the HTTP request generated.
    def TranslatePath(self):
        extracted_path = self.data.splitlines()[0].split(' ')[1]
        return os.path.abspath(os.path.join(self.Initialised_Directory, extracted_path.lstrip('/')))
    #pass
    
    #This funciton will check if it is a GET request  
    def GetRequest(self):
        return self.data.splitlines()[0].split(' ')[0] == 'GET'
    #pass

    #This will check if the path is a file or a directory 
    def ServerPath(self, system_path):
        if os.path.isdir(system_path):
            self.ServerDirectory(system_path)
        else:
            self.ServerFile(system_path)
    #pass
    
    #This function checks if if is a valid path or not -- which is checking if the path is within the servers root directory.
    def ValidPath(self, system_path):
        return system_path.startswith(self.Initialised_Directory)
    
    #pass

    #This function will serve a requested file
    def ServerFile(self, system_path):
        mtype, _ = mimetypes.guess_type(system_path)#Guessing the mime type for the file

        #Checking if the path exists or not and also is a file , then sending back and reading the file.
        if os.path.exists(system_path) and os.path.isfile(system_path):
            with open(system_path, 'r') as file:
                content = file.read()
            self.SendResponse(200, "OK", content, mtype)
        else:
            self.SendResponse(404, "Not Found")
    
    #pass


    #This function will serve a requested directory 
    def ServerDirectory(self, system_path):
        #Supporting the requirement that -- 
        #Must use 301 to correct paths such as http://127.0.0.1:8080/deep to http://127.0.0.1:8080/deep/ (path ending)
        if not self.data.splitlines()[0].split(' ')[1].endswith('/'):
            self.SendResponse(301, "Moved Permanently", h_redirection=self.data.splitlines()[0].split(' ')[1] + '/')#locating the Header value for redirection
            return
        #Trying to serve the index.html file from the directory.
        self.ServerFile(os.path.join(system_path, 'index.html'))
        #pass

    #This function is resposible for giving back a HTTP response.
    def SendResponse(self, status_code, status_message, content="", content_type="text/html", h_redirection=None):
        #A list comprising of all HTTP response headers and content
        response = [
            f"HTTP/1.1 {status_code} {status_message}",
            f"Content-Type: {content_type}",
            f"Content-Length: {len(content)}"
        ]
        if h_redirection:
            response.append(f"h_redirection: {h_redirection}")
        response.append("\r\n")
        response = "\r\n".join(response) + content
        self.request.sendall(response.encode('utf-8'))
        #pass



        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
