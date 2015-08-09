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
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Antiun Ingeniería S.L.',
    'website': 'http://www.serviciosbaeza.com',
    'depends': ['project'],
    'data': [
        'security/project_security.xml',
        'view/project_work_view.xml',
        'view/project_task_type_view.xml',
    ],
    'installable': True,
}
