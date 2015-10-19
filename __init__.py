# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LasComp
                                 A QGIS plugin
 asd
                             -------------------
        begin                : 2015-10-13
        copyright            : (C) 2015 by vivek
        email                : vjadon@asu.edu
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LasComp class from file LasComp.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .abc import LasComp
    return LasComp(iface)
