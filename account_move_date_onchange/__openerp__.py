# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza Romero <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Change period on account moves when changing date',
    'version': '1.0',
    'category': 'Custom modifications',
    'description': """
Automatic period change
=======================

This module adds an onchange over date field on account moves screen that
changes period to the corresponding one, avoiding to commit errors due to
forgetfulness.
    """,
    'author': 'Serv. Tecnológ. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
}
