# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import TestAlcDocuments


class TestAlcDocumentsFlow(TestAlcDocuments):
    def test_sale_order_flow(self):
        domain_documents = self.alc_document_model.get_partner_domain(self.partner)
        self.assertFalse(self.alc_document_model.search(domain_documents))

        # given
        vals_sale_order = self._get_vals_sale_order()
        sale_channel = "phone"
        vals_sale_order["sale_channel"] = sale_channel

        # when
        sale_order = self.so_model_no_delay.create(vals_sale_order)
        sale_order.action_confirm()
        sale_order.create_reports()

        # then
        document = self.alc_document_model.search(domain_documents)
        self.assertEqual(document.res_model, "sale.order")
        self.assertEqual(document.sale_channel, sale_channel)
        self.assertEqual(document.format, "pdf")
        self.assertEqual(document.partner_id, self.partner)

        self.assertEqual(self.partner.alc_document_count, 1)
