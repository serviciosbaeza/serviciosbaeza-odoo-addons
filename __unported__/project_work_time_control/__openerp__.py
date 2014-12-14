# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'Project task works time control',
    'version': '1.0',
    'category': 'Project management',
    'complexity': "easy",
    'description': """
Adds a button at task work level to compute minutes lasted from start date to
the current moment.
    """,
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com',
    'depends': ['project'],
    'data': [
        'view/project_work_view.xml',
    ],
    'installable': True,
}
