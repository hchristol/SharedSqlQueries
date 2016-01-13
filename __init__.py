# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SharedSqlQueries
                                 A QGIS plugin
 This plugin allows to share SQL customised queries (with keywords) written by a db manager and that can be used in a friendly interface by QGIS end users.
                             -------------------
        begin                : 2016-01-07
        copyright            : (C) 2016 by Ville de Clermont-Ferrand
        email                : hchristol@ville-clermont-ferrand.fr
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
    """Load SharedSqlQueries class from file SharedSqlQueries.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .shared_sqlqueries import SharedSqlQueries
    return SharedSqlQueries(iface)
