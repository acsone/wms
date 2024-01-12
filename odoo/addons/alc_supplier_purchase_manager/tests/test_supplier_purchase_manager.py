# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestSupplierPurchaseManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_user = cls.env.ref("base.user_demo")
        cls.partner = cls.env.ref("base.res_partner_4")

    def test_00(self):
        """No purchase_manager."""
        po_form = Form(self.env["purchase.order"])
        self.assertEqual(po_form.user_id, self.env.user)
        po_form.partner_id = self.partner
        self.assertEqual(po_form.user_id, self.env.user)

    def test_01(self):
        """Purchase_manager set."""
        self.partner.purchase_manager_id = self.other_user
        po_form = Form(self.env["purchase.order"])
        self.assertEqual(po_form.user_id, self.env.user)
        po_form.partner_id = self.partner
        self.assertEqual(po_form.user_id, self.other_user)

    def test_02(self):
        """Purchase_manager set when create is called."""
        self.partner.purchase_manager_id = self.other_user
        po = self.env["purchase.order"].create({"partner_id": self.partner.id})
        self.assertEqual(po.user_id, self.other_user)

    def test_03(self):
        """Purchase_manager set, even when set to False on create."""
        self.partner.purchase_manager_id = self.other_user
        purchase = self.env["purchase.order"].create(
            {"partner_id": self.partner.id, "user_id": False}
        )
        self.assertEqual(purchase.user_id, self.other_user)
