#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Modified 2023 by Ryden Graham
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

# 404 error template, answered by linusg: https://stackoverflow.com/questions/41852380/how-to-abort-a-python-script-and-return-a-404-error
GENERIC_404_ERROR = b"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<html><head></head><body><h1>404 Not Found</h1></body></html>"
GENERIC_405_ERROR = b"HTTP/1.1 405 Not Supported\r\nContent-Type: text/html\r\n\r\n<html><head></head><body><h1>405 Method Not Supported</h1></body></html>"

class MyWebServer(socketserver.BaseRequestHandler):

    def createFoundHttpReturn(self, header, body):
        return b"HTTP/1.1 200 OK Found\r\n" + header + b"\r\n\r\n" + body

    def createRedirectReturn(self, header):
        return b"HTTP/1.1 301 Moved Permanently\r\n" + header + b"\r\n\r\n<html><head></head><body><h1>301 Moved Permanently</h1></body></html>"

    def handleRequest(self):
        path = self.path.strip()

        # offset into www folder
        absFilePath = "www" + path.decode("utf-8")

        # Check if file type is legal. We support HTML and CSS files only. We also support paths ending in /.
        if not absFilePath.endswith(("/", ".html", ".css")):

            # Add '/' here to check the folder
            absFilePath = absFilePath + "/"
            # Check if we need to redirect
            if not os.path.exists(absFilePath):
                return GENERIC_404_ERROR

            # Send redirect
            redirectHeader = b"Location: " + path + b"/\r\nContent-type: text/html"
            return self.createRedirectReturn(redirectHeader)

        #support paths ending in /
        if absFilePath.endswith("/"):
            absFilePath += "index.html"

        try:
            fh = open(absFilePath, 'r', encoding="utf-8")
            fileData = fh.read()
            fh.close()

            fileType, _ = mimetypes.guess_type(absFilePath)

            # Add content type header, answered by Vikas Ojha: https://stackoverflow.com/questions/32651362/how-do-i-set-the-content-type-for-post-requests-in-python-requests-library
            header = b"Content-type: " + fileType.encode("utf-8")

            response = self.createFoundHttpReturn(header, fileData.encode("utf-8"))

            return response
        except IOError:
            return GENERIC_404_ERROR
  
    def handle(self):
        self.data = self.request.recv(1024).strip()

        httpInfo = self.data.split()

        self.method = httpInfo[0]
        self.connectionInfo = httpInfo[6]
        
        if self.method.strip() == b"GET":
            self.path = httpInfo[1]

            fileData = self.handleRequest()

            self.request.sendall(fileData)
        else:
            # don't support other requesttypes
            self.request.sendall(GENERIC_405_ERROR)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
