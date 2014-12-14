# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com> 
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Plained Bill of Materials",
    "version" : "1.0",
    "author" : "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category" : "Manufacturing",
    "description" : """
    Puts a new view on products and BoMs to see the BoM structure plained: all
    materials are seen at the same level, and get summarized them if there is
    more than one entry of that product.
    """,
    "website" : "www.serviciosbaeza.com",
    "license" : "AGPL-3",
    "depends" : [
        "mrp",
    ],
    "demo" : [],
    "data" : [
        'mrp_bom_view.xml',
        'report/mrp_plained_bom_report.xml',
    ],
    "installable" : True,
    "active" : False,
}
