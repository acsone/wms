# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestSupplierPurchaseManager(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_user = cls.env.ref("base.user_demo")
        cls.partner = cls.env.ref("base.res_partner_4")
        cls.manager = cls.env["res.users"].create(
            {"name": "Purchase Manager", "login": "pmanager"}
        )

    def test_00(self):
        """No purchase_manager."""
        po_form = Form(self.env["purchase.order"])
        self.assertFalse(po_form.purchase_manager_id)
        self.assertEqual(po_form.user_id, self.env.user)
        po_form.partner_id = self.partner
        self.assertFalse(po_form.purchase_manager_id)

    def test_01(self):
        """Purchase_manager set."""
        self.partner.purchase_manager_id = self.manager
        po_form = Form(self.env["purchase.order"])
        self.assertEqual(po_form.user_id, self.env.user)
        po_form.partner_id = self.partner
        self.assertEqual(po_form.purchase_manager_id, self.manager)
