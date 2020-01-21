# Copyright 2019 Workiva Inc.
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

from .iXBRLViewer import IXBRLViewerBuilder
from .localviewer import launchLocalViewer

def iXBRLViewerCommandLineOptionExtender(parser, *args, **kwargs):
    parser.add_option("--save-viewer",
                      action="store",
                      dest="saveViewerFile",
                      help="Save an HTML viewer file for an iXBRL report. Specify either a filename or directory.")
    parser.add_option("--viewer-url",
                      action="store",
                      dest="viewerURL",
                      default="js/dist/ixbrlviewer.js",
                      help="Specify the URL to ixbrlviewer.js")


def iXBRLViewerCommandLineXbrlRun(cntlr, options, *args, **kwargs):
    # extend XBRL-loaded run processing for this option
    if cntlr.modelManager is None or cntlr.modelManager.modelXbrl is None:
        cntlr.addToLog("No taxonomy loaded.")
        return
    out = getattr(options, 'saveViewerFile', False)
    if out:
        viewerBuilder = IXBRLViewerBuilder(cntlr.modelManager.modelXbrl)
        iv = viewerBuilder.createViewer(scriptUrl=options.viewerURL)
        iv.save(out)


def iXBRLViewerMenuCommand(cntlr):
    from .ui import SaveViewerDialog
    if cntlr.modelManager is None or cntlr.modelManager.modelXbrl is None:
        cntlr.addToLog("No document loaded.")
        return
    dialog = SaveViewerDialog(cntlr)
    if dialog.accepted and dialog.filename():
        viewerBuilder = IXBRLViewerBuilder(cntlr.modelManager.modelXbrl)
        iv = viewerBuilder.createViewer(scriptUrl=dialog.scriptUrl())
        iv.save(dialog.filename())


def iXBRLViewerToolsMenuExtender(cntlr, menu, *args, **kwargs):
    # Extend menu with an item for the savedts plugin
    menu.add_command(label="Save iXBRL Viewer Instance",
                     underline=0,
                     command=lambda: iXBRLViewerMenuCommand(cntlr))


def toolsMenuExtender(cntlr, menu, *args, **kwargs):
    iXBRLViewerToolsMenuExtender(cntlr, menu, *args, **kwargs)


def commandLineOptionExtender(*args, **kwargs):
    iXBRLViewerCommandLineOptionExtender(*args, **kwargs)


def commandLineRun(*args, **kwargs):
    iXBRLViewerCommandLineXbrlRun(*args, **kwargs)

def viewMenuExtender(cntlr, viewMenu, *args, **kwargs):
    # persist menu selections for showing filing data and tables menu
    from tkinter import Menu, BooleanVar # must only import if GUI present (no tkinter on GUI-less servers)
    def setLaunchIXBRLViewer(self, *args):
        cntlr.config["LaunchIXBRLViewer"] = cntlr.launchIXBRLViewer.get()
        cntlr.saveConfig()
    erViewMenu = Menu(cntlr.menubar, tearoff=0)
    viewMenu.add_cascade(label=_("iXBRL Viewer"), menu=erViewMenu, underline=0)
    cntlr.launchIXBRLViewer = BooleanVar(value=cntlr.config.get("Launch iXBRL Viewer", True))
    cntlr.launchIXBRLViewer.trace("w", setLaunchIXBRLViewer)
    erViewMenu.add_checkbutton(label=_("Launch viewer on load"), underline=0, variable=cntlr.launchIXBRLViewer, onvalue=True, offvalue=False)

def guiRun(cntlr, modelXbrl, attach, *args, **kwargs):
    """ run iXBRL Viewer using GUI interactions for a single instance or testcases """
    if cntlr.hasGui and cntlr.launchIXBRLViewer.get():
        launchLocalViewer(cntlr, modelXbrl)

__pluginInfo__ = {
    'name': 'ixbrl-viewer',
    'version': '0.1',
    'description': "iXBRL Viewer creator",
    'license': 'License :: OSI Approved :: Apache License, Version 2.0 (Apache-2.0)',
    'author': 'Paul Warren',
    'copyright': 'Copyright :: Workiva Inc. :: 2019',
    'CntlrCmdLine.Options': commandLineOptionExtender,
    'CntlrCmdLine.Xbrl.Run': commandLineRun,
    'CntlrWinMain.Menu.Tools': toolsMenuExtender,
    'CntlrWinMain.Menu.View': viewMenuExtender,
    'CntlrWinMain.Xbrl.Loaded': guiRun,
}
