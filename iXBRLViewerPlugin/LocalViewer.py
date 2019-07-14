"""
:mod:`EdgarRenderer.LocalViewer`
~~~~~~~~~~~~~~~~~~~
Edgar(tm) Renderer was created by staff of the U.S. Securities and Exchange Commission.
Data and content created by government employees within the scope of their employment 
are not subject to domestic copyright protection. 17 U.S.C. 105.
"""

from arelle.webserver.bottle import Bottle, static_file
import os, threading, time, logging, sys

port = None
reportsFolders = [os.path.dirname(__file__)] # 0 is root of include and ixviewer

def init(cntlr, reportsFolder): # returns browser root
    global port
    if port is None: # already initialized
    
        # find available port
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("",0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        #port = 8080 # test with fixed port
        
        def getlocalfile(file=None, relpath=None):
            cntlr.addToLog("http://localhost:{}/{}".format(port,file), messageCode="localViewer:get",level=logging.INFO)
            # print ("GET file={}".format(file))
            if not file and relpath:
                print("relpath=" + relpath)
            if file == 'favicon.ico':
                return static_file("arelle.ico", root=cntlr.imagesDir, mimetype='image/vnd.microsoft.icon')
            _report, _sep, _file = file.partition("/")
            if _report.isnumeric(): # in reportsFolder folder
                if _file == "ixbrlviewer.js":
                    root = os.path.join(os.path.dirname(__file__), "viewer", "dist")
                    return static_file(_file, root=root, mimetype='text/javascript')
                else:
                    root = reportsFolders[int(_report)]
                # print("file {} root {}".format(_file, root))
                # print (os.path.join(reportsFolders[int(_report)], _file))
                # is it an EDGAR workstation query parameter
                return static_file(_file, root=root,
                                   # extra_headers modification to py-bottle
                                   more_headers={'Cache-Control': 'no-cache, no-store, must-revalidate',
                                                 'Pragma': 'no-cache',
                                                 'Expires': '0'})
            return static_file(file, root="/") # probably can't get here unless path is wrong
        
        # start server
        localserver = Bottle()
        
        localserver.route('/<file:path>', 'GET', getlocalfile)
        localserver.route('<relpath:path>', 'GET', getlocalfile)
        # start local server on the port on a separate thread
        threading.Thread(target=localserver.run, 
                         # The wsgi server part of cherrypy was split into a new 'cheroot'
                         #kwargs=dict(server='cherrypy', host='localhost', port=port, quiet=True), 
                         kwargs=dict(server='cheroot', host='localhost', port=port, quiet=True), 
                         daemon=True).start()
        time.sleep(2) # allow other thread to run and start up

    localhost = "http://localhost:{}/{}".format(port, len(reportsFolders))
    reportsFolders.append(reportsFolder)
    cntlr.addToLog(_("http://localhost:{}").format(port), messageCode="localViewer:listen",level=logging.INFO)
    #print ("localhost={}".format(localhost))
    return localhost
