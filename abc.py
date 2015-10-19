# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LasComp
                                 A QGIS plugin
 asd
                              -------------------
        begin                : 2015-10-13
        git sha              : $Format:%H$
        copyright            : (C) 2015 by vivek
        email                : vjadon@asu.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from abc_dialog import LasCompDialog
import os.path
from PyQt4.QtGui import QFileDialog
import subprocess
import os

class LasComp:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LasComp_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LasCompDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&abc')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LasComp')
        self.toolbar.setObjectName(u'LasComp')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_output_file)

        #------------------------------Compress pushbutton-------------------------------

        #self.dlg.lineEdit.clear()
        self.dlg.compress.clicked.connect(self.laszipcmdline)


        #=--------------------------------lasview
        self.dlg.lasview.clicked.connect(self.lasviewcmdline)

        #=--------------------------------las2dem
        self.dlg.las2dem.clicked.connect(self.las2demcmdline)


        #--------------------------------show all las file button
        self.dlg.lasall.clicked.connect(self.listlasfiles)


        #--------------------------------show all asc file button
        self.dlg.ascall.clicked.connect(self.listascfiles)

        #--------------------------------asc 2 shape file convert button
        self.dlg.asc2shp.clicked.connect(self.asc2shpcmdline)




    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LasComp', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LasComp/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Las Compress'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&abc'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #---------------------select input button

    def select_output_file(self):
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Select Input Directory","")
        self.dlg.lineEdit.setText(dirname)




    #------------------compress button
    def laszipcmdline(self):
        name = []
        name = self.readfileforzip()
        for k in name:
            output1 = subprocess.check_output(k, shell=True)

        output2 = "las2laz conversion DONE!"
        self.dlg.outprint.setText(output2)

        # print subprocess.Popen("echo Hello World", shell=True, stdout=subprocess.PIPE).stdout.read()


    #----------------------lasview button
    def lasviewcmdline(self):
        name = []
        name = self.readfileforview()
        for k in name:
            output1 = subprocess.check_output(k, shell=True)
        output4 = "lasview DONE!"
        # print output
        self.dlg.outprint.setText(output4)

    #----------------------las2dem button
    def las2demcmdline(self):
        name = []
        name = self.readfileforlas2dem()
        for k in name:
            output1 = subprocess.check_output(k, shell=True)
        output6 = "las2dem DONE!"
        # print output
        self.dlg.outprint.setText(output6)



    def listlasfiles(self):
        nameofdir = self.dlg.lineEdit.text()
        filearr = []
        self.dlg.listoffiles.clear()
        for file in os.listdir(nameofdir):
            if file.endswith(".las"):
                filearr.append(file)
        self.dlg.listoffiles.addItems(filearr)



    def listascfiles(self):
        nameofdir = self.dlg.lineEdit.text()
        filearr = []
        self.dlg.listoffiles.clear()
        for file in os.listdir(nameofdir):
            if file.endswith(".asc"):
                filearr.append(file)
        self.dlg.listoffiles.addItems(filearr)

        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        for i in nameoffile:
            layer = self.iface.addRasterLayer("/home/sumeet/" + i , i)
        if not layer:
            output =  "Layer failed to load!"
            self.dlg.outprint.setText(output)


    #=---------------asc 2 shape file convert function
    def asc2shpcmdline(self):
        nameofdir = self.dlg.lineEdit.text()
        filearr = []
        self.dlg.listoffiles.clear()
        for file in os.listdir(nameofdir):
            if file.endswith(".tif"):
                filearr.append(file)

        temp = []
        for m in range(filearr.__len__()):
            abc = filearr[m]
            abc = abc[:-4]
            temp.append(abc)

        filecmd = []

        for i in temp:
            filecmd.append(('gdaltindex ' + str(i) + '.shp ' + str(i) + '.tif'))


        for k in filecmd:
            output1 = subprocess.check_output(k, shell=True)
        output = "shapefiles generated! "
        self.dlg.outprint.setText(output)

        filearrnew = []
        self.dlg.listoffiles.clear()
        for file in os.listdir(nameofdir):
            if file.endswith(".shp"):
                filearrnew.append(file)
        self.dlg.listoffiles.addItems(filearrnew)

        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        for i in nameoffile:
            layer = self.iface.addVectorLayer("/home/sumeet/" + i , i, "ogr")
        if not layer:
            output =  "Layer failed to load!"
            self.dlg.outprint.setText(output)




       #-----------------input functions for command line
    def readfileforview(self):
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        filecmd = []
        j =0
        for i in nameoffile:
            filecmd.append('./lasview.exe -i' + ' "' + i + '"')
            j = j+1
        return filecmd

    def readfileforlas2dem(self):
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        filecmd = []
        j =0
        for i in nameoffile:
            filecmd.append('./las2dem.exe -i' + ' "' + i + '" -elevation -oasc')
            j = j+1
        return filecmd

    def readfileforzip(self):
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        filecmd = []
        j =0
        for i in nameoffile:
            filecmd.append('./laszip.exe -i' + ' "' + i + '" -olaz')
            j = j+1
        return filecmd

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        layers = self.iface.legendInterface().layers()
        self.dlg.comboBox.clear()

        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)

        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
