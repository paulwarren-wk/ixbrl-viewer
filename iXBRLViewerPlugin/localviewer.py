from arelle.LocalViewer import LocalViewer
from arelle.webserver.bottle import static_file
from arelle.FileSource import archiveFilenameParts
import os
import logging
import os, zipfile, sys, traceback

from .iXBRLViewer import IXBRLViewerBuilder

VIEWER_SUFFIX = ".ixbrlview"

class iXBRLViewerLocalViewer(LocalViewer):
    # plugin-specific local file handler
    def getLocalFile(self, file=None, relpath=None):
        _report, _sep, _file = file.partition("/")
        if file == 'ixbrlviewer.js':
            return static_file('ixbrlviewer.js', os.path.abspath(os.path.join(os.path.dirname(__file__), "viewer", "dist")))
        elif _report.isnumeric(): # in reportsFolder folder
            # check if file is in the current or parent directory (may bve
            _fileDir = self.reportsFolders[int(_report)]
            _fileExists = False
            if os.path.exists(os.path.join(_fileDir, _file + VIEWER_SUFFIX)):
                _file = _file + VIEWER_SUFFIX
                _fileExists
            elif os.path.exists(os.path.join(_fileDir, _file)):
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

def launchLocalViewer(cntlr, modelXbrl):
    from arelle import LocalViewer
    try:
        viewerBuilder = IXBRLViewerBuilder(cntlr.modelManager.modelXbrl)
        iv = viewerBuilder.createViewer(scriptUrl="/ixbrlviewer.js")
        # first check if source file was in an archive (e.g., taxonomy package)
        _archiveFilenameParts = archiveFilenameParts(modelXbrl.modelDocument.filepath)
        if _archiveFilenameParts is not None:
            outDir = os.path.dirname(_archiveFilenameParts[0]) # it's a zip or package
        else: 
            outDir = modelXbrl.modelDocument.filepathdir
        out = modelXbrl.modelDocument.basename + VIEWER_SUFFIX
        iv.save(os.path.join(outDir, out))
        _localhost = localViewer.init(cntlr, outDir)
        import webbrowser
        webbrowser.open(url="{}/{}".format(_localhost, modelXbrl.modelDocument.basename))
    except Exception as ex:
        modelXbrl.error("viewer:exception",
                        "Exception %(exception)s \sTraceback %(traceback)s",
                        modelObject=modelXbrl, exception=ex, traceback=traceback.format_tb(sys.exc_info()[2]))
