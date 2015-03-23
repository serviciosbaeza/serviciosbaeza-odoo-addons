# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "Procurement MRP no Confirm",
    "version": "1.0",
    "depends": ["mrp"],
    'author': 'Serv. Tecnolog. Avanzados - Pedro M. Baeza,'
              'Avanzosc,'
              'OdooMRP team',
    "category": "MRP",
    "description": """
Don't confirm automatically production orders when created from procurements
============================================================================

This module avoids the automatic confirmation of manufacturing order when
procurement orders are executed.

Credits
=======

Contributors
------------
* Ainara Galdona <agaldona@avanzosc.es>
* Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
* Ana Juaristi <ajuaristio@gmail.com>
    """,
    'data': ["data/mrp_production_workflow.xml"],
    'installable': True,
}
