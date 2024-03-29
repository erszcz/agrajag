# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor.ui'
#
# Created: Fri Jul  4 17:58:40 2008
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(798,475)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setGeometry(QtCore.QRect(0,27,798,424))
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tileList = TileList(self.splitter)
        self.tileList.setMinimumSize(QtCore.QSize(150,0))
        self.tileList.setAcceptDrops(True)
        self.tileList.setDragEnabled(True)
        self.tileList.setIconSize(QtCore.QSize(60,60))
        self.tileList.setResizeMode(QtGui.QListView.Adjust)
        self.tileList.setSpacing(10)
        self.tileList.setViewMode(QtGui.QListView.IconMode)
        self.tileList.setObjectName("tileList")
        self.levelView = LevelView(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.levelView.sizePolicy().hasHeightForWidth())
        self.levelView.setSizePolicy(sizePolicy)
        self.levelView.setMinimumSize(QtCore.QSize(400,400))
        self.levelView.setMaximumSize(QtCore.QSize(820,16777215))
        self.levelView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.levelView.setObjectName("levelView")
        self.propEd = PropertyEditor(self.splitter)
        self.propEd.setObjectName("propEd")
        self.gridLayout.addWidget(self.splitter,0,0,1,1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,798,27))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setGeometry(QtCore.QRect(0,451,798,24))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionLoad = QtGui.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionAbout_Qt = QtGui.QAction(MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionSave_image = QtGui.QAction(MainWindow)
        self.actionSave_image.setObjectName("actionSave_image")
        self.actionNew_level = QtGui.QAction(MainWindow)
        self.actionNew_level.setObjectName("actionNew_level")
        self.actionSave_XML = QtGui.QAction(MainWindow)
        self.actionSave_XML.setObjectName("actionSave_XML")
        self.actionLoad_all = QtGui.QAction(MainWindow)
        self.actionLoad_all.setObjectName("actionLoad_all")
        self.actionFormation_toolbar = QtGui.QAction(MainWindow)
        self.actionFormation_toolbar.setObjectName("actionFormation_toolbar")
        self.menuFile.addAction(self.actionNew_level)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionLoad_all)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave_image)
        self.menuFile.addAction(self.actionSave_XML)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionExit,QtCore.SIGNAL("triggered()"),MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Agrajag Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "&Options", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("MainWindow", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad.setText(QtGui.QApplication.translate("MainWindow", "&Load...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_Qt.setText(QtGui.QApplication.translate("MainWindow", "About &Qt", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_image.setText(QtGui.QApplication.translate("MainWindow", "Save &image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionNew_level.setText(QtGui.QApplication.translate("MainWindow", "&New level...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_XML.setText(QtGui.QApplication.translate("MainWindow", "&Save XML", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_all.setText(QtGui.QApplication.translate("MainWindow", "Load &all", None, QtGui.QApplication.UnicodeUTF8))
        self.actionFormation_toolbar.setText(QtGui.QApplication.translate("MainWindow", "Formation toolbar", None, QtGui.QApplication.UnicodeUTF8))

from tilelist import TileList
from propertyeditor import PropertyEditor
from levelview import LevelView
