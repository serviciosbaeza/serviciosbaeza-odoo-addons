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
    "name" : "Allow searching on full category path",
    "version" : "1.0",
    "author" : "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "category" : "Sales Management",
    "description" : """
    This module allow to search text in the complete category path. For
    example, category *Can be sold* that is children of *All products*, has
    this full category path:
    
    *All products / Can be sold*
    
    Normal behaviour is that you can search this category typing any part of
    'Can be sold', but if you type any part of 'All products', you won't be
    able to select this category.
    
    This module changes this behaviour to get full results.
    """,
    "website" : "www.serviciosbaeza.com",
    "license" : "AGPL-3",
    "depends" : [
        "product",
    ],
    "demo" : [],
    "data" : [
    ],
    "installable" : True,
    "active" : False,
}
