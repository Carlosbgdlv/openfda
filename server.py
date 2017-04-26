import socketserver
import web


##
# WEB SERVER
##

##
# WEB SERVER
##

PORT = 8000


#Handler = http.server.SimpleHTTPRequestHandler
Handler = web.testHTTPRequestHandler

socketserver.TCPServer.allow_rouse_address = True   #ctrl+c
httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
httpd.serve_forever()


#de array a string

#a=["1","2"]
#"," join(a)
