# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2009 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
	"name" : "Common financial reports",
	"version" : "1.0",
	"author" : "Zikzakmedia SL",
	"website" : "www.zikzakmedia.com",
    "license" : "GPL-3",
	"depends" : ["account"],
	"category" : "Localisation/Accounting",
	"description": """
Add some common financial/accounting reports and some wizards to quickly compute them:
  * Account chart list
  * Invoice list
  * Account move (journal ledger)
  * Account move line
  * Account balance compared period-fiscal year
  * Cumulative general ledger

They can be found in the "Financial Management/Legal Statements/Generic Reports" menu or in the tree/form views of accounts, journals, invoices, account entries and account move lines.

Some reports are based on previous work by Pexego and others on the c2c_finance_report module for TinyERP 4.2 by Camptocamp SA.
201101 ported to v6 by Camptocamp Austria
""",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
                "wizard/wizard_account_balance_report_view.xml",
                "wizard/wizard_print_journal_entries_view.xml",
                "wizard/wizard_general_ledger_report_view.xml",
                'wizard/wizard_account_chart_view.xml',
                "wizard/wizard_invoice_list_report_view.xml",
		"account_report_report.xml",
		"account_report_wizard.xml",
                
	],
	"active": False,
	"installable": True
}
