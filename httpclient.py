#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # get the header then break it down further to get the code
        # (second element in the header)
        code = data.split("\r\n\r\n")[0].split()[1]
        code = int(code)
        return code

    def get_headers(self, data):
        # header is first element
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        # body is second element 
        body = data.split("\r\n\r\n")[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        # parse url to get the scheme, host, and port
        urlParsed = urllib.parse.urlparse(url)
        scheme = urlParsed.scheme
        host = urlParsed.hostname
        port = urlParsed.port
        
        # check if there's currently a port and what the scheme is and assign the appropriate port
        if (port == None) and (scheme == "https"):
            port = 443
        elif (port == None) and (scheme == "http"):
            port = 80
        
        self.connect(host, port)

        # send the request
        self.sendall(f'GET {url} HTTP/1.1\r\nHost: {host}\r\nConnection: Closed\r\n\r\n')

        # receive the data and extract the code and body
        dataReceived = self.recvall(self.socket)

        code = self.get_code(dataReceived)
        body = self.get_body(dataReceived)
        
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        urlParsed = urllib.parse.urlparse(url)
        scheme = urlParsed.scheme
        host = urlParsed.hostname
        port = urlParsed.port
        
        # check if there's currently a port and what the scheme is and assign the appropriate port
        if (port == None) and (scheme == "https"):
            port = 443
        elif (port == None) and (scheme == "http"):
            port = 80

        self.connect(host, port)

        # initialize content to empty incase there are no arguments
        content = ""
        
        # check if there are actually arguments
        if args != None:
            # if there are arguments then append the key-value pairs to content
            for keys, values in args.items():
                content += f'{keys}={values}&'
        contentLength = len(content)

        # construct and send the request
        request = f"POST {url} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {contentLength}\r\nConnection: Closed\r\n\r\n{content}"
        self.sendall(request)

        # receive the data and extract the code and body
        dataReceived = self.recvall(self.socket)
        code = self.get_code(dataReceived)
        body = self.get_body(dataReceived)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
