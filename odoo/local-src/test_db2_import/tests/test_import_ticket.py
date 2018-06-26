# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo.addons.db2_import.converter.ticket import DB2MapperHelpdeskTicket


from .common import DB2ImportTestCase


STAGE_WIP = 'helpdesk.stage_in_progress'
STAGE_SOLVED = 'helpdesk.stage_solved'


REASON_DEFECT = 'specific_helpdesk.product_defect'
REASON_MISSING = 'specific_helpdesk.missing_quantity'
REASON_EXTRA = 'specific_helpdesk.non_ordered_product'


class TestImportTicket(DB2ImportTestCase):

    _table = 'db2_hisprb'
    _suite_col = 'hpbsui'
    _problem_code_col = 'hpbcpb'

    def setUp(self):
        super(TestImportTicket, self).setUp()
        self.table_name = 'HISPRB'
        self.importer_table_ticket = self.env.ref(
            'db2_import.db2_table_hisprb_for_ticket'
        )

    @classmethod
    def get_row_from_suite(cls, suite, code):
        cr = cls.env.cr
        query = "SELECT id FROM %s WHERE %s = %%s AND %s = '%%s'" % (
            cls._table, cls._suite_col, cls._problem_code_col)
        cr.execute(query, (suite, code))
        res = cr.fetchone()
        if res:
            return res[0]
        return None

    def test_import_multiple_ticket_for_1_po(self):
        suite = 109686
        purchase = self.env['purchase.order'].create({
            'name': str(suite),
            'partner_id': self.env.ref('__import__.supplier_66200').id,
            'date_order': '2018-01-01',
            'date_planned': '2018-01-01',
            })

        code = 102
        db2_id = self.get_row_from_suite(suite, code)
        descr_qty = u"2"
        descr_comment = u"note de crédit reçue n° 090023"
        descr_inv_num = u"72127864"

        ticket = DB2MapperHelpdeskTicket.process(
            self.importer_table_ticket, self.table_name, db2_id)

        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.name, '109686-240-102')
        self.assertFalse(ticket.user_id)
        self.assertEqual(
            ticket.team_id, self.env.ref('specific_helpdesk.supplier_team'))
        self.assertEqual(ticket.active, True)
        self.assertEqual(ticket.purchase_order_id, purchase)
        self.assertEqual(ticket.partner_id, purchase.partner_id)
        self.assertTrue(ticket.description.startswith("[MIGRATION]"))
        self.assertTrue(descr_qty in ticket.description)
        self.assertTrue(descr_comment in ticket.description)
        self.assertTrue(descr_inv_num in ticket.description)
        self.assertEqual(ticket.stage_id, self.env.ref(STAGE_SOLVED))
        self.assertEqual(
            ticket.helpdesk_ticket_reason_id, self.env.ref(REASON_DEFECT))
        self.assertEqual(
            ticket.product_id, self.env.ref('__import__.product_7196443'))

        code = 104
        db2_id = self.get_row_from_suite(suite, code)
        descr_qty = u"162"
        descr_inv_num = u"72127864"

        ticket = DB2MapperHelpdeskTicket.process(
            self.importer_table_ticket, self.table_name, db2_id)

        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.name, '109686-300-104')
        self.assertFalse(ticket.user_id)
        self.assertEqual(
            ticket.team_id, self.env.ref('specific_helpdesk.supplier_team'))
        self.assertEqual(ticket.active, True)
        self.assertEqual(ticket.purchase_order_id, purchase)
        self.assertEqual(ticket.partner_id, purchase.partner_id)
        self.assertTrue(ticket.description.startswith("[MIGRATION]"))
        self.assertTrue(descr_qty in ticket.description)
        self.assertTrue(descr_inv_num in ticket.description)
        self.assertEqual(ticket.stage_id, self.env.ref(STAGE_SOLVED))
        self.assertEqual(
            ticket.helpdesk_ticket_reason_id, self.env.ref(REASON_MISSING))
        self.assertEqual(
            ticket.product_id, self.env.ref('__import__.product_7196644'))

        code = 110
        db2_id = self.get_row_from_suite(suite, code)
        descr_qty = u"12,000"
        descr_comment = u"ARTICLE NON COMM ACCEPT RESERV"

        ticket = DB2MapperHelpdeskTicket.process(
            self.importer_table_ticket, self.table_name, db2_id)
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.name, '109686-560-110')
        self.assertFalse(ticket.user_id)
        self.assertEqual(
            ticket.team_id, self.env.ref('specific_helpdesk.supplier_team'))
        self.assertEqual(ticket.active, True)
        self.assertEqual(ticket.purchase_order_id, purchase)
        self.assertEqual(ticket.partner_id, purchase.partner_id)
        self.assertTrue(ticket.description.startswith("[MIGRATION]"))
        self.assertTrue(descr_qty in ticket.description)
        self.assertTrue(descr_comment in ticket.description)
        self.assertEqual(ticket.stage_id, self.env.ref(STAGE_WIP))
        self.assertEqual(
            ticket.helpdesk_ticket_reason_id, self.env.ref(REASON_EXTRA))
        self.assertEqual(
            ticket.product_id, self.env.ref('__import__.product_5810993'))
