# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from openerp.tests import common
from openerp import fields
from datetime import timedelta, datetime


class TestProjectTimesheetTimeControl(common.TransactionCase):
    def setUp(self):
        super(TestProjectTimesheetTimeControl, self).setUp()
        self.project = self.env['project.project'].create(
            {'name': 'Test project'})
        self.analytic_account = self.project.analytic_account_id
        self.task = self.env['project.task'].create({
            'name': 'Test task',
            'project_id': self.project.id,
        })

    def test_onchange_account_id(self):
        record = self.env['account.analytic.line'].new()
        record.account_id = self.analytic_account.id
        action = record.onchange_account_id()
        self.assertTrue(action['domain']['task_id'])

    def test_onchange_task_id(self):
        record = self.env['account.analytic.line'].new()
        record.task_id = self.task.id
        record.onchange_task_id()
        self.assertEqual(record.account_id, self.analytic_account)

    def test_create_write_analytic_line(self):
        line = self.env['account.analytic.line'].create({
            'date_time': fields.Datetime.now(),
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })
        self.assertEqual(line.date, fields.Date.today())
        line.date_time = '2016-03-23 18:27:00'
        self.assertEqual(line.date, '2016-03-23')

    def test_button_end_work(self):
        date_time = fields.Datetime.to_string(
            datetime.now() - timedelta(hours=1))
        line = self.env['account.analytic.line'].create({
            'date_time': date_time,
            'account_id': self.analytic_account.id,
            'name': 'Test line',
        })
        line.button_end_work()
        self.assertTrue(line.unit_amount)
