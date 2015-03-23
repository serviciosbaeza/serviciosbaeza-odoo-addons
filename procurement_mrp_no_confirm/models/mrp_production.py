# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp.osv import orm, fields


class MrpProduction(orm.Model):
    _inherit = 'mrp.production'

    _columns = {
        'no_confirm': fields.boolean('No confirm'),
    }
