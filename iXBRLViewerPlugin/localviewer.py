from arelle.LocalViewer import LocalViewer
from arelle.webserver.bottle import static_file
import os
import logging

class iXBRLViewerLocalViewer(LocalViewer):
    # plugin-specific local file handler
    def getLocalFile(self, file=None, relpath=None):
        _report, _sep, _file = file.partition("/")
        if _report.isnumeric(): # in reportsFolder folder
            # check if file is in the current or parent directory (may bve
            _fileDir = self.reportsFolders[int(_report)]
            _fileExists = False
            if os.path.exists(os.path.join(_fileDir, _file)):
                _fileExists = True
            else:
                if os.path.exists(os.path.join(os.path.dirname(_fileDir), _file)):
                    _fileDir = os.path.dirname(_fileDir)
                    _fileExists = True
            if not _fileExists:
                self.cntlr.addToLog("http://localhost:{}/{}".format(self.port,file), messageCode="localViewer:fileNotFound",level=logging.DEBUG)
            return static_file(_file, root=_fileDir,
                               # extra_headers modification to py-bottle
                               more_headers={'Cache-Control': 'no-cache, no-store, must-revalidate',
                                             'Pragma': 'no-cache',
                                             'Expires': '0'})
        return static_file(file, root="/") # probably can't get here unless path is wrong

localViewer = iXBRLViewerLocalViewer("iXBRL Viewer",  os.path.dirname(__file__))
