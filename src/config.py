"""
    LIC - Instruction Book Creation software
    Copyright (C) 2010 Remi Gagne
    Copyright (C) 2015 Jeremy Czajkowski

    This file (config.py) is part of LIC.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
   
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
   
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *


# Path to LDraw, L3P and PovRay.  These are set by user through PathsDialog below.
# Contents below are just some brain-dead default settings for a very first run of LIC. 
if sys.platform.startswith('win'):
    LDrawPath = ""
    L3PPath = ""
    POVRayPath = ""
else:
    root = os.path.expanduser('~')
    LDrawPath = os.path.join(root, 'LDraw')
    L3PPath = os.path.join(LDrawPath, 'Apps', 'L3p')
    POVRayPath = os.path.join(root, 'Applications', 'POV-Ray')

class PathsDialog(QDialog):

    def __init__(self, parent, hideCancelButton=False):
        QDialog.__init__(self, parent, Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(self.tr("Localizations of tools"))
        self.setFixedWidth(400)

        ldrawLabel, self.ldrawEdit, ldrawButton = self.makeLabelEditButton("L&Draw:", LDrawPath, self.browseForLDraw)
        l3pLabel, self.l3pEdit, l3pButton = self.makeLabelEditButton("&L3P:", L3PPath, self.browseForL3P)
        povLabel, self.povEdit, povButton = self.makeLabelEditButton("&POV-Ray:", POVRayPath, self.browseForPOV)

        buttons = QDialogButtonBox.Ok if hideCancelButton else QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttonBox = QDialogButtonBox(buttons, Qt.Horizontal)
        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), lambda: QDialog.reject(self))

        grid = QGridLayout()
        grid.addWidget(ldrawLabel, 0, 0)
        grid.addWidget(self.ldrawEdit, 0, 1)
        grid.addWidget(ldrawButton, 0, 2)
        grid.addWidget(l3pLabel, 1, 0)
        grid.addWidget(self.l3pEdit, 1, 1)
        grid.addWidget(l3pButton, 1, 2)
        grid.addWidget(povLabel, 2, 0)
        grid.addWidget(self.povEdit, 2, 1)
        grid.addWidget(povButton, 2, 2)
        grid.addWidget(buttonBox, 4, 1, 1, 2)
        self.setLayout(grid)

    def makeLabelEditButton(self, text, path, slot):
        edit = QLineEdit(path)
        button = QPushButton(self.tr("Browse..."))
        label = QLabel(self.tr(text))
        label.setBuddy(button)
        edit.setFixedWidth(200)
        self.connect(button, SIGNAL("clicked()"), slot)
        return label, edit, button

    def browseForLDraw(self):
        self.browse("Path to LDraw library", LDrawPath, self.ldrawEdit, self.validateLDrawPath, False)

    def browseForL3P(self):
        self.browse("Path to L3P", L3PPath, self.l3pEdit, self.validateL3PPath)

    def browseForPOV(self):
        self.browse("Path to POV-Ray", POVRayPath, self.povEdit, self.validatePOVPath)

    def validateLDrawPath(self, path):
        p1 = os.path.normcase( os.path.join(path, "PARTS") )
        p2 = os.path.normcase( os.path.join(path, "P") )
        if not (os.path.isdir(p1) and os.path.isdir(p2)):
            return "LDraw path must contain 'PARTS' and 'P' folders"
        return ""

    def validateL3PPath(self, path):
        return self.validate(path, "l3p")

    def validatePOVPath(self, path):
        return self.validate(path, "pvengine")

    @staticmethod
    def validate(path, prefix):
        normpath = os.path.normcase(path)
        surfix = ".exe" if os.name == 'nt' else ""  
        if not os.path.isfile(normpath) or not os.path.basename(normpath).startswith(prefix):
            return "Path must contain executable file with pattern %s*%s" % (prefix,surfix) 
        return ""        

    def browse(self, title, defaultPath, target, validator, singleFile=True):
        if singleFile:
            path = str(QFileDialog.getOpenFileName(self, title, defaultPath, "Executable (*.exe)" if os.name=="nt" else ""))
        else:
            path = str(QFileDialog.getExistingDirectory(None, title, defaultPath, QFileDialog.ShowDirsOnly))
        
        if path != "":
            valid = validator(path)
            if valid != "":
                QMessageBox.warning(self, "Invalid path", valid)
            else:
                target.setText(os.path.normcase(path))

    def accept(self):
        res = self.validateLDrawPath(str(self.ldrawEdit.text()))
        if res:
            QMessageBox.warning(self, "Invalid path", res)
        else:
            global LDrawPath, L3PPath, POVRayPath
            LDrawPath = str(self.ldrawEdit.text())
            L3PPath = str(self.l3pEdit.text())
            POVRayPath = str(self.povEdit.text())
            QDialog.accept(self)

filename = ""  # Set when a file is loaded

# SET to True L3PAccessLog | POVAccessLog in configuration file; If you have know what this tool is doing for you
writeL3PActivity = False
writePOVRayActivity = False

def checkPath(pathName, root=None):
    root = root if root else modelCachePath()
    path = os.path.join(root, pathName)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path

def appDataPath():
    if os.name == 'nt':
        return os.path.join(os.environ["APPDATA"], "licreator")
    else:
        return os.getcwd()

def rootCachePath():
    return checkPath('cache', appDataPath())

def modelCachePath():
    return checkPath(os.path.basename(filename), rootCachePath())

def finalImageCachePath():
    return checkPath('Final_Images')

def glImageCachePath():
    return checkPath('GL_Images')

def partsCachePath():
    return checkPath('parts', rootCachePath())

def litCachePath():
    return checkPath('templates', rootCachePath())

def datCachePath():
    return checkPath('DATs')

def povCachePath():
    return checkPath('POVs')

def pngCachePath():
    return checkPath('PNGs')

def pdfCachePath():
    return checkPath('PDFs')
