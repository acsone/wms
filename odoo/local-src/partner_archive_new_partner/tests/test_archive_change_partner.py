# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from mock import MagicMock, patch
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartner, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner1 = cls.env["res.partner"].create({"name": "Partner1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Partner2"})

        cls.saleorder = MagicMock()
        cls.invoice = MagicMock()
        cls.delivery = MagicMock()

    def setUp(self):
        super(TestPartner, self).setUp()

        self.sale_model = self.registry.models.get("sale.order")
        self.registry.models["sale.order"] = MagicMock()
        self.invoice_model = self.registry.models.get("account.invoice")
        self.registry.models["account.invoice"] = MagicMock()
        self.picking_model = self.registry.models.get("stock.picking")
        self.registry.models["stock.picking"] = MagicMock()

    def tearDown(self):
        super(TestPartner, self).setUp()

        if self.sale_model:
            self.registry["sale.order"] = self.sale_model
        else:
            del self.registry.models["sale.order"]
        if self.invoice_model:
            self.registry["account.invoice"] = self.invoice_model
        else:
            del self.registry.models["account.invoice"]
        if self.picking_model:
            self.registry["stock.picking"] = self.picking_model
        else:
            del self.registry.models["stock.picking"]

    def test_writing_sale_order_partner(self):
        self.partner1.active = True
        wizard_data = self.partner1.archive_partner()
        self.saleorder.partner_id = self.partner1
        self.env["sale.order"].search = MagicMock(
            return_value=[self.saleorder]
        )
        with patch.object(self.saleorder, 'write') as patched_so:
            context = wizard_data["context"]
            context["active_id"] = self.partner1.id
            self.env[wizard_data["res_model"]].with_context(context).create(
                {"new_partner_id": self.partner2.id}
            ).action_confirm()
            self.assertEqual(1, patched_so.call_count)

    def test_writing_invoice_partner(self):
        self.partner1.active = True
        wizard_data = self.partner1.archive_partner()
        self.invoice.partner_id = self.partner1
        self.env["account.invoice"].search = MagicMock(
            return_value=self.invoice
        )
        with patch.object(self.invoice, 'write') as patched_inv:
            context = wizard_data["context"]
            context["active_id"] = self.partner1.id
            self.env[wizard_data["res_model"]].with_context(context).create(
                {"new_partner_id": self.partner2.id}
            ).action_confirm()
            self.assertEqual(1, patched_inv.call_count)

    def test_writing_delivery_order_partner(self):
        self.partner1.active = True
        wizard_data = self.partner1.archive_partner()
        self.delivery.partner_id = self.partner1
        self.env["account.invoice"].search = MagicMock(
            return_value=self.delivery
        )
        with patch.object(self.delivery, 'write') as patched_picking:
            context = wizard_data["context"]
            context["active_id"] = self.partner1.id
            self.env[wizard_data["res_model"]].with_context(context).create(
                {"new_partner_id": self.partner2.id}
            ).action_confirm()
            self.assertEqual(1, patched_picking.call_count)
