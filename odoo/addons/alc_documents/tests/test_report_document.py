# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64encode

from odoo import fields

from .common import TestAlcDocuments


class TestAlcDocumentsFlow(TestAlcDocuments):
    def test_sale_order_flow(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        self.assertFalse(self.alc_document_model.search(domain_documents))
        document = self.alc_document_model.search(domain_documents)
        # given
        vals_sale_order = self._get_vals_sale_order()
        sale_channel = self.env["sale.channel"].create({"name": "Test Channel"})
        vals_sale_order["sale_channel_id"] = sale_channel.id

        # when
        sale_order = self.so_model_no_delay.create(vals_sale_order)
        sale_order.action_confirm()
        attachment = sale_order.env["ir.attachment"].create(
            {
                "type": "binary",
                "res_model": sale_order._name,
                "res_id": sale_order.id,
                "name": "test.pdf",
                "mimetype": "application/pdf",
                "datas": b64encode(b"data"),
            }
        )

        # then
        document = self.alc_document_model.search(domain_documents) - document
        self.assertEqual(document.res_model, "sale.order")
        self.assertEqual(document.sale_channel_id, sale_channel)
        self.assertEqual(document.format, "pdf")
        self.assertEqual(document.partner_id, self.partner)
        self.assertEqual(document.document_date.date(), fields.Date.today())

        self.assertEqual(self.partner.alc_document_count, 1)

        attachment.unlink()
        self.assertFalse(self.partner.alc_document_count)
