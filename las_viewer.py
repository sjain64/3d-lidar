# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LasViewer
                                 A QGIS plugin
 This plugin helps in visualizing selected SHP file present in Layers panel.
                              -------------------
        begin                : 2015-10-30
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
from las_viewer_dialog import LasViewerDialog
from PyQt4.QtGui import QFileDialog
import os.path
import subprocess
import qgis
import ctypes


class LasViewer():
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
            'LasViewer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LasViewerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Las Viewer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LasViewer')
        self.toolbar.setObjectName(u'LasViewer')

        # Author : Sumeet Jain
        # Button to ask user to select the directory in which lasview is stored
        self.dlg.lasviewDir.clear()
        self.dlg.lasviewDirButton.clicked.connect(self.select_lastool_file)

        # Author : Sumeet Jain
        # Button to start operation
        self.dlg.OkButton.clicked.connect(self.ok_button)

    # Author : Sumeet Jain
    # Selecting the lasview directory
    def select_lastool_file(self):
        dirname = QFileDialog.getExistingDirectory(self.dlg, "Select the directory in which lasview.exe is stored","")
        self.dlg.lasviewDir.setText(dirname)

    # Author : Sumeet Jain
    # Main Process of the button - Visualization of the file selected in the QGIS legend
    def ok_button(self):
        lasviewDir = self.dlg.lasviewDir.text()
        layer = self.iface.activeLayer()
        layerpath = layer.source()
        name_las = layerpath
        name_las =name_las[:-4]
        name_las = ''.join((name_las, '.laz'))
        os.chdir(lasviewDir)
        output1 = subprocess.check_output('lasview.exe -i' + ' "' + name_las + '"', shell=True)
        # self.dlg.statusBox.appendPlainText(str(layerpath))
        self.dlg.close()
        qgis.utils.reloadPlugin('LasViewer')





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
        return QCoreApplication.translate('LasViewer', message)


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

        icon_path = ':/plugins/LasViewer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Las Viewer'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Las Viewer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


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

