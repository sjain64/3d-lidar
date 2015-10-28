# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LidarProcessor
                                 A QGIS plugin
 This plugin is used to Process Lidar files. Compression, Visualization and tile indexing can be done.
                              -------------------
        begin                : 2015-10-21
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Tuple Coders
        email                : tuplecoders@gmail.com
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
from lidar_processor_dialog import LidarProcessorDialog
import os.path
from PyQt4.QtGui import QFileDialog
import subprocess
import os


class LidarProcessor:
    """QGIS Plugin Implementation."""

    # Author : Vivek Jadon and Sumeet Jain
    # This function is used to call corresponding functions on button click event
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
            'LidarProcessor_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LidarProcessorDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LiDAR Processor')

        self.toolbar = self.iface.addToolBar(u'LidarProcessor')
        self.toolbar.setObjectName(u'LidarProcessor')

        # Button Calls

        # Select Input Button
        self.dlg.inputDir.clear()
        self.dlg.inputDirButton.clicked.connect(self.select_input_file)

        # Select Output Button
        self.dlg.outputDir.clear()
        self.dlg.outputDirButton.clicked.connect(self.select_output_file)

        # Start Processing Button
        self.dlg.startProc.clicked.connect(self.proc_start)

        # To make the Status box uneditable by the user
        self.dlg.statusBox.setReadOnly(True)





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
        return QCoreApplication.translate('LidarProcessor', message)


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

        icon_path = ':/plugins/LidarProcessor/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'LiDAR Operations'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&LiDAR Processor'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar




    # Author : Vivek Jadon
    # Enable users to select the input Directory---
    def select_input_file(self):
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Select Input Directory","")
        self.dlg.inputDir.setText(dirname)
        self.listalllasfiles()

    # Author : Vivek Jadon
    # Enable users to select the input Directory---
    def select_output_file(self):
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Select Output Directory","")
        self.dlg.outputDir.setText(dirname)

    # Author : Sumeet Jain
    #list all files in the listoffiles combobox
    def listalllasfiles(self):
        nameofdir = self.dlg.inputDir.text()
        filearr = []
        self.dlg.listoffiles.clear()
        for file in os.listdir(nameofdir):
            if file.endswith(".las"):
                filearr.append(file)
        self.dlg.listoffiles.addItems(filearr)

    # Author : Sumeet Jain
    # This func is called when Start Processing Button is pressed. It is used to perform the selected lidar operations
    def proc_start(self):

        if self.dlg.compress.isChecked():
            self.lascompress()
        if self.dlg.visualize.isChecked():
            self.lasview()
        if self.dlg.demGen.isChecked():
            self.las2dem()
        if self.dlg.shpGen.isChecked():
            self.tif2shp()
        if self.dlg.loadLayer.isChecked():
            self.loadlayer()


    # Author : Vivek Jadon
    # This is prefromed if COMPRESS checkbox is checked. It is reponsible for Compression of Lidar Files
    def lascompress(self):
        count = 0
        self.dlg.statusBox.appendPlainText("COMPRESSION")
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        if self.dlg.selectedFile.isChecked():
            fname = str(self.dlg.listoffiles.currentText())
            command = './laszip.exe -i' + ' "'  + nameofinputdir + "/"  + fname + '" -odir "' + nameofoutputdir + '" -olaz'
            output1 = subprocess.check_output(command, shell=True)
            compratio = self.compressratio(nameofinputdir, nameofoutputdir, fname)
            self.dlg.statusBox.appendPlainText('Compressed ' + fname + '\n with Compression Ratio = ' +  str(compratio))
            count = 1
        else:
            name = []
            name = self.readfileforzip()
            for k in name:
                output1 = subprocess.check_output(k, shell=True)
                count = count +1
            self.displayoutput()
        output2 = "Compression process complete for " + str(count) + " files. \n"
        self.dlg.statusBox.appendPlainText(output2)

    # Author : Sumeet Jain
    # This function updates status after completion of Compression process
    def displayoutput(self):
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        for i in nameoffile:
            compratio = self.compressratio(nameofinputdir, nameofoutputdir, i)
            self.dlg.statusBox.appendPlainText('Compressed ' + i + ' with Compression Ratio = ' +  str(compratio))

    # Author : Vivek Jadon
    # This function prepares compression commands
    def readfileforzip(self):
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        filecmd = []
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        for i in nameoffile:
            filecmd.append('./laszip.exe -i' + ' "' + nameofinputdir + "/" + i + '" -odir "' + nameofoutputdir + '" -olaz')
        return filecmd

    # Author : Sumeet Jain
    # This function returns the compression ratio for each file compressed
    def compressratio(self, ipdir, opdir, ipfilename):
        fnamewoext = ipfilename
        fnamewoext = fnamewoext[:-1]
        ratio = (float(os.path.getsize(ipdir + '/' + ipfilename))/(float(os.path.getsize(opdir + '/' + fnamewoext + 'z'))))
        return "{:.2f}".format(ratio)


    # Author : Sumeet Jain
    # This is prefromed if VIEW checkbox is checked. It is reponsible for Visualization of  Lidar  Files
    def lasview(self):
        count = 0
        nameofdir = self.dlg.inputDir.text()
        self.dlg.statusBox.appendPlainText("VISUALIZATION")
        if self.dlg.selectedFile.isChecked():
            fname = str(self.dlg.listoffiles.currentText())
            command = './lasview.exe -i' + ' "' + nameofdir + "/"  + fname + '"'
            output1 = subprocess.check_output(command, shell=True)
            self.dlg.statusBox.appendPlainText('Viewing ' + fname + '...')
            count = 1
        else:
            name = []
            name = self.readfileforview()
            for k in name:
                output1 = subprocess.check_output(k, shell=True)
                count = count + 1

        output2 = "Visualization process complete for " + str(count) + " files \n"
        self.dlg.statusBox.appendPlainText(output2)

    # Author : Vivek Jadon
    # This function prepares commands for visualization of LAS files
    def readfileforview(self):
        nameofdir = self.dlg.inputDir.text()
        filecmd = []
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]
        j =0
        for i in nameoffile:
            filecmd.append('./lasview.exe -i' + ' "'  + nameofdir + "/" + i + '"')
            self.dlg.statusBox.appendPlainText('Viewing ' + i + '  ...')
            j = j+1
        return filecmd

    # Author : Vivek Jadon
    # It is reponsible for Conversion of  Lidar  Files to DEM files
    def las2dem(self):
        count = 0
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        self.dlg.statusBox.appendPlainText("DEM GENERATION")
        if self.dlg.selectedFile.isChecked():
            fname = str(self.dlg.listoffiles.currentText())
            cmdasc = './las2dem.exe -i' + ' "' + nameofinputdir + "/" + fname + '" -elevation -odir "' + nameofoutputdir + '" -oasc'
            output1 = subprocess.check_output(cmdasc, shell=True)
            cmdtif = './las2dem.exe -i' + ' "' + nameofinputdir + "/" + fname + '" -elevation -odir "' + nameofoutputdir + '" -otif'
            output2 = subprocess.check_output(cmdtif, shell=True)
            self.dlg.statusBox.appendPlainText('Generated DEM file for ' + fname + '...')
            count = 2

        else:
            name = []
            name = self.readfilefordem()
            for k in name:
                output1 = subprocess.check_output(k, shell=True)
                count = count + 1

        output2 = "DEM file generation process complete for " + str(count/2) + " files. \n"
        self.dlg.statusBox.appendPlainText(output2)

    # Author : Sumeet Jain
    # This function prepares commands for LAS to DEM conversion
    def readfilefordem(self):
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        filecmd = []
        nameoffile = [self.dlg.listoffiles.itemText(i) for i in  range (self.dlg.listoffiles.count())]

        nrows = self.dlg.nrows.text()
        ncols = self.dlg.ncols.text()

        if nrows == "" and ncols == "":
            for i in nameoffile:
                filecmd.append('./las2dem.exe -i' + ' "' + nameofinputdir + "/" + i + '" -elevation -odir "' + nameofoutputdir + '" -oasc')
                filecmd.append('./las2dem.exe -i' + ' "' + nameofinputdir + "/" + i + '" -elevation -odir "' + nameofoutputdir + '" -otif')
                self.dlg.statusBox.appendPlainText('Generated DEM file for ' + i)
        else:
            j =0
            for i in nameoffile:
                filecmd.append('./las2dem.exe -i' + ' "' + nameofinputdir + "/" + i + '" -elevation -ncols ' + str(ncols) + ' -nrows ' +  str(nrows) + ' -odir "' + nameofoutputdir + '" -oasc')
                filecmd.append('./las2dem.exe -i' + ' "' + nameofinputdir + "/" + i + '" -elevation -ncols ' + str(ncols) + ' -nrows ' +  str(nrows) + ' -odir "' + nameofoutputdir + '" -otif')
                self.dlg.statusBox.appendPlainText('Generated DEM file for ' + i + ' with Dimensions \n No of Rows: ' + str(nrows) + ' No of cols: ' + str(ncols))
                j = j+1
        return filecmd

    # Author : Vivek Jadon
    # This function prepares commands to convert TIFF files to SHP files.
    def tif2shp(self):
        count = 0
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        self.dlg.statusBox.appendPlainText("SHP GENERATION")
        if self.dlg.selectedFile.isChecked():
            fname = str(self.dlg.listoffiles.currentText())
            fnamewoext = fname
            fnamewoext = fnamewoext[:-4]
            output1 = subprocess.check_output(('gdaltindex ' + nameofoutputdir + "/" + fnamewoext + '.shp ' + nameofinputdir + "/" + fnamewoext + '.tif'), shell=True)
            self.dlg.statusBox.appendPlainText('Generated SHP file for ' + fname + '...')
            count = 1
        else:
            name = []
            name = self.readfileforshp()
            for k in name:
                output1 = subprocess.check_output(k, shell=True)
                count = count + 1

        output2 = "SHP file generation process complete for " + str(count) + " files. \n"
        self.dlg.statusBox.appendPlainText(output2)

    # Author : Sumeet Jain
    # This function is used for conversion of conversion of multiple TIFF files to SHP files
    def readfileforshp(self):
        nameofinputdir = self.dlg.inputDir.text()
        nameofoutputdir = self.dlg.outputDir.text()
        filearr = []

        for file in os.listdir(nameofoutputdir):
            if file.endswith(".tif"):
                filearr.append(file)

        temp = []
        for m in range(filearr.__len__()):
            fnamewoext = filearr[m]
            fnamewoext = fnamewoext[:-4]
            temp.append(fnamewoext)

        filecmd = []

        for i in temp:
            filecmd.append(('gdaltindex ' + nameofoutputdir + "/" + i + '.shp ' + nameofoutputdir + "/" + i + '.tif'))
            self.dlg.statusBox.appendPlainText('Generated DEM file for ' + i + '  ...')
        return filecmd

    # Author : Sumeet Jain and Vivek Jadon
    # This function is used to load SHP and ASC files in Layers panel of QGIS
    def loadlayer(self):
        nameofoutputdir = self.dlg.outputDir.text()
        self.dlg.statusBox.appendPlainText('Loading asc files..')
        filearrasc = []
        for file in os.listdir(nameofoutputdir):
            if file.endswith(".asc"):
                filearrasc.append(file)

        for i in filearrasc:
            layer = self.iface.addRasterLayer(nameofoutputdir + "/" +i , i)
            self.dlg.statusBox.appendPlainText(i + ' file loaded')
        if not layer:
            output =  "Layer failed to load!"
            self.dlg.statusBox.appendPlainText(output)


        self.dlg.statusBox.appendPlainText('\nLoading shp files..')
        filearrshp = []
        for file in os.listdir(nameofoutputdir):
            if file.endswith(".shp"):
                filearrshp.append(file)

        for i in filearrshp:
            layer = self.iface.addVectorLayer(nameofoutputdir + "/" +i, i, "ogr")
            self.dlg.statusBox.appendPlainText(i + ' file loaded')

        if not layer:
            output =  "Layer failed to load!"
            self.dlg.statusBox.appendPlainText(output)



    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
