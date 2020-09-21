# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time
from odoo.exceptions import UserError

from .common import AlcEdiConnectorCase


class TestUblOrderExporter(AlcEdiConnectorCase):
    @classmethod
    def setUpClass(cls):
        super(TestUblOrderExporter, cls).setUpClass()
        cls.draft_purchase_order = cls.purchase_order.copy()
        cls.ubl_order_exporter_task_def = cls.edi_backend._get_task(
            "ubl.order.exporter"
        )

    @freeze_time()
    def test_00(self):
        """
        Data:
            A supplier using the edi connector
            A purchase order that can sent via edi-UBL
        Test case:
            send the ubl document
        Expected result:
            the method to write on the ftp is called with the generated
            document,
            The sent file is saved as attachment
        """
        attachments = self._get_attachments(self.purchase_order)
        self.assertTrue(self.purchase_order.can_send_ubl_document)
        self.assertEqual(self.mocked_sftp_push.call_count, 0)
        self.purchase_order.send_ubl_order_document()
        self.assertEqual(self.mocked_sftp_push.call_count, 1)
        attachments = self._get_attachments(self.purchase_order) - attachments
        self.assertTrue(
            attachments.name,
            self.ubl_order_exporter_task_def.filename(self.purchase_order),
        )

    def test_01(self):
        """
        Data:
            A supplier not using the edi connector
            A purchase order approved
        Test case:
            can_send_ubl_document
            send the ubl document
        Expected result:
            can_send_ubl_document is False
            a UserError is sent
        """
        self.assertTrue(self.purchase_order.partner_id.use_edi_connector)
        self.assertTrue(self.purchase_order.state, "approved")
        self.assertTrue(self.purchase_order.can_send_ubl_document)
        self.purchase_order.partner_id.use_edi_connector = False
        self.assertFalse(self.purchase_order.can_send_ubl_document)
        with self.assertRaises(UserError):
            self.purchase_order.send_ubl_order_document()
        self.purchase_order.partner_id.use_edi_connector = True
        self.assertTrue(self.purchase_order.can_send_ubl_document)
        self.purchase_order.send_ubl_order_document()

    def test_02(self):
        """
        Data:
            A supplier using the edi connector
            A draft purchase
        Test case:
            can_send_ubl_document
            send the ubl document
        Expected result:
            can_send_ubl_document is False
            a UserError is sent
        """
        self.assertTrue(self.draft_purchase_order.partner_id.use_edi_connector)
        self.assertTrue(self.draft_purchase_order.state, "draft")
        self.assertFalse(self.draft_purchase_order.can_send_ubl_document)
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.draft_purchase_order.send_ubl_order_document()
        self.draft_purchase_order.button_approve()
        self.assertTrue(self.draft_purchase_order.can_send_ubl_document)
        self.draft_purchase_order.send_ubl_order_document()

    def test_03(self):
        """
        Data:
            A supplier using the edi connector
            An approved purchase
            The user does not have purchase manager permission
        Test case:
            can_send_ubl_document
            send the ubl document
        Expected result:
            can_send_ubl_document is False
            a UserError is sent
        """
        self.assertTrue(self.purchase_order.partner_id.use_edi_connector)
        group = self.group_edi_purchase_order_manager
        self.assertTrue(group)
        self.env.user.write({"groups_id": [(3, group.id, 0)]})
        self.assertFalse(self.purchase_order.can_send_ubl_document)
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.purchase_order.send_ubl_order_document()
